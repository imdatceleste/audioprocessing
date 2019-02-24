# -*- encoding: utf8 -*-
from __future__ import print_function
import sys
import os
import codecs
import getopt

reload(sys)
sys.setdefaultencoding('utf-8')


def usage():
    print('Usage:')
    print('\t python text_sound_file_checker.py -i <meta_file> -w <wavs_dir>')
    sys.exit(1)


def cleanup_metadata(lines, wavsdir):
    done_lines = []
    print('Checking files... ')
    sys.stdout.flush()
    exist = 0
    for fname in lines:
        orig_name = os.path.join(wavsdir, fname)
        if os.path.isfile(orig_name):
            exist += 1
            if fname in done_lines:
                print('Duplicate {}'.format(fname))
            else:
                done_lines.append(fname)
        else:
            print('Filename not exist: {}'.format(fname))

    print('Done: {} from {}'.format(exist, len(lines)))


if __name__ == '__main__':
    infile = None
    wavsdir = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:w:', ['infile', 'wavs_dir'])
    except getopt.GetoptError:
        usage()

    for opt, args in opts:
        if opt in ('-i', '--infile'):
            infile = args
        elif opt in ('-w', '--wavs_dir'):
            wavsdir = args

    if infile is None or wavsdir is None:
        usage()
        exit(1)
    else:
        orig_lines = codecs.open(infile, 'r', 'utf-8').readlines()
        lines = []
        filenames = []
        for one_line in orig_lines:
            if u'|' in one_line:
                try:
                    filename, orig_transcription = one_line.split('|')
                    filenames.append(filename)
                except:
                    print('line error: {}'.format(one_line))
                    filename, orig_transcription, _ = one_line.split('|')
            else:
                print('Format error in line: {}'.format(one_line))
        cleanup_metadata(filenames, wavsdir)