from __future__ import print_function, unicode_literals

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import getopt
import json
import codecs
import os


def read_audio_entries(jsn_file):
    json_data = json.load(codecs.open(jsn_file, 'r', 'utf-8'))
    audio_entries = list()
    for entry in json_data['fragments']:
        audio_entry = AudioEntry(entry)
        audio_entries.append(audio_entry)
    return audio_entries


def transform_all_jsons(folder_path=None, destination_path=None):
    result_file_path = destination_path
    if folder_path is None:
        print('Folder path is not defined')
        return False
    json_files = list()
    allfiles = os.listdir(folder_path)
    for item in allfiles:
        if item.endswith('.json'):
            json_files.append(os.path.join(folder_path, item))

    all_audio_entries = list()
    for item in json_files:
        audio_entries = read_audio_entries(jsn_file=item)
        all_audio_entries.extend(audio_entries)

    if destination_path is None:
        result_file_path = os.path.join(folder_path, 'all_audio_items.txt')
    return write_audio_entries_to_file(all_audio_entries, result_file_path)


def write_audio_entries_to_file(audio_entries, file_path):
    csv_text = ''
    audio_entries.sort(key=lambda x: x.id, reverse=False)
    for audio_entry in audio_entries:
        if len(audio_entry.text) > 0:
            text = audio_entry.text[0]
            if len(text) > 0:
                csv_text = csv_text + audio_entry.id + '.wav' + '|' + text + '\n'
    f = codecs.open(file_path, 'w', 'utf-8')
    if f is None:
        print('Can\'t open file for write: {}'.format(file_path))
        return False
    print(csv_text, file=f)
    f.close()
    return True


def transform(data_file, dest_file):
    audio_entries = read_audio_entries(jsn_file=data_file)
    result_path = os.path.splitext(data_file)[0]
    if dest_file is None:
        csv_fname = result_path + '.txt'
    else:
        csv_fname = dest_file

    write_audio_entries_to_file(audio_entries, csv_fname)


class AudioEntry:
    def __init__(self):
        self.start = None
        self.end = None
        self.id = None
        self.text = None

    def __init__(self, json_entry):
        self.start = json_entry['begin']
        self.end = json_entry['end']
        self.id = json_entry['id']
        self.text = json_entry['lines']


def print_usage():
    print('Usage:')
    print('\tpython audio_split.py -j <jsonfile>')
    sys.exit(1)


if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'j:', ['--json'])
    except getopt.GetoptError:
        print_usage()
    json_file = None

    for opt, arg in options:
        if opt in ('-j', '--json'):
            json_file = arg

    if json_file is None:
        print_usage()
    transform(data_file=json_file)
