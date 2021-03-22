import functools
import re
import requests
import structlog as logging
import traceback

from pathlib import Path
from django.template import Context, Template



logger = logging.getLogger(__name__)



def file_uploads(instance, filename):
    root = Path(instance._meta.db_table)
    lmsid = instance and instance.app and (instance.app.lmsid or instance.app.pk)
    return root / str(lmsid) / filename



def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition('.')
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)



sentinel = object()
def rgetattr(obj, attr, default=sentinel):
    if default is sentinel:
        _getattr = getattr
    else:
        def _getattr(obj, name):
            return getattr(obj, name, default)
    return functools.reduce(_getattr, [obj]+attr.split('.'))



def apply_task(task_s, sync=False, **kwargs):
    if not sync:
        task_ = task_s.apply_async(**kwargs)
        logger.info('Task', name=task_s.name, id=task_.id, action='Submitted')
        return task_
    else:
        task_ = task_s.apply()
        logger.info('Task', name=task_s.name, id='', action='Executed')
        if isinstance(task_.result, Exception):
            logger.exception('Task', name=task_s.name, id='', 
                action='Failed', traceback=traceback.format_exc())
            raise task_.result
        else:
            return task_.result



def flatten(object):
    for item in object:
        if isinstance(item, (list, tuple, set)):
            yield from flatten(item)
        else:
            yield item



class Request(object):

    class ErrorResponse:

        def __init__(self, exc):
            self.exc = exc

        def json(self):
            return {}

        def text(self):
            return ''

        @property
        def response_json(self):
            return {'exc': str(self.exc)}

    class Method:

        TIMEOUT = 50

        def __init__(self, method):
            self.method = method

        def send(self, *args, **kwargs):
            kwargs.update(timeout=self.TIMEOUT)
            logger.info('Request', args=args, kwargs=kwargs)

            try:
                response = self.method(*args, **kwargs)
                try:
                    response_data = response.json()
                    response_json = response_data
                except ValueError:
                    response_data = response.text
                    response_json = {'data': response_data}

                response.response_json = response_json
                logger.info('Response', args=args, kwargs=kwargs, data=response_data)

                return response

            except requests.exceptions.Timeout as e:
                logger.exception('Request', args=args, kwargs=kwargs, msg='requests.exceptions.Timeout')
            except Exception as e:
                logger.exception('Request', args=args, kwargs=kwargs, msg=str(e))

            return Response(e)


    GET = Method(requests.get)
    PUT = Method(requests.put)
    POST = Method(requests.post)
    PATCH = Method(requests.patch)
    DELETE = Method(requests.delete)



def render_from_string(template, context=None):
    string = repr(template)
    _context = Context(context or {})
    rendered_string = Template(string).render(_context)
    return eval(rendered_string)



def get_filename(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]
