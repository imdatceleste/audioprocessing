# -*- encoding: utf8 -*-
from __future__ import print_function
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import codecs
import re

_comma_number_re = re.compile(r'([0-9][0-9\.]+[0-9])')
_decimal_number_re = re.compile(r'([0-9]+\,[0-9]+)')
_pounds_re = re.compile(r'£([0-9\.]*[0-9]+)')
_dollars_re = re.compile(r'\$([0-9\,\.]*[0-9]+)')
_ordinal_re = re.compile(r'[0-9]+\.')
_number_re = re.compile(r'[0-9]+')

num_to_20 = [u'', u'un', u'deux', u'trois', u'quatre', u'cinq', u'six', u'sept', u'huit', u'neuf', u'dix', u'onze', u'douze', u'treize', u'quatorze', u'quinze', u'seize', u'dix-sept', u'dix-huit', u'dix-neuf']
num_tens = [u'', u'dix', u'vingt', u'trente', u'quarante', u'cinquante', u'soixante', u'soixante-dix', u'quatre-vingt', u'quatre-vingt-dix']
num_to_add = [u'', u'un', u'deux', u'trois', u'quatre', u'cinq', u'six', u'sept', u'huit', u'neuf']
text = 'num_to_20 + num_tens + num_to_add'
special_num = [u'soixante', u'quatre-vingt']
_whitespace_re = re.compile(r'\s+')


def collapse_whitespace(text):
    return re.sub(_whitespace_re, ' ', text)


def _remove_commas(m):
    return m.group(1).replace('.', '')


def _expand_decimal_point(m):
    return m.group(1).replace(',', ' virgule ')


def _expand_dollars(m):
    match = m.group(1)
    parts = match.split(',')
    if len(parts) > 2:
        return match + ' euro'  # Unexpected format
    dollars = int(parts[0]) if parts[0] else 0
    cents = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    if dollars and cents:
        dollar_unit = 'euro' if dollars == 1 else 'euro'
        cent_unit = 'cent' if cents == 1 else 'cent'
        return '%s %s, %s %s' % (dollars, dollar_unit, cents, cent_unit)
    elif dollars:
        dollar_unit = 'euro' if dollars == 1 else 'euro'
        return '%s %s' % (dollars, dollar_unit)
    elif cents:
        cent_unit = 'cent' if cents == 1 else 'cent'
        return '%s %s' % (cents, cent_unit)
    else:
        return 'zéro euro'


def _expand_ordinal(m):
    num_str = m.group(0)
    num_str = num_str.replace('.', '')
    text = _make_de_num(num_str)
    text = text + ''
    return text


def _get_tens(num_str):
    num = int(num_str)
    if num == 0:
        return ''
    text = ''
    if num > 9:
        single = int(num_str[1])
        tens = int(num_str[0])
    else:
        single = int(num_str)
        tens = 0

    if single > 0:
        if tens > 1:
            if tens == 7:
                single = single + 10
                text = special_num[0] + '-' + num_to_20[single]
            elif tens == 9:
                single = single + 10
                text = special_num[1] + '-' + num_to_20[single]
            else:
                text =  num_tens[tens] + '-' + num_to_add[single]
        else:
            x = tens * 10 + single
            text = num_to_20[x]
    else:
        text = num_tens[tens]
    return text


def _get_hundreds(num, has_thousands=False):
    if num == 0:
        return ''
    elif num == 1 and not has_thousands:
        return 'cent'
    else:
        return num_to_add[num] + 'cent'


def _get_thousands(num, has_millions=False):
    if num == 0:
        return ''
    elif num == 1 and not has_millions:
        return 'mille'
    else:
        return num_to_add[num] + 'mille'


def _make_de_num(num_str, thousands_helper=False):
    text = ''
    num = int(num_str)
    num_length = len(num_str)
    if num_length == 1:
        text = num_to_20[num]
    elif num_length == 2:
        text = _get_tens(num_str)
    elif num_length == 3:
        tens = num_str[1:]
        text = _get_tens(tens)
        num = int(num_str[0])
        text = _get_hundreds(num, thousands_helper) + text
    elif num_length == 4:
        thousands_helper = True
        tens = num_str[2:]
        text = _get_tens(tens)
        num = int(num_str[1])
        text = _get_hundreds(num, thousands_helper) +  text
        num = int(num_str[0])
        text = _get_thousands(num, False) +  text
    elif num_length > 4 and num_length <= 6:
        thousands_helper = True
        back_part = num_str[-3:]
        front_part = num_str[:len(num_str) - 3]
        back_str = _make_de_num(back_part, thousands_helper)
        front_str = _make_de_num(front_part, thousands_helper) + 'mille'
        text = front_str + back_str
    elif num_length > 6 and num_length <= 9:
        back_part = num_str[-6:]
        front_part = num_str[:len(num_str) - 6]
        back_str = _make_de_num(back_part, True)
        front_str = _make_de_num(front_part)
        if num_length == 7:
            front_str = front_str + 'million'
        else:
            front_str = front_str + 'des millions'
        text = front_str + back_str
    else:
        text = 'TBD'

    return collapse_whitespace(text)


def _expand_number(m):
    num_str = m.group(0)
    return _make_de_num(num_str)


def fr_normalize_numbers(text):
    text = re.sub(_comma_number_re, _remove_commas, text)
    text = re.sub(_decimal_number_re, _expand_decimal_point, text)
    if text[-1] == '.':
        dot_found = True
        text = text[:-1]
    else:
        dot_found = False
    text = re.sub(_ordinal_re, _expand_ordinal, text)
    if dot_found:
        text += '.'
    text = re.sub(_number_re, _expand_number, text)
    return text


if __name__ == '__main__':
    text = u'78654' \
           u'...'
    print(text, '==>', fr_normalize_numbers(text))

