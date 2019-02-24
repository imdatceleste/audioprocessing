
# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import getopt
import codecs
import json
import shutil
from progressbar import ProgressBar, Percentage, Bar, ETA, FormatLabel, AnimatedMarker

def copy_files(filelist, destination):
    for fname in filelist:
        shutil.copyfile(fname, os.path.join(destination, os.path.basename(fname)))


def missing_files(proto_in_file, audio_files):
    protocol = json.load(codecs.open(proto_in_file, 'r', 'utf-8'))
    result = []
    checklist = []
    for entry in protocol:
        checklist.append(os.path.basename(entry.keys()[0]))
    for fname in audio_files:
        fullfname = os.path.basename(fname)
        if fullfname not in checklist:
            result.append(fname)
    return result


def main(indir, out_path):
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    audio_files = []
    for root, dirs, files in os.walk(indir):
        files.sort()
        widgets=[FormatLabel('   | File: %(message)s [%(value)s/'+str(len(files))+']'), ' ', Percentage(), ' ', Bar(marker='@', left='[', right=']'), ' ', ETA()]
        pBar = ProgressBar(widgets=widgets, maxval=len(files)).start()
        counter = 0
        acounter = 0
        proto_in_file = os.path.join(root, 'proto_in.json')
        for filename in filter(lambda filename: filename.endswith('.wav'), files):
            counter += 1
            pBar.update(counter, filename)
            filename = os.path.join(root, filename)
            audio_files.append(filename)
        result = missing_files(proto_in_file, audio_files)
    if len(result) > 0:
        copy_files(result, out_path)
    pBar.finish()


if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'p:o:', ['--path', '--out'])
    except getopt.GetoptError:
        print('Usage:')
        print('\tpython check_google.py -p <audio-path> -o <out-path>')
        sys.exit(1)
    path = None
    start_file = None
    out_path = None
    for opt, arg in options:
        if opt in ('-p', '--path'):
            path = arg
        elif opt in ('-o', '--out'):
            out_path = arg

    if path is not None and out_path is not None:
        main(path, out_path)
    else:
        print('Usage:')
        print('\tpython check_google.py -p <audio-path> -o <out-path>')
        sys.exit(1)
