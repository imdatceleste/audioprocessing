# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import os
import re
import time
import getopt
import logging
from pydub import AudioSegment, silence
from pydub.playback import play
from utils.utils import configure_logger
from progressbar import ProgressBar, Percentage, Bar, ETA, FormatLabel, AnimatedMarker

logger = logging.getLogger(os.path.basename(sys.argv[0]))

"""
Sound Audio File Trimmer

Copyright (c) 2018 Munich Artificial Intelligence Laboratories GmbH (M-AILABS)

Created: 2018-01-16 ??:?? CET, KA

These class finds the voice activitiy of an audio, trims the tag-ends and silents

"""
splitter = re.compile(r'(\d+)')


class SoundDetector(object):
    def __init__(self, sound, minAudioLength=0, samplerate=16000, chunk_size=10, silence_threshold=-30, filePath=None, silence_length=100, audioFormat='wav'):
        self.sound = sound
        self.samplerate = samplerate
        self.chunk_size = chunk_size
        self.silence_threshold = silence_threshold
        self.minAudioLength = minAudioLength
        self.filePath = filePath
        self.start = 0
        self.minSilenceLength = 300
        self.audioFormat = audioFormat
        self.silence_length = silence_length

    def writeFile(self, sound):
        """
        Writes the audio to the disk

        Params:
            sound: audio segment
        Returns:
        """
        top_directory = os.path.dirname(self.filePath)
        audioPath = os.path.join(top_directory, "trimmed")
        if not os.path.exists(audioPath):
            os.makedirs(audioPath)
        name = os.path.basename(self.filePath).split('.')[0] + '.wav'
        audioPath = os.path.join(audioPath, name)
        # Create the directory where the file segments to be written
        sound = sound.set_frame_rate(self.samplerate)
        sound.export(audioPath, format='wav')
        return True

    def addSilenceToSound(self, sound):
        """
        Add 500 msec silence to the beginning and end of the audio

        Params:
            sound: audio segment
        Returns:
            sound: audio segment
        """
        second_of_silence = AudioSegment.silent(duration=self.silence_length)
        sound = second_of_silence + sound + second_of_silence
        return sound

    def checkSoundLength(self, soundTuple):
        """
        Controls the sound part if it is greater than minimum audio length

        Params:
            soundTuple is a tuple keeping the beginning and end of the audio part
        Returns:
            trim is True if the sound tuple is less than the minimum audio length
        """
        trim = False

        length = soundTuple[1] - soundTuple[0]
        if length < self.minAudioLength:
            trim = True
        return trim

    def createChunks(self, soundList):
        """
        Iterate over sound tuples to merge the voice segments of which lengths are less than minsilence length

        Params:
            soundList list that has voice begin end tuples
        Returns:
            newSoundList merged list
        """
        newSoundList = []
        data_start = soundList[0][0]
        data_end = soundList[0][1]
        for i in range(len(soundList) - 1):
            first = soundList[i][1]
            last = soundList[i + 1][0]
            if (last - first) < self.minSilenceLength:
                data_end = soundList[i + 1][1]
            else:
                newSoundList.append((data_start, data_end))
                data_start = soundList[i + 1][0]
                data_end = soundList[i + 1][1]
        if (data_end - data_start) > 0:
            newSoundList.append((data_start, data_end))
        return newSoundList

    def findChuncks(self):
        """
        Receive the audio, finds the voice segments, merge the voice segments and trims accordingly

        Returns True if it is succesful
        """
        global logger

        # Find audio segments which has silence threshold greater than the given
        soundList = []
        counter = 0
        while (self.start + self.chunk_size) <= len(self.sound):
            if self.sound[self.start:self.start + self.chunk_size].dBFS >= self.silence_threshold:
                temp = self.start
                while self.sound[self.start:self.start + self.chunk_size].dBFS >= self.silence_threshold:
                    self.start += self.chunk_size
                soundList.append((temp, self.start))
                counter += 1
            self.start += self.chunk_size
        # Create new sound chunks that has between each other minimum silence length
        if soundList:
            soundList = self.createChunks(soundList)
            # Remove trimmings
            trimBegin = False
            trimEnd = False
            if len(soundList) == 0:
                logger.info('FOR THE FILE {} THERE IS NO VALID SOUND'.format(os.path.basename(self.filePath)))
                return False
            elif len(soundList) == 1:
                trimBegin = self.checkSoundLength(soundList[0])
                if trimBegin:
                    logger.info('FOR THE FILE {} THERE IS ONLY ONE AUDIO PART and IT is NOT VALID'.format(os.path.basename(self.filePath)))
                    return False
            elif len(soundList) >= 2:
                trimBegin = self.checkSoundLength(soundList[0])
                if trimBegin:
                    logger.info('FOR THE FILE {} THE BEGINNING PART IS TRIMMED'.format(os.path.basename(self.filePath)))
                    soundList = soundList[1:]
                trimEnd = self.checkSoundLength(soundList[len(soundList) - 1])
                if trimEnd:
                    logger.info('FOR THE FILE {} THE END PART IS TRIMMED'.format(os.path.basename(self.filePath)))
                    soundList = soundList[:-1]
                if len(soundList) == 0:
                    logger.info('FOR THE FILE {} ALL THE AUDIO IS TRIMMED'.format(os.path.basename(self.filePath)))
                    return False

            data_start = soundList[0][0]
            data_end = soundList[len(soundList) - 1][1]
            self.sound = self.addSilenceToSound(self.sound[data_start:data_end])
            # play(sound)
            _ = self.writeFile(self.sound)
        else:
            logger.info('THE FILE {} IS EMPTY'.format(os.path.basename(self.filePath)))
            return False
        return True


