# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import getopt
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the REST API for async
batch processing.

Example usage:
    python transcribe_async.py resources/audio.raw
    python transcribe_async.py gs://cloud-samples-tests/speech/vr.flac
"""

import io
import codecs
import json
from progressbar import ProgressBar, Percentage, Bar, ETA, FormatLabel, AnimatedMarker


def transcribe_file(speech_file, context_text=None, language='de-DE'):
    """Transcribe the given audio file asynchronously."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()
    audio = types.RecognitionAudio(content=content)
    if context_text is not None:
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            max_alternatives=2,
            speech_contexts=[speech.types.SpeechContext(phrases=context_text)],
            language_code=language)
    else:
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            max_alternatives=2,
            language_code=language)
    operation = client.long_running_recognize(config, audio)
    response = operation.result(timeout=90)
    final_result = []
    for result in response.results:
        for alternative in result.alternatives:
            final_result.append((alternative.transcript, alternative.confidence))
    return final_result


def transcribe_files(indir, protocol_file, missing_files, previous_protocol=None, context_file=None, language='de-DE'):
    text_all = None
    if previous_protocol is not None:
        output_protocol = previous_protocol
    else:
        output_protocol = {}
    if context_file is not None:
        text_lines = codecs.open(context_file, 'r', 'utf-8').readlines()
        text_all = ' '.join(text_lines).replace('\n', ' ')
    widgets=[FormatLabel('        File: %(message)s [%(value)s/'+str(len(missing_files))+']'), ' ', Percentage(), ' ', Bar(marker='@', left='[', right=']'), ' ', ETA()]
    pBar = ProgressBar(widgets=widgets, maxval=len(missing_files)).start()
    counter = 0
    for counter, filename in enumerate(missing_files):
        fname_only = os.path.basename(filename)
        pBar.update(counter, fname_only)
        filename = os.path.join(indir, fname_only)
        transcription = transcribe_file(filename, text_all, language)
        if len(transcription)>0:
            output_protocol[fname_only] = transcription[0][0]
        else:
            output_protocol[fname_only] = '__ERROR__'
        json.dump(output_protocol, codecs.open(protocol_file, 'w', 'utf-8'), indent=4)
    pBar.finish()


def convert_protocol(protocol):
    tmp_res = protocol
    if protocol is not None:
        if not isinstance(protocol, dict):
            result = {}
            for entry in protocol:
                key = entry.keys()[0]
                value = entry[key]
                transc = value[0].keys()[0]
                result[key] = transc
            converted = True
    result = {}
    for key in tmp_res.keys():
        value = tmp_res[key]
        key = os.path.basename(key)
        result[key] = value
    return result


def check_missing_files(protocol, audio_files):
    result = []
    checklist = []
    if protocol is not None:
        for fname in protocol.keys():
            checklist.append(os.path.basename(fname))
        for fname in audio_files:
            filename_only = os.path.basename(fname)
            if filename_only not in checklist:
                result.append(fname)
    else:
        result = audio_files
    return result


def main(indir, protocol_file, context_file, language):
    audio_files = []
    missing_files = []
    proto_path = os.path.join(indir, protocol_file)
    if os.path.exists(proto_path):
        protocol = json.load(codecs.open(proto_path, 'r', 'utf-8'))
    else:
        protocol = None
    if protocol is not None:
        protocol = convert_protocol(protocol)
        json.dump(protocol, codecs.open(proto_path, 'w', 'utf-8'), indent=4)
    for root, dirs, files in os.walk(indir):
        files.sort()
        counter = 0
        acounter = 0
        for filename in filter(lambda filename: filename.endswith('.wav'), files):
            filename = os.path.join(root, filename)
            audio_files.append(filename)
        missing_files = check_missing_files(protocol, audio_files)
    if len(missing_files) > 0:
        transcribe_files(indir, proto_path, missing_files, protocol, context_file, language)
        print('Done\n')
    else:
        print('All done in this directory, nothing to do there anymore...')


if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'p:c:l:', ['--path', '--context', '--language'])
    except getopt.GetoptError:
        print('Usage:')
        print('\tpython google.py -p <audio-path> [-c <contextfile>] [-l <language>]')
        print('\t\t Language is something like: de_DE, en_US, tr_TR, (with underscore)...')
        sys.exit(1)

    path = None
    context_file = None
    language = 'de-DE'
    proto_file_name = 'proto_in.json'
    for opt, arg in options:
        if opt in ('-p', '--path'):
            path = arg
        elif opt in ('-c', '--context'):
            context_file = arg
        elif opt in ('-l', '--language'):
            language = arg.replace('_', '-')

    if path is not None:
        print('Working on project: {}'.format(path))
        main(path, proto_file_name, context_file, language)
    else:
        print('Usage:')
        print('\tpython google.py -p <audio-path> [-c <contextfile>] [-l <language>]')
        print('\t\t Language is something like: de_DE, en_US, tr_TR, (with underscore)...')
        sys.exit(1)
