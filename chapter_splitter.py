from __future__ import print_function, unicode_literals
import getopt
import codecs
import os
import sys
import subprocess
reload(sys)
sys.setdefaultencoding('utf8')


def create_result_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def split_text(data_file, chapter_splitter_word=None, destination_folder=None):
    result_folder_path = None
    if destination_folder is not None:
        create_result_folder(destination_folder)
        result_folder_path = destination_folder
    else:
        result_folder_path = os.path.dirname(data_file)

    file_base_name = os.path.splitext(os.path.basename(data_file))[0]
    text_lines = codecs.open(data_file, 'r', 'utf-8').readlines()
    chapter_index = 0
    accumulated_chapter_text = ''
    for line in text_lines:
        if chapter_splitter_word is not None and chapter_splitter_word.lower() in line.lower():
            if chapter_index > 0:
                write_strings_to_file(accumulated_chapter_text, result_folder_path, file_base_name, chapter_index)
                accumulated_chapter_text = ''
            chapter_index += 1
        accumulated_chapter_text = accumulated_chapter_text + line.replace('|', '')
    if len(accumulated_chapter_text) != 0:
        write_strings_to_file(accumulated_chapter_text, result_folder_path, file_base_name, chapter_index)
    return result_folder_path


def write_strings_to_file(text, result_dir, base_filename, chapter_index):
    filename = '{}_{}.txt'.format(base_filename, str(chapter_index).zfill(3))
    filepath = result_dir + '/' + filename
    f = codecs.open(filepath, 'w', 'utf-8')
    print(text, file=f)
    f.close()


def print_usage():
    print('Usage:')
    print('\tpython sentence tokeniser.py -f <txtfile> -s <split text>, -d <destination folder path>.')
    sys.exit(1)


if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'f:s:d:', ['--file', '--split_text', '--destination_folder'])
    except getopt.GetoptError:
        print_usage()

    text_file = None
    splitter = None
    destination_path = None
    for opt, arg in options:
        if opt in ('-f', '--file'):
            text_file = arg
        if opt in ('-s', '--split_text'):
            splitter = arg
        if opt in ('-d', '--destination_folder'):
            destination_path = arg

    if text_file is None:
        print_usage()

    split_text(data_file=text_file, chapter_splitter_word=splitter, destination_folder=destination_path)
