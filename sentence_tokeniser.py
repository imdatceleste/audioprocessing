# coding=utf-8
from __future__ import print_function, unicode_literals

import sys
import getopt
import codecs
import os
from nltk.tokenize import sent_tokenize

reload(sys)
sys.setdefaultencoding('utf8')


def create_result_folder(data_file):
    result_path = os.path.splitext(data_file)[0]
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    return result_path


def tokenise(data_file, language='english', sen_max_len=None, pass_tokenise=False):
    if language is None:
        language = 'english'
    if sen_max_len is None:
        sen_max_len = 800
    resulf_folder_path = create_result_folder(data_file)
    filename = os.path.splitext(os.path.basename(data_file))[0]+'.txt'

    book_text = ' '.join(codecs.open(data_file, 'r', 'utf-8').readlines())
    book_text = cleanup_booktext(book_text)

    if pass_tokenise:
        sentence_tokens = codecs.open(data_file, 'r', 'utf-8').readlines()
    else:
        sentence_tokens = sent_tokenize(book_text, language=language)
    book_text = ''
    for line in sentence_tokens:
        if len(line) >= sen_max_len:
            split_lines = split_too_long_line(line, sen_max_len)
            book_text = book_text + split_lines
        else:
            book_text = book_text + line + '\n'
    filepath = write_strings_to_file(book_text, resulf_folder_path, filename)
    return filepath


def cleanup_booktext(txt):
    clean_text = txt
    items_to_remove = [u'«', u'»', u'›', u'‹', u'–', '„', '“']
    for item in items_to_remove:
        clean_text = clean_text.replace(item, '')
    clean_text = clean_text.replace('\n', ' ')
    clean_text = clean_text.replace('  ', ' ')
    return clean_text


def split_too_long_line(str_to_cut='', maxlen=800):
    string_to_cut = str_to_cut
    result = ''
    # chars_set = [';', ':', ',']
    chars_set = [u'»', u'...', u'.', u'!', u'?', u';', u':', u',']
    strong_chars_set = [u'»', u'...', u'.', u'!', u'?', u';', u':']
    window_left = 50
    window_right = 100
    for item in chars_set:
        # looking for a separator in [-window_left : + window_right] characters window
        winleft = maxlen - 50 if item in strong_chars_set else window_left
        found_index = string_to_cut.find(item, max(1, maxlen-winleft), min(len(string_to_cut), maxlen+window_right))
        if found_index > 0 and (len(string_to_cut) - found_index > 30):
            result = result + string_to_cut[0:found_index+1].strip() + '\n'
            string_to_cut = string_to_cut[found_index+1:].strip()
            break
    if len(string_to_cut) > maxlen and len(string_to_cut) != len(str_to_cut):  # avoid to recursion fall if there no punctuation
        string_to_cut = split_too_long_line(string_to_cut, maxlen)
    result = result + string_to_cut + '\n'
    result = result.replace('\n\n', '\n')
    return result


def write_strings_to_file(text, result_dir, filename):
    filepath = os.path.join(result_dir, filename)
    f = codecs.open(filepath, 'w', 'utf-8')
    print(text, file=f)
    f.close()
    return filepath


def print_usage():
    print('Usage:')
    print('\tpython sentence tokeniser.py -f <txtfile> -l <language>, -m <line max len>, -n (use if language not supported and you want kust split to chapters and limit lines)')
    sys.exit(1)

if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'f:l:m:n', ['--file', '--language', '--maxlen', '--not_tokenise'])
    except getopt.GetoptError:
       print_usage()

    text_file = None
    language = None
    sen_len = 800
    not_tokenise = False
    for opt, arg in options:
        if opt in ('-f', '--file'):
            text_file = arg
        if opt in ('-l', '--language'):
            language = arg
        if opt in ('-m', '--maxlen'):
            sen_len = int(arg)
        if opt in ('-n', '--not_tokenise'):
            not_tokenise = True

    if text_file is None:
        print_usage()

    tokenise(data_file=text_file, language=language, sen_max_len=180, pass_tokenise=not_tokenise)
