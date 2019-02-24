# -*- encoding: utf8 -*-
from __future__ import print_function
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import codecs
import re
import random
import getopt
import json
from text import normalize_numbers, transliterate_text

fname = re.compile(r'_[0-9][0-9]_f[0-9][0-9][0-9][0-9][0-9][0-9]\.wav')


def usage():
    print('Usage:')
    print('\t python finalize_data.py -i <meta_file> -l <language> [-s -w <wavsdir>]')
    sys.exit(1)


def shuffle_files(lines, wavsdir):
    retlines = []
    print('Shuffling data... ', end='')
    sys.stdout.flush()
    random.shuffle(lines)
    for i, line in enumerate(lines):
        line = line.strip()
        if u'|' in line:
            try:
                filename, transcription = line.split('|')
            except:
                print('hello')
            orig_name = os.path.join(wavsdir, filename)
            if os.path.exists(orig_name):
                m = fname.search(filename)
                out_f = filename[:m.span()[0]] + '_s{:06d}'.format(i+1) + '.wav'
                retlines.append(u'{}|{}'.format(out_f, transcription))
                new_name= os.path.join(wavsdir, out_f)
                os.rename(orig_name, new_name)
    print('done')
    return retlines


if __name__ == '__main__':
    infile = None
    wavsdir = None
    language = None
    do_shuffle = False
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:w:l:s', ['infile', 'wavs', 'language', 'shuffle'])
    except getopt.GetoptError:
        usage()

    for opt, args in opts:
        if opt in ('-i', '--infile'):
            infile = args
        elif opt in ('-w', '--wavs'):
            wavsdir = args
        elif opt in ('-l', '--language'):
            language = args
        elif opt in ('-s', '--shuffle'):
            do_shuffle = True

    if infile is None or (wavsdir is None and do_shuffle) or language is None:
        usage()
    else:
        print('META: {}'.format(infile))
        if do_shuffle:
            print()
            print('**** WARNING **** WARNING **** WARNING **** WARNING **** WARNING **** WARNING **** WARNING ****')
            print()
            s = 'n'
            while s != 'y':
                s = raw_input('\a******* WARNING: All changes will be made INPLACE. Are you sure you want to continue (y/n)? ')
                if s  != 'n' and s != 'y':
                    print('ERR: Please say \'y\' or \'n\'')
                elif s == 'n':
                    sys.exit(0)

            s = 'n'
            while s != 'y':
                s = raw_input('\a******* DO YOU HAVE YOUR BACKUPS (y/n)? ')
                if s  != 'n' and s != 'y':
                    print('ERR: Please say \'y\' or \'n\'')
                elif s == 'n':
                    sys.exit(0)

            s = 'n'
            while s != 'y':
                s = raw_input('\a******* LAST CHANCE. ARE YOU ABSOLUTELY SURE (y/n)? ')
                if s  != 'n' and s != 'y':
                    print('ERR: Please say \'y\' or \'n\'')
                elif s == 'n':
                    sys.exit(0)

        orig_lines = codecs.open(infile, 'r', 'utf-8').readlines()
        lines = []
        for a in orig_lines:
            lines.append(a.strip())
        if do_shuffle:
            lines = shuffle_files(lines, wavsdir)
        print('Transliterating & normalizing... ', end='')
        sys.stdout.flush()
        out_lines = []
        mls_lines = {}
        for i,line in enumerate(lines):
            if u'|' in line:
                try:
                    filename, orig_transcription = line.split('|')
                except:
                    filename, orig_transcription, _ = line.split('|')
                transcription = transliterate_text(orig_transcription, language)
                transcription = normalize_numbers(transcription, language)
                mls_lines[filename] = {'original': unicode(orig_transcription), 'clean': unicode(transcription)}
                ljspeech_f = filename.replace('.wav', '')
                out_lines.append(u'{}|{}|{}'.format(ljspeech_f, orig_transcription, transcription))

        ljspeech = codecs.open(os.path.join(os.path.dirname(infile), 'metadata.csv'), 'w', 'utf-8')
        for l in out_lines:
            print(l, file=ljspeech)
        ljspeech.close()
        json.dump(mls_lines, codecs.open(os.path.join(os.path.dirname(infile), 'metadata_mls.json'), 'w', 'utf-8'), indent=4)
        print('done')