def segmentAudioFile(fileName, minAudioLength, silence_threshold, silence_length):
    """
    Receive an audio file, converts to AudioSegment if it is stereo and call trimming class

    Params:
        filename(str): file name's path to be segmented
    """
    global logger

    formats = {'.wav': 'wav', '.mp3': 'mp3', '.m4a': 'm4a'}

    names = os.path.splitext(fileName)
    audioFormat = formats.get(names[1], None)
    if audioFormat is not None:
        basename = os.path.basename(fileName)
        # Read sound
        sound = AudioSegment.from_file(fileName, format=audioFormat)
        if sound.channels == 2:  # Stereo to mono conversion - this step is working with wav file or python 3
            logger.info('CONVERTING FILE:{} from STEREO to MONO'.format(basename))
            sound = sound.set_channels(1)  # Convert to mono
        # If sample rate is not set explicitly than take the audio's default sampling rate
        samplerate = sound.frame_rate
        # Create sound management object
        soundObject = SoundDetector(sound, minAudioLength=minAudioLength, silence_threshold=silence_threshold, filePath=fileName, silence_length=silence_length, audioFormat=audioFormat)
        _ = soundObject.findChuncks()
        soundObject = None
        return True
    else:
        return False


def usage():
    print('Usage:')
    print('split_voice.py <-f <filename> | -d <top-dir> > [-t <traverse-subdirectories>] [-m <min-audio-length>] [-l <silence-length>] [-s <sil-th>]')
    print('\t-f --file           <file-name>                    File name to be cleaned')
    print('\t-d --dir            <top-directory>                Directory that contains the files to be converted. In default mode does not traverse sub-directories')
    print('\t-t --traverse       <traverse=directories>         Traverse whole subdirectories,default=False')
    print('\t-m --min            <minimum-audio-length>         Minimum audio length that keeps the audio not trimmed,default=100msec')
    print('\t-l --sl             <silence-length>               Silence length that is added to the beginning and end of the audio file,default=500msec')
    print('\t-s --silence        <silence-threshold>            Below this number defined as silence,default=-40')
    print()
    sys.exit(1)


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    global splitter
    return [atoi(c) for c in re.split('(\d+)', text)]


#    return [atoi(c) for c in splitter.split( text)]


def getfiles(dirpath):
    a = [s for s in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, s))]
    a.sort(key=natural_keys)
    return a


def main(fileName, top_directory, minAudioLength, silence_threshold, traverse, silence_length):
    # Create log directory and configure logging
    work_on_single_file = fileName is not None
    if work_on_single_file and not os.path.exists(fileName):
        print('Could not find the audio-file {}.'.format(fileName))
        usage()
    # Configure logger
    logPath = os.path.join(os.getcwd(), 'log')
    if not os.path.exists(logPath):
        os.makedirs(logPath)
    configure_logger(logFileName=os.path.join(logPath, 'trimming.log'))
    # Check if the file exists in the data directory
    if work_on_single_file:
        _ = segmentAudioFile(fileName, minAudioLength=minAudioLength, silence_threshold=silence_threshold, silence_length=silence_length)
    else:
        fullFilePaths = []
        if traverse:
            for root, dirs, files in os.walk(top_directory):
                files.sort()
                for fileName in filter(lambda fileName: fileName.endswith('.wav') or fileName.endswith('.mp3') or fileName.endswith('.m4a'), files):
                    filePath = os.path.join(root, fileName)
                    fullFilePaths.append(filePath)
        else:
            fileList = getfiles(top_directory)
            # Create the directory where the file segments to be written
            for fileName in filter(lambda fileName: fileName.endswith('.wav') or fileName.endswith('.mp3') or fileName.endswith('.m4a'), fileList):
                filePath = os.path.join(top_directory, fileName)
                fullFilePaths.append(filePath)
        # Process the files
        if fullFilePaths:
            widgets = ['Trimming files: ', Percentage(), ' ', Bar(marker='#', left='[', right=']'), ' ', ETA()]
            pBar = ProgressBar(widgets=widgets, maxval=len(fullFilePaths)).start()
            for i in range(len(fullFilePaths)):
                _ = segmentAudioFile(fullFilePaths[i], minAudioLength=minAudioLength, silence_threshold=silence_threshold, silence_length=silence_length)
                pBar.update(i)
            pBar.finish()
        else:
            print("No files found to be processed!")


if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'f:m:s:d:tl:', ['file=', 'min=', 'silence=', 'dir=', 'traverse', 'sl='])
    except getopt.GetoptError:
        usage()

    fileName = None
    top_directory = None
    minAudioLength = 100
    silence_threshold = -40
    traverse = False
    silence_length = 500

    for opt, arg in options:
        if opt in ['-f', '--file']:
            fileName = arg
        elif opt in ['-d', '--dir']:
            top_directory = arg
        elif opt in ['-m', '--min']:
            minAudioLength = int(arg)
        elif opt in ['-l', '--sl']:
            silence_length = int(arg)
        elif opt in ['-s', '--silence']:
            silence_threshold = int(arg)
        elif opt in ['-t', '--traverse']:
            traverse = True

    if not fileName and not top_directory:
        print('Please provide either a top-directory with the \'-d\' or a file with \'-f\'')
        usage()
    main(fileName, top_directory, minAudioLength, silence_threshold, traverse, silence_length)

