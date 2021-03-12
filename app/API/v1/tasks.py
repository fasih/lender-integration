import structlog as logging

from urllib.parse import urlencode
from celery.decorators import task

from base.utils import *
from borrowers.models import *
from platforms.models import *



logger = logging.getLogger(__name__)



def fetch_from_lms(app):
    lms = app.lms
    lms_api = LoanManagementSystemAPI.objects.filter(lms=lms).order_by('priority')
    context = {'loanId': app.lmsid}

    for api in lms_api:
        url = render_from_string(f'{lms.base_url}{api.path}', context)
        request = getattr(Request, api.method)
        kwargs = dict(headers={})

        if api.params:
            query_params = render_from_string(api.params, context)
            kwargs.update(params=query_params)

        if api.headers:
            headers = render_from_string(api.headers, context)
            kwargs["headers"].update(headers)

        if api.body:
            body = render_from_string(api.body, context)
            kwargs.update(json=body)

        if api.auth_scheme:
            kwargs["headers"].update({"Authorization":
                                f"{api.auth_scheme} {lms.api_key}"})

        response = request.send(url, **kwargs)
        data = LoanApplicationData(app=app, lms_api=api, request=kwargs,
                response=response.json(), response_code=response.status_code)
        data.save()



@task(name="loans_post")
def loans_post(application_id):
    logger.info('loans_post', status='Started', **locals())

    app = LoanApplication.objects.select_related('lms').get(pk=application_id)
    fetch_from_lms(app)

    logger.info('loans_post', status='Finished', **locals())



@task(name="loans_patch")
def loans_patch(application_id):
    logger.info('loans_patch', status='Started', **locals())

    app = LoanApplication.objects.select_related('lms').get(pk=application_id)
    fetch_from_lms(app)

    logger.info('loans_patch', status='Finished', **locals())



@task(name="loans_put")
def loans_put(application_id):
    logger.info('loans_put', status='Started', **locals())

    logger.info('loans_put', status='Finished', **locals())



