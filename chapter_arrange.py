from __future__ import print_function, unicode_literals

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import getopt
import os


def create_result_folder(data_file):
    result_path = os.path.splitext(data_file)[0]
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    return result_path


def arrange(path):
    audios = list()
    text_files = list()
    allfiles = os.listdir(path)
    for item in allfiles:
        if item.endswith('.mp3') or item.endswith('.wav'):
            audios.append(path + '/' +item)
        elif item.endswith('.txt'):
            text_files.append(path + '/' +item)
    audios.sort()
    text_files.sort()
    index = 0

    for text_path in text_files:
        chapter_folder = create_result_folder(text_path)
        audio_path = audios[index]
        text_file = os.path.basename(text_path)
        audio_file = os.path.basename(audio_path)
        text_destination = chapter_folder+'/'+text_file
        audio_destination = chapter_folder+'/'+audio_file
        os.rename(text_path, text_destination)
        os.rename(audio_path, audio_destination)
        index += 1

if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'p:', ['--path'])
    except getopt.GetoptError:
        print('Usage:')
        print('\tpython chapter_arrange.py -p <path to folder>')
        sys.exit(1)
    path = None
    for opt, arg in options:
        if opt in ('-p', '--path'):
            path = arg
    if path is None:
        print('Usage:')
        print('\tpython chapter_arrange.py -p <path to folder>')

    arrange(path=path)
