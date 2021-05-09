import base64
import img2pdf
import json
import os
import numpy as np
import pandas as pd
import shutil
import structlog as logging
import tempfile

from datetime import date, datetime
from dateutil import relativedelta
from furl import furl
from fuzzywuzzy import fuzz

from django.conf import settings
from django.template.defaultfilters import register

from services.pdf_compressor import compress

logger = logging.getLogger(__name__)



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

    keys = key and key.split(',') or []
    response = []

    if isinstance(data, dict):
        for each in keys:
            response.append(data.get(each) or "")
        if len(response) == 1:
            return response[0]
        else:
            return response
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
    except Exception as e:
        logger.exception('calculate_emi', msg=str(e), local=locals())
        P = N = R = 0

    try:
        R = R/(12*100)
        EMI = (P*R*pow(1+R, N))/(pow(1+R,N)-1)
    except Exception as e:
        logger.exception('calculate_emi', msg=str(e), local=locals())
        EMI = 0
    return abs(EMI)



@register.filter
def calculate_delta(from_date, delta='M'):
    try:
        TODAY = datetime.today()
        delta_list = ['Y', 'M', 'D']
        delta = delta if delta in delta_list else delta_list[1]
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        df = pd.DataFrame([[from_date, TODAY]], columns=['from_date', 'to_date'])
        return int(round(((df['from_date'] - df['to_date'])/np.timedelta64(1, delta)).abs()))
    except Exception as e:
        logger.exception('calculate_delta', msg=str(e), local=locals())
        return 0



@register.filter
def calculate_emi_date(disburse_date, data_csv):
    try:
        data = data_csv.split(',')
        CYCLE_DATE = int(data[0])
        THERSHOLD_DATE = 32

        disburse_date = datetime.strptime(disburse_date, '%Y-%m-%d')

        if not (1 <= CYCLE_DATE <= 28):
            raise Exception(f'EMI cycle cannot be {CYCLE_DATE}')

        if len(data) == 2:
            try:
                threshold = int(data[1])
            except ValueError:
                threshold = 0
            if threshold > CYCLE_DATE:
                THERSHOLD_DATE = threshold
            else:
                logger.info('calculate_emi_date', local=locals(),
                                msg='Threshold date is invalid')

        if disburse_date.day >= THERSHOLD_DATE:
            months_delta = 2
        else:
            months_delta = 1

    except Exception as e:
        logger.exception('calculate_emi_date', msg=str(e), local=locals())
        return ''
    emi_date = disburse_date + relativedelta.relativedelta(months=months_delta)
    return emi_date.strftime(f'%Y-%m-{CYCLE_DATE}')



@register.filter
def generate_base64pdf(items, key):
    compress_level = -1
    file_list = []
    is_pdf = False

    for item in items:
        compress_level = item['compress']
        file_type = item.get(key)
        file_name = item['filename']
        _, ext = os.path.splitext(file_name)
        abs_file_path = "{}/{}".format(settings.MEDIA_ROOT, file_name)

        if ext.lower() == '.pdf':
            is_pdf = True
            file_path = abs_file_path

        elif ext == '':
            if 'pdf' in file_type:
                is_pdf = True
                file_renamed = f'{abs_file_path}.pdf'
            else:
                #All other file_type will be considered as image/png
                is_pdf = False
                file_renamed = f'{abs_file_path}.png'
            shutil.copyfile(abs_file_path, file_renamed)
            file_path = file_renamed

        else:
            is_pdf = False
            file_path = abs_file_path

        file_list.append(file_path)

    if is_pdf:
        pdf_filename = file_list[-1]
    else:
        pdf_filename = tempfile.NamedTemporaryFile(suffix='.pdf').name
        with open(pdf_filename, "wb") as f:
            try:
                f.write(img2pdf.convert(file_list))
            except Exception as e:
                logger.exception('generate_base64pdf', msg=str(e), items=items)
    try:
        if compress_level == -1:
            raise Exception('File compress switch does not exist')
        compressed_filename = tempfile.NamedTemporaryFile(suffix='.pdf').name
        compress(pdf_filename, compressed_filename, power=compress_level)
    except:
        compressed_filename = pdf_filename

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



@register.filter
def fuzzymatch(name_list, match_with):
    str_a = ' '.join(name_list) if isinstance(name_list, list) else name_list
    str_b = match_with

    # for invalid input
    if not (len(str_a) or len(str_b)):
        return 0
    str_a = str_a.lower().strip()
    str_b = str_b.lower().strip()
    sub_str_a = str_a.split(" ")
    sub_str_b = str_b.split(" ")

    # for identical strings
    if str_a == str_b:
        return 100

    # for similar male/female names
    if abs(len(str_a) - len(str_b)) == 1:
        if len(sub_str_a[0]) > len(sub_str_b[0]):
            big, small = sub_str_a[0], sub_str_b[0]
        else:
            big, small = sub_str_b[0], sub_str_a[0]
        last = list(big[-1])
        meta = ["a", "e", "i", "o", "u"]
        if last[0] in meta and big[:-1] == small:
            return 0
        return fuzz.ratio(str_a, str_b)

    # for non identical string with equal sub parts
    if len(sub_str_a) == len(sub_str_b):
        if len(str_a) == len(str_b):
            temp_res = fuzz.token_sort_ratio(str_a, str_b)
            if temp_res == 100:
                return temp_res
        return fuzz.ratio(str_a, str_b)
    else:
        # non identical strings with unequal sub parts
        return fuzz.ratio(str_a, str_b)
