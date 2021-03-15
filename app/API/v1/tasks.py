import structlog as logging

from celery.decorators import task

from base.utils import *
from borrowers.models import *
from lenders.models import *
from platforms.models import *



logger = logging.getLogger(__name__)



def fetch_from_lms(app):
    lms = app.lms
    lms_api = LoanManagementSystemAPI.objects.filter(lms=lms
                                        ).active().order_by('priority')
    context = {'loanId': app.lmsid}
    context.update(lms.__dict__)

    if lms.oauth_url:
        oauth_body = render_from_string(lms.oauth_body, context)
        try:
            response = Request.POST.send(lms.oauth_url, data=oauth_body,
                                            headers=lms.oauth_headers)
            oauth_data = response.json()
            lms.auth_token = oauth_data['access_token']
        except:
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

    for api in lms_api:
        url = render_from_string(f'{lms.base_url}{api.path}', context)
        request = getattr(Request, api.method)
        kwargs = dict(headers=headers)

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

        if api.auth_scheme:
            kwargs["headers"].update({"Authorization":
                                f"{api.auth_scheme} {lms.auth_token}"})

        response = request.send(url, **kwargs)
        data = LoanApplicationData(app=app, lms_api=api, request=kwargs,
                                    response=response.response_json,
                                    response_code=response.status_code)
        data.save()



def fetch_from_svc(app):
    pass



def push_to_lender(app):
    app_data = LoanApplicationData.objects.filter(app=app,
                        response_code__gte=200, response_code__lte=299
                    ).select_related('lms_api', 'svc_api').order_by('created')
    loan, _ = Loan.objects.get_or_create(app=app, lender=app.lender)

    context = {'loanId': app.lmsid, 'lms_api': {}, 'svc_api': {}}

    for each in app_data:
       if each.lms_api:
            context['lms_api'].update({each.lms_api.name: each.response})
       elif each.svc_api:
            context['svc_api'].update({each.svc_api.name: each.response})

    cp = app.cp
    lms = app.lms
    lender = app.lender

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

    for api in lender_api:
        url = render_from_string(f'{lender.base_url}{api.path}', context)
        request = getattr(Request, api.method)
        kwargs = dict(headers=headers)

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

        if api.auth_scheme:
            kwargs["headers"].update({"Authorization":
                                f"{api.auth_scheme} {lender.auth_token}"})

        response = request.send(url, **kwargs)
        data = LoanData(app=app, loan=loan, lender_api=api, request=kwargs,
                            response=response.response_json,
                            response_code=response.status_code)
        data.save()



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



