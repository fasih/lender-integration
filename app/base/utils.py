import functools
import requests
import structlog as logging
import traceback

from django.template import Context, Template

logger = logging.getLogger(__name__)



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



def apply_task(task_s, apply_async, **kwargs):
    if apply_async:
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

    class Method:

        TIMEOUT = 15

        def __init__(self, method):
            self.method = method

        def send(self, *args, **kwargs):
            kwargs.update(timeout=self.TIMEOUT)
            logger.info('Request', args=args, kwargs=kwargs)

            try:
                response = self.method(*args, **kwargs)
                try:
                    response_data = response.json()
                except ValueError:
                    response_data = response.text
                logger.info('Response', args=args, kwargs=kwargs, data=response_data)
                return response
            except requests.exceptions.Timeout:
                logger.exception('Request', args=args, kwargs=kwargs, msg='requests.exceptions.Timeout')
            except Exception as e:
                logger.exception('Request', args=args, kwargs=kwargs, msg=str(e))

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
