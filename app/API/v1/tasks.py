import copy
import tempfile
import structlog as logging

from celery.decorators import task
from collections import defaultdict
from dictor import dictor
from django.core.files import File
from rest_framework import status
from urllib.parse import urlparse

from base.models import *
from base.utils import *
from borrowers.models import *
from lenders.models import *
from platforms.models import *

logger = logging.getLogger(__name__)



def fetch_from_lms(app):
    app_data = LoanApplicationData.objects.filter(is_success, app=app
                                    ).select_related('lms_api', 'svc_api'
                                    ).active().order_by('created')

    context = {'loanId': app.lmsid, 'lms_api': {}, 'svc_api': {}}

    for each in app_data:
       if each.lms_api:
            context['lms_api'].update({each.lms_api.name: each.response})
       elif each.svc_api:
            context['svc_api'].update({each.svc_api.name: each.response})

    lms = app.lms

    context.update(lms.__dict__)
    context.update(lms=lms)

    lms_api = LoanManagementSystemAPI.objects.filter(lms=lms
                                        ).active().order_by('priority')

    if lms.oauth_url:
        oauth_body = render_from_string(lms.oauth_body, context)
        try:
            response = Request.POST.send(lms.oauth_url, data=oauth_body,
                                            headers=lms.oauth_headers)
            oauth_data = response.json()
            lms.auth_token = oauth_data['access_token']
        except Exception as e:
            logger.exception('fetch_from_lms', status='Exited', **locals())
            return
    elif lms.api_key:
        lms.auth_token = lms.api_key
    else:
        lms.auth_token = None

    if lms.params:
        query_params = render_from_string(lms.params, context)
    else:
        query_params = {}

    if lms.headers:
        headers = render_from_string(lms.headers, context)
    else:
        headers = {}

    if lms.body:
        body = render_from_string(lms.body, context)
    else:
        body = {}

    continue_status = True
    previous_priority = None

    for api in lms_api:

        if continue_status or previous_priority == None:
            #init or continue the workflow
            previous_priority = api.priority
        else:
            #break the workflow
            break

        app_data = LoanApplicationData.objects.filter(is_success, app=app,
                                ).select_related('lms_api', 'svc_api'
                                ).active().order_by('created')

        already_called_non_idempotent_api = False
        for each in app_data:
            if each.lms_api == api and api.method == api.METHOD.POST:
                already_called_non_idempotent_api = True
                break
            if each.lms_api:
                context['lms_api'].update({each.lms_api.name: each.response})

        if already_called_non_idempotent_api:
            continue

        if api.iterable:
            iterable_data = dictor(context, api.iterable_data) or [{}]
            iterable_filter_keys = api.iterable_filters.keys()
            iterable_filter_data = defaultdict(list)

            for item in iterable_data:
                for k in iterable_filter_keys:
                    if item.get(k) in api.iterable_filters[k]:
                        key = item.get(k)
                        if isinstance(api.iterable_filters[k][key], list):
                            iterable_filter_data[key].append(item)
                        else:
                            iterable_filter_data[key] = item
            iterable_data_list = []
            for each in iterable_filter_data.values():
                if isinstance(each, list):
                    iterable_data_list.extend(each)
                else:
                    iterable_data_list.append(each)
        else:
            iterable_data_list = [{}]

        for each in iterable_data_list:
            if isinstance(each, dict):
                context.update(**each)
                iterable_context = each
            else:
                iterable_context = {}

            external_api = bool(urlparse(api.path).scheme)
            url_format = f'{api.path}' if external_api else f'{lms.base_url}{api.path}'
            url = render_from_string(url_format, context)
            request = getattr(Request, api.method)
            kwargs = dict(headers=headers)

            if api.auth_scheme:
                kwargs["headers"].update({"Authorization":
                                    f"{api.auth_scheme} {lms.auth_token}"})

            if api.params:
                api_query_params = render_from_string(api.params, context)
                query_params.update(**api_query_params)
                kwargs.update(params=query_params)

            if api.headers:
                api_headers = render_from_string(api.headers, context)
                headers.update(**api_headers)
                kwargs["headers"].update(headers)

            if api.body:
                api_body = render_from_string(api.body, context)
                if isinstance(api_body, dict):
                    body.update(**api_body)
                    kwargs.update(json=body)
                else:
                    kwargs.update(json=api_body)

            response = request.send(url, **kwargs)
            request_json = kwargs.copy()
            request_json.update(url=url)

            data = LoanApplicationData(app=app, lms_api=api,
                                        response_code=response.status_code)

            filename = get_filename(response.headers.get('content-disposition'))
            if filename:
                lf = tempfile.NamedTemporaryFile()
                for block in response.iter_content(1024 * 8):
                    if not block:
                        break
                    lf.write(block)
                data.response_file.save(filename, File(lf), save=False)
                data.response = {'headers': dict(response.headers),
                                 'filename': data.response_file.name}
            else:
                data.response = response.response_json

            if iterable_context:
                request_json.update(iterable_context=iterable_context)
            data.request = request_json

            data.save()
            continue_status = status.is_success(response.status_code)



def fetch_from_svc(app):
    pass



