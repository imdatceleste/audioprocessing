# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import os
import re
_comma_number_re = re.compile(r'([0-9][0-9\.]+[0-9])')
_decimal_number_re = re.compile(r'([0-9]+\,[0-9]+)')
_pounds_re = re.compile(r'£([0-9\.]*[0-9]+)')
_dollars_re = re.compile(r'\$([0-9\,\.]*[0-9]+)')
_ordinal_re = re.compile(r'[0-9]+\.')
_number_re = re.compile(r'[0-9]+')


"""
Numeric to word convertor in Italian

Copyright (c) 2017 Munich Artificial Intelligence Laboratories GmbH (M-AILABS)

Created: 2017-02-25 ??:?? CET, KA
"""

def _get_decimal(decimalPart):
    '''
    Returns decimal part numbers with the correct word of seperator
    '''
    units = [u'zero', u'uno', u'due', u'tre', u'quattro', u'cinque', u'sei', u'sette', u'otto', u'nove']
    comma = u'virgola'
    return ' '.join([units[int(i)] for i in decimalPart]), comma


def _num_to_words(num):
    '''
    Italian converter
    Params:
        num(int/long): number to be converted
    Returns:
        wordString  
    '''
    units = ['', u'uno', u'due', u'tre', u'quattro', u'cinque', u'sei', u'sette', u'otto', u'nove']
    teens = ['', u'undici', u'dodici', u'tredici', u'quattordici', u'quindici', u'sedici', u'diciassette', u'diciotto', u'diciannove']
    tens = ['', u'dieci', u'venti', u'trenta', u'quaranta', u'cinquanta', u'sessanta', u'settanta',  u'ottanta', u'novanta']
    centos = ['', u'cento', u'duecento', u'trecento', u'quattrocento', u'cinquecento', u'seicento', u'settecento', u'ottocento', u'novecento']
    thousands = ['', u'mila', u'milioni', u'miliardi']

    words = []
    if num==0: words.append(u'zero')
    else:
        # Convert num to string
        numStr = '%d'%num
        numStrLen = len(numStr)
        # Get the number of group with 3 digits 
        groups = (numStrLen+2)/3
        if groups>(len(thousands)):
            return ''
        # Pad the zereos to the missing digits
        numStr = numStr.zfill(groups*3)
        for i in range(0,groups*3,3):
            h,t,u = int(numStr[i]),int(numStr[i+1]),int(numStr[i+2])
            g = groups-(i/3+1)
            # Add hundreds
            if h>=1:
               words.append(centos[h])
            # Add tens
            if t>1:
                if u==1 or u==8: 
                    words.append(tens[t][:-1] + units[u])
                elif u==3: 
                    words.append(tens[t] + u'tré')
                else: 
                    words.append(tens[t] + units[u])
            # Add teens
            elif t==1:
                if u>=1: words.append(teens[u])
                else: words.append(tens[t])
            # If second digit is zero
            else:
                # In order not to say 'bir bin'
                if (g==1 and u==1):
                    words.append('')
                elif (g==3 and u==1) or (g==4 and u==1):
                    words.append('un')
                else:
                    if u>=1: words.append(units[u])
            # Add thousands
            if (g==1) and (h==0 and t==0 and u==1):
                words.append(u'mille')
            elif (g==2) and (h==0 and t==0 and u==1):
                words.append(u'milione')
            elif (g==3) and (h==0 and t==0 and u==1):
                words.append(u'miliardo')
            elif (g>=1) and ((h+t+u)>0): 
                words.append(thousands[g])
    return ' '.join(words)


def _ntow(num):
    if type(num)!=int and type(num)!=float and type(num)!=long: return ''
    if type(num)==float:
        numStr = str(num)
        if '.' in numStr:
            splitNum=numStr.split('.')                
        elif ',' in numStr:
            splitNum=numStr.split(',')
        dec,comma=_get_decimal(splitNum[1])
        comma=' ' + comma + ' '            
        return _num_to_words(long(num)) + comma + dec
    return _num_to_words(num)


def _remove_commas(m):
    return m.group(1).replace('.', '')


def _expand_number(m):
    num_str = m.group(0)
    if ',' in num_str:
        num_str = num_str.replace(',', '.')
        num = float(num_str)
    else:
        num = int(num_str)
    return _ntow(num)


def it_normalize_numbers(text):
    text = re.sub(_comma_number_re, _remove_commas, text)
    text = re.sub(_decimal_number_re, _expand_number, text)
    text = re.sub(_number_re, _expand_number, text)
    return text


