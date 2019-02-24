from __future__ import print_function, unicode_literals

import sys
import json
import codecs
from os.path import isfile, join

reload(sys)
sys.setdefaultencoding('utf8')

import getopt
import os

from aeneas.tools.execute_task import ExecuteTaskCLI
from audio_splitter import make_split


def create_result_folder(data_file):
    result_path = os.path.splitext(data_file)[0]
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    return result_path


all_jsons = None


def set_proper_filename_id(json_filepath, filename_prefix):
    global all_jsons
    aeneas_json = json.load(codecs.open(json_filepath, 'r', 'utf-8'))
    for entry in aeneas_json['fragments']:
        s_key = entry['id']
        s_key = filename_prefix + '_' + s_key
        entry['id'] = s_key
    json.dump(aeneas_json, codecs.open(json_filepath, 'w', 'utf-8'), indent=4)
    if all_jsons is None:
        all_jsons = aeneas_json
    else:
        all_jsons['fragments'].extend(aeneas_json['fragments'])
    root_book_folder = os.path.split(os.path.dirname(json_filepath))[0]
    root_json_path = os.path.join(root_book_folder, 'result.json')
    json.dump(all_jsons, codecs.open(root_json_path, 'w', 'utf-8'), indent=4)


def arrange(folder_path):
    folders = list()
    allitems = os.listdir(folder_path)
    for item in allitems:
        item_folder_path = join(folder_path, item)
        if isfile(item_folder_path) is False:
            folders.append(item_folder_path)

    for folder in folders:
        folder_items = os.listdir(folder)
        book_text_file_path = folder + '/' + os.path.basename(folder) + '.txt'
        book_audio_file_path = None
        for file_item in folder_items:
            if file_item.endswith('.mp3') or file_item.endswith('.wav'):
                book_audio_file_path = os.path.join(folder, file_item)
                break

        if book_audio_file_path is None:
            print('Can\'t find audio for chapter in folder: {}'.format(folder))
            continue

        json_filepath = os.path.join(folder, os.path.basename(folder) + '.json')

        args = [
            "dummy",
            book_audio_file_path,
            book_text_file_path,
            'task_language=deu|is_text_type=plain|os_task_file_format=json|is_audio_file_detect_head_max=1|task_adjust_boundary_nonspeech_string=REMOVE',
            json_filepath
        ]
        exit_code = ExecuteTaskCLI(use_sys=False).run(arguments=args)
        print('Folder {} done with  exit code: {}'.format(os.path.basename(folder), exit_code))
        if exit_code == 0:
            set_proper_filename_id(json_filepath, os.path.basename(folder))

    print('Aeneas finished all the fodlers')


def split_audio(folder_path):
    folders = list()
    allitems = os.listdir(folder_path)
    for item in allitems:
        item_folder_path = join(folder_path, item)
        if isfile(item_folder_path) is False:
            folders.append(item_folder_path)

    for folder in folders:
        folder_items = os.listdir(folder)
        json_file_path = os.path.join(folder, os.path.basename(folder) + '.json')
        book_audio_file_path = None
        for file_item in folder_items:
            if file_item.endswith('.mp3') or file_item.endswith('.wav'):
                book_audio_file_path = os.path.join(folder, file_item)
                break

        if book_audio_file_path is None:
            print('Can\'t find audio for chapter in folder: {}'.format(folder))
            continue
        make_split(json_file_path, book_audio_file_path)
        print('Audio splitted: {}'.format(book_audio_file_path))
    print('Split audio is done')


def print_usage():
    print('Usage:')
    print('\tpython aeneas_runner.py -f <path to folder with chapters folders>')
    sys.exit(1)


if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'f:', ['--folder'])
    except getopt.GetoptError:
        print_usage()
    path = None
    for opt, arg in options:
        if opt in ('-f', '--folder'):
            path = arg

    if path is None:
        print_usage()

    arrange(folder_path=path)
    split_audio(folder_path=path)
