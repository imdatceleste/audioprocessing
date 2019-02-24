from __future__ import print_function, unicode_literals
import getopt
import os
import sys
import subprocess
from progressbar import ProgressBar, Percentage, Bar, ETA, FormatLabel, AnimatedMarker

reload(sys)
sys.setdefaultencoding('utf8')


def create_result_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def convert_audio(source_dir, dest_dir):
    destination_folder = dest_dir
    if dest_dir is None:
        destination_folder = os.path.join(source_dir, 'converted_audio')
        destination_folder = create_result_folder(destination_folder)

    allfiles = os.listdir(source_dir)
    all_audios = list()
    for file_item in allfiles:
        if file_item.endswith('.mp3') or file_item.endswith('.wav'):
            all_audios.append(file_item)

    widgets = [FormatLabel('Convert audio: %(message)s [%(value)s/' + str(len(all_audios)) + ']'), ' ', Percentage(), ' ', Bar(marker='@', left='[', right=']'), ' ', ETA()]
    pBar = ProgressBar(widgets=widgets, maxval=len(all_audios)).start()

    for idx, audio_file in enumerate(all_audios):
        pBar.update(value=idx, message=audio_file)
        audio_file_path = os.path.join(source_dir, audio_file)
        result_audio_fname = os.path.os.path.basename(os.path.splitext(audio_file)[0]) + '.wav'
        output_audio_file = os.path.join(destination_folder, result_audio_fname)
        command = 'sox {} -r 22050 {} channels 1'.format(audio_file_path, output_audio_file)
        result = subprocess.check_call(command, shell=True)
        if result != 0:
            print('Can\'t convert file: {}'.format(audio_file))
            pBar.finish()
            return False
    pBar.finish()
    return True


def print_usage():
    print('Usage:')
    print('\tpython sentence tokeniser.py -s <source_folder> -d <destination folder>. It will make 22050kHZ single channel wav files from input audio')
    sys.exit(1)


if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 's:d:', ['--source_folder', '--destination_folder'])
    except getopt.GetoptError:
        print_usage()

    source = None
    dest = None
    for opt, arg in options:
        if opt in ('-s', '--source_folder'):
            source = arg
        if opt in ('-d', '--destination_folder'):
            dest = arg

    if source is None:
        print_usage()

    convert_audio(source_dir=source, dest_dir=dest)
