import base64
import img2pdf
import json
import os
import shutil
import tempfile

from datetime import date, datetime
from dateutil import relativedelta
from furl import furl

from django.conf import settings
from django.template.defaultfilters import register

from services.pdf_compressor import compress



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

        P_default = params_dict[P_key] or 0
        N_default = params_dict[N_key] or 0
        R_default = params_dict[R_key] or 0

        P_value = context.get(P_key) and str(context.get(P_key)).strip()
        N_value = context.get(N_key) and str(context.get(N_key)).strip()
        R_value = context.get(R_key) and str(context.get(R_key)).strip()

        P = float(P_value or P_default)
        N = float(N_value or N_default)
        R = float(R_value or R_default)
    except:
        P = N = R = 0

    R = R/(12*100)
    EMI = (P*R*pow(1+R, N))/(pow(1+R,N)-1)
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

    pdf_ext = False
    no_ext = False

    for item in items:
        name = item.get(key)
        filename.append("{}/{}".format(settings.MEDIA_ROOT, item['filename']))
        _, ext = os.path.splitext(item['filename'])

        if ext.lower() == '.pdf':
            pdf_ext = True
        elif ext == '':
            no_ext = True

    if pdf_ext:
        final_filename = filename[0]
    elif no_ext:
        src_filename = filename[0]
        final_filename = f'{src_filename}.pdf'
        shutil.copy(src_filename, final_filename)
    else:
        final_filename = tempfile.NamedTemporaryFile(suffix='.pdf').name
        with open(final_filename, "wb") as f:
            f.write(img2pdf.convert(filename))
    try:
        compressed_filename = tempfile.NamedTemporaryFile(suffix='.pdf').name
        compress(final_filename, compressed_filename, power=3)
    except:
        compressed_filename = final_filename

    data = open(compressed_filename, "rb").read()
    encoded = base64.b64encode(data)
    base64_string = encoded.decode('utf-8')
    return base64_string



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
