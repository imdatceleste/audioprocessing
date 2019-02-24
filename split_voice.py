# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import os
import re
import time
import getopt
import logging
import codecs
from pydub import AudioSegment, silence
from pydub.playback import play
from utils import convertMilliseconsTime, configure_logger
logger = logging.getLogger(__name__)
"""
Sound Audio File Splitter

Copyright (c) 2017 Munich Artificial Intelligence Laboratories GmbH (M-AILABS)

Created: 2017-12-20 ??:?? CET, KA

These class finds the voice activitiy of an audio and writes the audio segments to the disk

"""
splitter = re.compile(r'(\d+)')

class SoundDetector(object):
    def __init__(self, sound, minSilenceLength=0, samplerate=16000, maximum=20, chunk_size=10, silence_threshold=-30, gain=0, filePath=None):
        self.sound = sound
        self.samplerate = samplerate
        self.maximum = maximum * 1000
        self.chunk_size = chunk_size
        self.silence_threshold = silence_threshold
        self.minSilenceLength = minSilenceLength
        self.gain = gain
        self.filePath = filePath
        self.noFiles = 0
        self.start = 0
        self.minSilenceLengthThreshold=150

    def writeChunk(self, chunks):
        """
        Writes the audio chunks to the disk
        
        Params:
            chunks: audio segment
        Returns:
            noFiles: returns number of files to be written
        """
        top_directory = os.path.dirname(self.filePath)
        # Create the directory where the file segments to be written
        audioPath = os.path.join(top_directory, 'audio_segments')
        audioPath = os.path.join(audioPath, os.path.basename(self.filePath).split('.')[0])
        if not os.path.exists(audioPath):
            os.makedirs(audioPath)
        duration = 0
        # If the chunk less than 250msec and dBFS is less than 30dB then it is most probably a breeze and no need to write it
        for i in range(len(chunks)):
            if len(chunks[i])<500 and chunks[i].dBFS<-30:
                continue
            # play(chunks[i])
            names = os.path.basename(self.filePath).split('.') 
            path = names[0] + '-%006d.wav' % (self.noFiles,)
            path = os.path.join(audioPath, path)
            chunks[i] = chunks[i].set_frame_rate(self.samplerate)
            chunks[i].export(path, format="wav")
            duration += len(chunks[i])
            self.noFiles += 1
        return self.noFiles, duration

    def applyGainToAudio(self, chunks, gain):
        """ 
        Change the amplitude (generally, loudness) of the AudioSegment. Gain is specified in dB.
        
        Params:
            chunks: audio segment
            gain(int): gain levelin dB. Can be + or -
        Returns:
            gained: amplified or deamplified audio segment
        """
        gained=[]
        for i in range(len(chunks)):
            gained.append(chunks[i].apply_gain(gain))
        return gained

    def calculateSilenceThreshold(self, sound, soundList):
        """
        Iterate over sound list to calculte the minimum decibel to determine the minimum silence threshold

        Params:
            sound: audio segment
            soundList(list): that has voice begin end tuples
        Returns:
            silence_threshold (int): 
        """
        dBFSList = []
        for i in range(len(soundList)):
            dBFSList.append(sound[soundList[i][0]:soundList[i][1]].dBFS)                

        self.silence_threshold = min(dBFSList) - 3
        return True

    def getNewSoundChunks(self, soundList):
        """
        Creates a chunk list from the voice segment tuples
        """
        chunks=[]
        for i,j in soundList:
            chunks.append(self.sound[i:j])
            
        return chunks

    def calculateMinSilenceLength(self, soundList):
        """
        Iterate over sound list until the chunks are created that is suitavle to minimum 
        silence length and maximum audio size

        Params:
            soundList(list): voice segments start,end tuples
        Returns:
            chunks 
        """
        # If minimum silence length is set then merge the voice segments with that setting 
        # and return the chunks
        if self.minSilenceLength!=0:
            newSoundList = self.mergeChuncks(soundList)
            return self.getNewSoundChunks(newSoundList)

        i=0
        newSound=[]
        self.minSilenceLength=1000
        newSoundList = self.mergeChuncks(soundList)
        while i<len(newSoundList):
            # If there are still voice segments greater than maximum audio size reduce the 
            # minimum silence length and remerge the voice segments 
            if (newSoundList[i][1]-newSoundList[i][0]) > self.maximum:    
                self.minSilenceLength -= 50
                # If the minimum silence length reaches to the minimum threshold and there are 
                # still voice segments greater than maximum audio size then stop the splitting
                if self.minSilenceLength<self.minSilenceLengthThreshold:
                    self.minSilenceLength += 50
                    break
                newSoundList = self.mergeChuncks(soundList)
                i=0
                continue
            i+=1
        chunks = self.getNewSoundChunks(newSoundList)
        return chunks

    def mergeChuncks(self, soundList):
        """
        Iterate over chunks to merge the voice segments of which lengths are less than minsilence length

        Params:
            soundList list that has voice begin end tuples
        Returns:
            newSoundList merged list
        """
        newSoundList = []
        data_start = soundList[0][0]
        data_end = soundList[0][1]
        for i in range(len(soundList)-1):
            first = soundList[i][1]
            last = soundList[i+1][0]
            if (last-first)<self.minSilenceLength:
                data_end = soundList[i+1][1]
            else:
                newSoundList.append((data_start,data_end))
                data_start = soundList[i+1][0]
                data_end = soundList[i+1][1]
        if (data_end-data_start)>0:
            newSoundList.append((data_start,data_end))
        return newSoundList

    def findChuncks(self):
        """
        Receive the audio, finds the voice segments, calculates silence threshold and merge the voice segments according to  minimum silence length

        Params:
            soundList list that has voice begin end tuples
        Returns:
            newSoundList merged list
        """
        global logger

        soundList = []
        threshold_counter = 10
        counter = 0
        while (self.start+self.chunk_size)<=len(self.sound): 
            if self.sound[self.start:self.start+self.chunk_size].dBFS > self.silence_threshold:
                temp = self.start
                while self.sound[self.start:self.start+self.chunk_size].dBFS >= self.silence_threshold:
                    self.start += self.chunk_size
                soundList.append((temp, self.start))
                counter += 1
            self.start+=self.chunk_size
        # Calculate the threshold statistics
        _ = self.calculateSilenceThreshold(self.sound, soundList)
        logger.info('THE NEW SILENCE THRESHOLD:{} '.format(self.silence_threshold))
        if len(soundList)>0:
            chunks = self.calculateMinSilenceLength(soundList)
            logger.info('MINIMUM SILENCE LENGTH of this FILE is:{} '.format(self.minSilenceLength))
            chunks = self.applyGainToAudio(chunks, self.gain)
            if self.gain!=0:
                logger.info('{} GAIN APPLIED to the FILE'.format(self.gain))
            logger.info('TOTAL {} of CHUNKS were CREATED'.format(len(chunks)))
            written_files, duration = self.writeChunk(chunks)
        return written_files, duration


