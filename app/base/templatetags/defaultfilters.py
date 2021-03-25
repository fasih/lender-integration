import base64
import img2pdf
import json
import os

from datetime import date, datetime
from dateutil import relativedelta
from furl import furl

from django.conf import settings
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
def calculate_emi(context, query_string):
    try:
        f = furl(f'?{query_string}')
        params_list = f.query.asdict()['params']
        params_dict = dict(params_list)

        P_key = params_list[0][0]
        N_key = params_list[1][0]
        R_key = params_list[2][0]

        P_value = params_dict[P_key] or 0
        N_value = params_dict[N_key] or 0
        R_value = params_dict[R_key] or 0

        P = float(context.get(P_key) or P_value)
        N = float(context.get(N_key) or N_value)
        R = float(context.get(R_key) or R_value)
    except:
        P = N = R = 0

    EMI = P * R * (1 + R)*N/((1 + R)*N - 1)
    return abs(EMI)



@register.filter
def calculate_delta(from_date, delta='months'):
    try:
        TODAY = date.today()
        delta_list = ['months', 'days']
        delta = delta if delta in delta_list else 'months'
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        relative_delta = relativedelta.relativedelta(TODAY, from_date)
        return getattr(relative_delta, delta)
    except:
        return '0'



@register.filter
def calculate_emi_date(disburse_date, cycle_date):
    try:
        EMI_CYCLE_DUE_DATE = int(cycle_date)
        disburse_date = datetime.strptime(disburse_date, '%Y-%m-%d')
    except:
        return ''
    if disburse_date.day >= EMI_CYCLE_DUE_DATE:
        emi_date = disburse_date + relativedelta.relativedelta(months=1)
    else:
        emi_date = disburse_date
    return emi_date.strftime(f'%Y-%m-{EMI_CYCLE_DUE_DATE}')



@register.filter
def generate_base64pdf(items, key):
    filename = []
    already_pdf = False
    for item in items:
        name = item.get(key)
        filename.append("{}/{}".format(settings.MEDIA_ROOT, item['filename']))
        _, ext = os.path.splitext(item['filename'])
        if ext.lower() == '.pdf':
            already_pdf = True

    if not already_pdf:
        final_filename = f"/tmp/{name}.pdf"
        with open(final_filename, "wb") as f:
            f.write(img2pdf.convert(filename))
    else:
        final_filename = filename[0]

    data = open(final_filename, "rb").read()
    encoded = base64.b64encode(data)
    return encoded



@register.filter
def force(item, value):
    return value



@register.filter
def default_today(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except:
        date_str = None
        TODAY = date.today()
    return date_str or TODAY.strftime('%Y-%m-%d')



@register.filter
def strip(string):
    data = str(string)
    return data.strip()
