import json

from django.template.defaultfilters import register



@register.filter
def to_python(value, key=None):
    try:
        data = json.loads(value)
    except:
        try:
            data = json.loads(value.replace('""', '"'))
        except:
            data = {}
    if key:
        return data.get(key) or ""
    return data