def segmentAudioFile(fileName, maximum=0, minSilenceLength=0, silence_threshold=0, samplerate=0, gain=0):
    """
    Receive an audio file, converts to AudioSegment sound and splits to the small segments

    Params:
        filename(str): file name's path to be segmented
    Returns:
        basename(str): base name of the file
        written_files(int): number of files to be written to the disk
    """
    global logger

    formats = {'.wav' : 'wav', '.mp3': 'mp3', '.m4a':'m4a'}

    names = os.path.splitext(fileName)
    audio_format = formats.get(names[1], None)
    if audio_format is not None:
        basename = os.path.basename(fileName)
        # Read sound
        logger.info('-' * 80)
        logger.info('READING and SPLITTING the FILE:{}'.format(basename))
        sound = AudioSegment.from_file(fileName, format=audio_format)
        if sound.channels==2: # Stereo to mono conversion - this step is working with wav file or python 3  
            logger.info('CONVERTING FILE:{} from STEREO to MONO'.format(basename))
            sound = sound.set_channels(1) # Convert to mono
        # If sample rate is not set explicitly than take the audio's default sampling rate
        if samplerate==0:
            samplerate = sound.frame_rate
        # Create sound management object
        soundObject = SoundDetector(sound, maximum=maximum, minSilenceLength=minSilenceLength, silence_threshold=silence_threshold, samplerate=samplerate, gain=gain, filePath=fileName)
        written_files, duration = soundObject.findChuncks()
        logger.info('{} FILES were WRITTEN to the DISK and the DURATION (\'hh:mm:ss\') is: {}'.format(written_files, convertMilliseconsTime(duration)))
        soundObject = None
        return duration
    else:
        return None


