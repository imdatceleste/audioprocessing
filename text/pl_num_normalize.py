# -*- encoding: utf8 -*-
from __future__ import print_function
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import os
import codecs
import re

_decimal_number_re = re.compile(r'([0-9]+[\.\,][0-9]+)')
_number_re = re.compile(r'[0-9\|]+')

num_to_20 = [u'', u'jeden', u'dwa', u'trzy', u'cztery', u'pięć', u'sześć', u'siedem', u'osiem', u'dziewięć', u'dziesięć', u'jedenaście', u'dwanaście', u'trzynaście', u'czternaście', u'piętnaście', u'szesnaście', u'siedemnaście', u'osiemnaście', u'dziewiętnaście']
num_tens = [u'', u'dziesięć', u'dwadzieścia', u'trzydzieści', u'czterdzieści', u'п\'pięćdziesiąt', u'sześćdziesiąt', u'siedemdziesiąt', u'osiemdziesiąt', u'dziewięćdziesiąt']
num_hundreds = [u'', u'sto', u'dwieście', u'trzysta', u'czterysta', u'pięćset', u'sześćset', u'siedemset', u'osiemset', u'dziewięćset']
num_to_add = [u'', u'jeden', u'dwa', u'trzy', u'cztery', u'pięć', u'sześć', u'siedem', u'osiem', u'dziewięć']

decimal_zero = u'zero'
one_female = u'jedna'
two_female = u'dwie'

mio_falls = [u'milion', u'miliony', u'milionów']
thousand_falls = [u'tysiąc', u'tysiące', u'tysięcy']

decimal_float_tens_falls = [u'dziesiąta', u'dziesiate']
decimal_float_hundreds_falls = [u'setna', u'setnych']
decimal_float_thousands_falls = [u'tysięczna', u'tysięcznych']
decimal_float_ten_thousands_falls = [u'dziesięciotysięczną', u'dziesięciotysięcznych']

_whitespace_re = re.compile(r'\s+')


def collapse_whitespace(text):
    return re.sub(_whitespace_re, ' ', text)


def _expand_decimal_point(m):
    num_str = m.group(0)
    num_str = num_str.replace('.', '|')
    return num_str


def _get_millions(full_num_str):
    millions_only_str = full_num_str[0:len(full_num_str) - 6]
    num = int(millions_only_str)
    tens_mio_num = num % 100
    count_text = _get_count_string_until_thouthand(millions_only_str)
    mio_fall_text = _get_mio_thousand_fall(tens_mio_num, mio_falls)
    result = collapse_whitespace(count_text + ' ' + mio_fall_text).strip()
    return result


def _get_thousands(full_num_str):
    thousands_only_str = full_num_str[max(0, len(full_num_str) - 6):len(full_num_str) - 3]
    num = int(thousands_only_str)
    tens_th_num = num % 100
    count_text = _get_count_string_until_thouthand(thousands_only_str, last_one_two_female=True)
    th_fall_text = _get_mio_thousand_fall(tens_th_num, thousand_falls)
    result = collapse_whitespace(count_text + ' ' + th_fall_text).strip()
    return result


def _get_mio_thousand_fall(number_max_99, fall_list):
    num = int(number_max_99)
    if num == 0:
        return ''

    if num in range(11, 19):
        res_index = 2
    else:
        last_digit = num % 10
        if last_digit == 1:
            res_index = 0
        elif last_digit in [2, 3, 4]:
            res_index = 1
        else:
            res_index = 2

    result = fall_list[res_index]
    return result


def _get_count_string_until_thouthand(num_str_max_999, last_one_two_female=False):
    num = int(num_str_max_999)
    hundreds = ''
    tens = ''
    if num > 99:
        hundred_index = int(num / 100)
        hundreds = num_hundreds[hundred_index]

    tens_num = num % 100
    if tens_num <= 19:
        to_twenty = num_to_20[tens_num]
        if last_one_two_female:  # 1 and 2 thousands or digit before decimal has female numbers
            if tens_num == 1:
                to_twenty = one_female
            if tens_num == 2:
                to_twenty = two_female
    else:
        tens_index = int(tens_num / 10)
        tens = num_tens[tens_index]
        to_ten_index = tens_num % 10
        to_twenty = num_to_add[to_ten_index]

        if last_one_two_female:  # 1 and 2 thousands or last or digit before decimal has female numbers
            if to_ten_index == 1:
                to_twenty = one_female
            if tens_index == 2:
                to_ten_index = two_female

    result = hundreds + ' ' + tens + ' ' + to_twenty
    result = collapse_whitespace(result).strip()
    return result


def _make_pl_float_full_part(num_str):
    result = ''
    decimal_part_separator = 'i'
    if num_str == '0':
        result = decimal_zero + ' ' + decimal_part_separator
    else:
        num_parsed = _make_pl_integer(num_str, last_female=True)
        result = num_parsed + ' ' + decimal_part_separator
    return result


def _make_pl_float_decimal_part(num_str):
    result = ''
    num = int(num_str)
    if num == 0:
        result = decimal_zero + ' ' + decimal_float_tens_falls[1]
    else:
        strlen = len(num_str)
        num_parsed = _make_pl_integer(num_str, last_female=True)
        if strlen == 1:
            float_part_fall_dict = decimal_float_tens_falls
        elif strlen == 2:
            float_part_fall_dict = decimal_float_hundreds_falls
        elif strlen == 3:
            float_part_fall_dict = decimal_float_thousands_falls
        elif strlen == 4:
            float_part_fall_dict = decimal_float_ten_thousands_falls

        float_part_fall = float_part_fall_dict[1]
        if (num % 10 == 1) and (num % 20 is not 11):
            float_part_fall = float_part_fall_dict[0]
        result = num_parsed + ' ' + float_part_fall
    return result


def _make_pl_integer(num_str, last_female=False):
    text = ''
    strlen = len(num_str)
    if strlen > 6:
        text += _get_millions(num_str)

    if strlen > 3:
        text = '{0} {1}'.format(text, _get_thousands(num_str))

    text = '{0} {1}'.format(text, _get_count_string_until_thouthand(num_str[max(0, len(num_str) - 3):len(num_str)], last_one_two_female=last_female))
    return text


def _make_pl_num(num_str):
    text = ''
    if '|' in num_str:
        integer_part, float_part = num_str.split('|', 2)
        int_processed = _make_pl_float_full_part(integer_part)
        float_processed = _make_pl_float_decimal_part(float_part)
        text = int_processed + ' ' + float_processed

    else:  # process as integer number
        text = _make_pl_integer(num_str)

    collapse_whitespace(text).strip()
    return text


def _expand_number(m):
    num_str = m.group(0)
    return _make_pl_num(num_str)


def pl_normalize_numbers(text):
    text = re.sub(_decimal_number_re, _expand_decimal_point, text)
    text = text.replace(',', '')  # In polish copmma used for thouthands separators
    text = collapse_whitespace(re.sub(_number_re, _expand_number, text)).strip()
    return text


if __name__ == '__main__':
    texts = [u'12,530', u'1.0', u'126897.56', u'15.96', u'8080808', u'121000.1001', u'20,250', u'11,569']
    for substring in texts:
        print(substring, '==>', pl_normalize_numbers(substring))
