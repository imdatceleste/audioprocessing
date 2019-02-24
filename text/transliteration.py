# -*- encoding: utf8 -*-
from __future__ import print_function
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
ascii_chars = u'ABCDEFGHIJKLMNOPQRSTUVWYXZabcdefghijklmnopqrstuvwxyz0123456789!\',-.:;? '


de_chars = ascii_chars + u'äöüßÄÖÜ'
tr_chars = ascii_chars + u'ışğçäöüİŞĞÇÄÖÜ'
it_chars = ascii_chars + u'àéèìíîòóùúÀÉÈÌÍÎÒÓÙÚ'
es_chars = ascii_chars + u'¡¿ñáéíóúÁÉÍÓÚÑ'
fr_chars = ascii_chars + u'àâæçéèêëîïôœùûüÿŸÜÛÙŒÔÏÎËÊÈÉÇÆÂÀ'
uk_chars = ascii_chars + u'АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯабвгґдеєжзиіїйклмнопрстуфхцчшщьюя'
ru_chars = ascii_chars + u'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
pl_chars = ascii_chars + u'ĄĆĘŁŃÓŚŹŻąćęłńóśźż'

languages = {
            'en': ascii_chars,
            'de': de_chars,
            'tr': tr_chars,
            'it': it_chars,
            'es': es_chars,
            'fr': fr_chars,
            'uk': uk_chars,
            'ru': ru_chars,
            'pl': pl_chars
            }
transliteration_table = {
    u'–': {
            'default': '-'
        },
    u'—': {
            'default': '-'
        },
    u'¡': {
            'default': '', 
        },
    u'¿': { 
            'default': '',
        },
    u'à': { 
            'default': 'a'
        },
    u'á': { 
            'default': 'a'
        },
    u'ä': { 
            'default': 'ae'
        },
    u'â': { 
            'default': 'a'
        },
    u'æ': { 
            'default': 'ae'
        },
    u'Ä': { 
            'default': 'Ae'
        },
    u'À': { 
            'default': 'A'
        },
    u'Á': {
            'default': 'A'
        },
    u'Æ': { 
            'default': 'Ae'
        },
    u'Â': { 
            'default': 'A'
        },
    u'À': { 
            'default': 'A'
        },
    u'ç': {
            'default': 'c',
            'de': 'tsch',
            'en': 'ch',
            'es': 'ch',
            'fr': 'ç',
            'uk': u'ч'
        },
    u'Ç': { 
            'default': 'C',
            'de': 'Tsch',
            'en': 'Ch'
        },
    u'é': { 
            'default': 'e'
        },
    u'è': { 
            'default': 'e'
        },
    u'ê': {
            'default': 'e'
        },
    u'ë': { 
            'default': 'e'
        },
    u'É': { 
            'default': 'E'
        },
    u'È': { 
            'default': 'E'
        },
    u'Ë': { 
            'default': 'E'
        },
    u'Ê': { 
            'default': 'E'
        },
    u'ğ': { 
            'default': 'gh'
        },
    u'Ğ': { 
            'default': 'Gh'
        },
    u'ì': { 
            'default': 'i'
        },
    u'í': { 
            'default': 'i'
        },
    u'î': { 
            'default': 'i'
        },
    u'ï': { 
            'default': 'i'
        },
    u'Ì': { 
            'default': 'I'
        },
    u'Í': { 
            'default': 'I'
        },
    u'Ï': { 
            'default': 'I'
        },
    u'Î': { 
            'default': 'I'
        },
    u'ı' : {
            'default': 'i'
        },
    u'İ': { 
            'default': 'I'
        },
    u'ñ': { 
            'default': 'n',
            'de': 'ny'
        },
    u'Ñ': { 
            'default': 'n',
            'de': 'Ny'
        },
    u'ö': { 
            'default': 'oe'
        },
    u'ò': { 
            'default': 'o'
        },
    u'ó': { 
            'default': 'o'
        },
    u'ô': { 
            'default': 'o'
        },
    u'œ': { 
            'default': 'oe'
        },
    u'Ö': { 
            'default': 'Oe'
        },
    u'Œ': { 
            'default': 'Oe'
        },
    u'Ô': { 
            'default': 'O'
        },
    u'Ò': { 
            'default': 'O'
        },
    u'Ó': { 
            'default': 'O'
        },
    u'ü': { 
            'default': 'ue'
        },
    u'ù': { 
            'default': 'u'
        },
    u'û': { 
            'default': 'u'
        },
    u'ú': { 
            'default': 'u'
        },
    u'Û': { 
            'default': 'U'
        },
    u'Ù': { 
            'default': 'U'
        },
    u'Ù': { 
            'default': 'U'
        },
    u'Ü': { 
            'default': 'Ue'
        },
    u'ß': { 
            'default': 'ss'
        },
    u'ş': { 
            'default': 'sh',
            'de': 'sch',
            'uk': u'ш'
        },
    u'Ş': { 
            'default': 'Sh',
            'de': 'Sch'
        },
    u'ÿ': { 
            'default': 'y'
        },
    u'Ÿ': { 
            'default': 'Y'
        }
}


def transliterate_text(line, language):
    language_charset = languages.get(language, ascii_chars)
    outline = ''
    for s in line:
        if s in language_charset:
            outline += s
        else:
            mapping_list = transliteration_table.get(s, None)
            if mapping_list is not None:
                mapping = mapping_list.get(language, None)
                if mapping is None:
                    mapping = mapping_list.get('default', None)
                if mapping is not None:
                    char = mapping
                    outline += char
    return outline


if __name__ == '__main__':
    line = u'çabcdefghijklĞ'
    language = 'de'
    print('{} ==> {}'.format(line, transliterate_text(line, language)))

