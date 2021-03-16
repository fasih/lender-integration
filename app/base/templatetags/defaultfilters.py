import json

from django.template.defaultfilters import register



@register.filter
def to_python(value, key=None):
    try:
        data = eval(value)
    except:
        try:
            data = json.loads(value)
        except:
            try:
                data = json.loads(value.replace('""', '"'))
            except:
                data = {}
    if key and isinstance(data, dict):
        return data.get(key) or ""
    return data



@register.filter
def default_if_blank(value, default):
    if isinstance(value, str) and not len(value.strip()):
        return default
    if not len(value):
        return default
    return value



@register.filter
def calculate_emi(context):
    try:
        P = float(context.get('applied_amount'))
        n = float(context.get('loan_tenure'))
        r = float(context.get('int_rate_reducing_perc'))
    except ValueError:
        P = n = r = 0

    EMI = P * r * (1 + r)*n/((1 + r)*n - 1)
    return EMI
