from __future__ import print_function, unicode_literals

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import getopt
import json
import codecs
import os
import librosa


def read_audio_entries(data_file):
    json_data = json.load(codecs.open(data_file, 'r', 'utf-8'))
    audio_entries = list()
    for entry in json_data['fragments']:
        audio_entry = AudioEntry(entry)
        audio_entries.append(audio_entry)
    return audio_entries


def make_split(data_file, sound_file, start_shift_in_seconds=-0.1, end_shift_in_seconds=-0.1):
    audio_entries = read_audio_entries(data_file=data_file)
    result_path = os.path.splitext(sound_file)[0]
    if not os.path.exists(result_path):
        os.makedirs(result_path)

    return cut_sound_files_librosa(audio_entries, sound_file, result_path, start_shift_in_seconds, end_shift_in_seconds)


def cut_sound_files_librosa(audio_entries, sound_file, result_folder_path, start_shift_in_seconds=-0.1, end_shift_in_seconds=-0.1):
    audio_data, sample_rate = librosa.load(sound_file)
    for audio_entry in audio_entries:
        if len(audio_entry.text[0]) == 0:
            continue

        start = float(audio_entry.start)
        if start < 0:
            start = 0.0

        end = float(audio_entry.end)
        if end <= start:
            continue

        start_i = int(start * sample_rate)
        end_i = int(end * sample_rate)
        segment = audio_data[start_i:end_i]
        librosa.output.write_wav(os.path.join(result_folder_path, audio_entry.id) + '.wav', segment, sample_rate)
    return True


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
    print('\tpython audio_split.py -j <jsonfile> -a <audiofile>')
    sys.exit(1)

if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'j:a:', ['--json', '--audio'])
    except getopt.GetoptError:
        print_usage()
    json_file = None
    audio_file = None

    for opt, arg in options:
        if opt in ('-j', '--json'):
            json_file = arg
        elif opt in ('-a', '--audio'):
            audio_file = arg

    if json_file is None or audio_file is None:
        print_usage()

    make_split(data_file=json_file, sound_file=audio_file)