def usage():
    print('Usage:')
    print('split_voice.py <-f <filename> | -d <top-dir> > [-m <min-sil-length>] [-x <max-sil-length>] [-s <sil-th>] [-g <gain>]')
    print('\t-f --file           <file-name>                    File name to be cleaned')
    print('\t-d --dir            <top-directory>                Directory that contains the files to be converted. It does not traverse sub-directories')
    print('\t-x --max            <maximum-chunk-length>         Maximum chunks length in seconds,default=20sec')
    print('\t-m --min            <minimum-silence-length>       Minimum silence length to split the file,default=1000msec')
    print('\t-s --silenc         <silence-threshold>            Below this number defined as silence,default=-30')
    print('\t-r --samplerate     <sampling-rate>                Sample rate of the files to be outputted,default=16000')
    print('\t-g --gain           <apply-gain>                   Increase amplitude of the audio chunks as decibel,default=0 (+, - must be given)')
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


def main(fileName, top_directory, maxmimum, minSilenceLength, silence_threshold, samplerate, gain):
    # Create log directory and configure logging
    duration = 0
    work_on_single_file = fileName is not None
    if work_on_single_file and not os.path.exists(fileName):
        print('Could not find the audio-file {}.'.format(fileName))
        usage()
    if maximum < 10 or maximum > 23:
        print('Audio duration should be between 5 and 20 seconds!')
        usage()
    if minSilenceLength > 0 and (minSilenceLength > 1000 or minSilenceLength < 150):
        print('Minimum silence length value should be between 150msec and 1000msec!')
        usage()
    if samplerate > 0 and (samplerate > 44100 or samplerate < 16000):
        print('Sample rate should be between 16000 and 44100')
        usage()

    logPath = os.path.join(os.getcwd(), 'log')
    if not os.path.exists(logPath):
        os.makedirs(logPath)
    configure_logger(logFileName=os.path.join(logPath, 'vlog.log'))

    # Check if the file exists in the data directory
    if work_on_single_file:
        duration = segmentAudioFile(fileName, maximum=maximum, minSilenceLength=minSilenceLength, silence_threshold=silence_threshold, samplerate=samplerate, gain=gain)
        logger.info('-' * 80)
        logger.info('TOTAL DURATION of the FILES is {} '.format(duration))
    else:
        fileList = getfiles(top_directory)
        # Create the directory where the file segments to be written
        for fileName in filter(lambda fileName: fileName.endswith('.wav') or fileName.endswith('.mp3'), fileList):
            filePath = os.path.join(top_directory, fileName)
            temp_duration = segmentAudioFile(filePath, maximum=maximum, minSilenceLength=minSilenceLength, silence_threshold=silence_threshold, samplerate=samplerate, gain=gain)
            if temp_duration is not None:
                duration += temp_duration
            else:
                break
        logger.info('-' * 80)
        logger.info('TOTAL DURATION of the FILES is \'hh:mm:ss\' {} '.format(convertMilliseconsTime(duration)))


if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 'f:x:m:s:r:g:d:', ['file=', 'max=', 'min=', 'silence=', 'samplerate=', 'gain=', 'dir='])
    except getopt.GetoptError:
        usage()
    fileName = None
    top_directory = None
    maximum = 20
    minSilenceLength = 0
    silence_threshold = -40
    samplerate = 0
    gain =  0
    for opt, arg in options:
        if opt in ['-f', '--file']:
            fileName = arg
        elif opt in ['-d', '--dir']:
            top_directory = arg
        elif opt in ['-x', '--max']:
            maximum = int(arg)
        elif opt in ['-m', '--min']:
            minSilenceLength = int(arg)
        elif opt in ['-s', '--silence']:
            silence_threshold = int(arg)
        elif opt in ['-r', '--samplerate']:
            samplerate = int(arg)
        elif opt in ['-g', '--gain']:
            gain = int(arg)

    if not fileName and not top_directory:
        print('Please provide either a top-directory with the \'-d\' or a file with \'-f\'')
        usage()
    main(fileName, top_directory, maximum, minSilenceLength, silence_threshold, samplerate, gain)