def push_to_lender(app):
    app_data = LoanApplicationData.objects.filter(is_success, app=app,
                                    ).select_related('lms_api', 'svc_api'
                                    ).active().order_by('created')
    loan, _ = Loan.objects.get_or_create(app=app, lender=app.lender)

    context = {'loanId': app.lmsid, 'lms_api': defaultdict(list),
                'svc_api': defaultdict(list), 'lender_api': defaultdict(list)}

    for each in app_data:
       if each.lms_api:
            if each.lms_api.iterable:
                iterable_response = each.response
                iterable_response.update(**each.request.get('iterable_context', {}))
                context['lms_api'][each.lms_api.name].append(iterable_response)
            else:
                context['lms_api'].update({each.lms_api.name: each.response})
       elif each.svc_api:
            if each.lms_api.iterable:
                iterable_response = each.response
                iterable_response.update(**each.request.get('iterable_context', {}))
                context['svc_api'][each.svc_api.name].append(iterable_response)
            else:
                context['svc_api'].update({each.svc_api.name: each.response})

    cp = app.cp
    lms = app.lms
    lender = app.lender

    context.update(lender.__dict__)
    context.update(lender=lender, lms=lms, cp=cp)

    lender_api = LenderSystemAPI.objects.filter(lender=lender
                                            ).active().order_by('priority')

    if lender.oauth_url:
        oauth_body = render_from_string(lender.oauth_body, context)
        try:
            response = Request.POST.send(lender.oauth_url, data=oauth_body,
                                            headers=lender.oauth_headers)
            oauth_data = response.json()
            lender.auth_token = oauth_data['access_token']
        except:
            return
    elif lender.api_key:
        lender.auth_token = lender.api_key
    else:
        lender.auth_token = None

    if lender.params:
        query_params = render_from_string(lender.params, context)
    else:
        query_params = {}

    if lender.headers:
        headers = render_from_string(lender.headers, context)
    else:
        headers = {}

    if lender.body:
        body = render_from_string(lender.body, context)
    else:
        body = {}

    continue_status = True
    previous_priority = None

    for api in lender_api:

        if continue_status or previous_priority == None:
            #init or continue the workflow
            previous_priority = api.priority
        else:
            #break the workflow
            break

        loan_data = LoanData.objects.filter(is_success, app=app,
                                        ).select_related('lender_api'
                                        ).active().order_by('created')

        already_called_non_idempotent_api = False
        for each in loan_data:
            if each.lender_api == api and api.method == api.METHOD.POST:
                already_called_non_idempotent_api = True
                break
            if each.lender_api:
                context['lender_api'].update({each.lender_api.name: each.response})

        if already_called_non_idempotent_api:
            continue

        if api.iterable:
            iterable_data = dictor(context, api.iterable_data) or [{}]
            iterable_filter_keys = api.iterable_filters.keys()
            iterable_filter_data = defaultdict(list)

            for item in iterable_data:
                for k in iterable_filter_keys:
                    if item.get(k) in api.iterable_filters[k]:
                        key = item.get(k)
                        item_config = api.iterable_filters[k][key]
                        item[k] = item_config['name']
                        item['compress'] = item_config.get('compress') or -1

                        if isinstance(item_config['type'], list):
                            iterable_filter_data[key].append(item)
                        else:
                            iterable_filter_data[key] = item

            iterable_data_list = []
            for each in iterable_filter_data.values():
                if isinstance(each, list):
                    _item = {'items': each}
                    _item.update(**each[0])
                else:
                    _item = {'items': [each]}
                    _item.update(**each)
                iterable_data_list.append(_item)
        else:
            iterable_data_list = [{}]

        for each in iterable_data_list:
            if isinstance(each, dict):
                context.update(**each)
                iterable_context = each
            else:
                iterable_context = {}

            external_api = bool(urlparse(api.path).scheme)
            url_format = f'{api.path}' if external_api else f'{lender.base_url}{api.path}'
            url = render_from_string(url_format, context)
            request = getattr(Request, api.method)
            kwargs = dict(headers=headers)

            if api.auth_scheme:
                kwargs["headers"].update({"Authorization":
                                    f"{api.auth_scheme} {lender.auth_token}"})

            if api.params:
                api_query_params = render_from_string(api.params, context)
                _query_params = copy.deepcopy(query_params)
                _query_params.update(**api_query_params)
                kwargs.update(params=_query_params)

            if api.headers:
                api_headers = render_from_string(api.headers, context)
                _headers = copy.deepcopy(headers)
                _headers.update(**api_headers)
                kwargs["headers"].update(_headers)

            if api.body:
                api_body = render_from_string(api.body, context)
                if isinstance(api_body, dict):
                    _body = copy.deepcopy(body)
                    _body.update(**api_body)
                    kwargs.update(json=_body)
                else:
                    kwargs.update(json=api_body)

            response = request.send(url, **kwargs)
            data = LoanData(app=app, loan=loan, lender_api=api, request=kwargs,
                                response=response.response_json,
                                response_code=response.status_code)
            data.save()
            continue_status = status.is_success(response.status_code)



@task(name="loans_post")
def loans_post(application_id):
    logger.info('loans_post', status='Started', **locals())

    app = LoanApplication.objects.select_related('cp', 'lms', 'lender'
                                    ).get(pk=application_id)
    fetch_from_lms(app)
    fetch_from_svc(app)
    push_to_lender(app)

    logger.info('loans_post', status='Finished', **locals())



@task(name="loans_patch")
def loans_patch(application_id):
    logger.info('loans_patch', status='Started', **locals())

    app = LoanApplication.objects.select_related('lms').get(pk=application_id)

    fetch_from_lms(app)
    fetch_from_svc(app)

    logger.info('loans_patch', status='Finished', **locals())



@task(name="loans_put")
def loans_put(application_id):
    logger.info('loans_put', status='Started', **locals())

    app = LoanApplication.objects.select_related('cp', 'lms', 'lender'
                                    ).get(pk=application_id)
    push_to_lender(app)

    logger.info('loans_put', status='Finished', **locals())



