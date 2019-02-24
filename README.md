# Training Data Preparation, Transcription & QA

## 1. Train Data Splitting
The audio splitter ``split_voice.py`` is used to split long mp3 or wav files into smaller segments. The splitting happens at pauses, ignoring breathing and so on (it is actually quite ingenious way :-)

### Dependencies
You will need the following packages installed before you can train a model using this code. Other required packages will be installed with these packages because of the dependencies.

```
 * pydub==1.4.0
 * getopt==0.20.0
```
You can install packages requirements through 'pip' like:  
```
pip install pydub
```


### Usage

```
Usage:
$ python split_voice.py -d <my-directory-full-of-mp3-or-wav-files> | -f <my-file-to-be-split>

         -f --file           <file-name>                    File name to be cleaned
         -d --dir            <top-directory>                Directory that contains the files to be converted. It does not traverse sub-directories
         -s --silence        <silence-threshold>            Below this number chunk is defined as silence,default=-40
         -x --max            <maximum-chunk-length>         Maximum chunks length in seconds after conversion,default=20sec
         -m --min            <minimum-silence-length>       Minimum silence length between the chunks to split the file,default=0 msec
         -r --samplerate     <sampling-rate>                Sample rate of the files to be outputted
         -g --gain           <apply-gain>                   Increase amplitude of the audio chunks as decibel,default=0 (+, - must be given)
```
The result is in a directory called ``audio_segments`` in either the ``<my-directory...>`` or on the parent directory of the ``<my-file...>``

All the output is logged on the console and into a text file in the runtime directory  and ``log`` subdirectory. 

### Parameters
* Usage is quite simple. You either have a folder containing lots of files (-d option) or you use it one a single file (-f) to be split.

*  Silence threshold (-s) is used for to separate the voice activity from the silence. Decibel metric is used. The value should be specified with (-) sign. This value is used just at the beginning to create the voice activity tuples. Then the  minimum decibel value of the voice activity tuples are found and this value is set with a small buffer as the new silence threshold.

*  This tool supports mp3 and wav file formats

*  If the audio file is formatted as stereo, then it is automatically converted to mono format

*  -m option significates the minimum silence length between audio segment tuples. The tool is try to merge them until it reaches to the minimum silence length value. Default valu is zero seconds. 

*  -x option significates maximim audio chunk size. Audio file is splitted until  this value is reached. Default value is 1000 miliseconds.  

*  if both -x and -m value are set or both of them are not set, then the audio file is splitted according to maximim audio chunk size's default value.

*  -g option increases or decreases audio chunks' amplitudes in decibel value. Value can be set with (+) or (-) sign. 

*  -r option sets the audio chunk's bit rate. If no value is specified then the bitrate value of the original audio file is used.

_Note: In python 2, when the big sized, stereo and mp3 formatted audio file is converted to mono format, an overflow error raises. This error can be bypassed either using python 3.x or converting the file externally from stereo to the mono format._


## 2. Train Data Transcription QA

This project is meant for performing QA on training data.

### Approach
First we retrieve some audio-books (public-domain) and their textual representation.

The audio-books are then cut in small segments (8-12 seconds each). You can have one folder per chapter or all segments in one folder, it doesn't matter.

Next we clean the textual version of the audio-book. Please remove any text that *does not exist in the audio*.

This textual representation is then stored as plain-text, UTF-8 encoded file.

### Google
Next, we run the audio segments through Google's speech recognition API. For this, you use ```google.py```

    python google.py -p <path-where-segnments are> -o <transcription-json-file>

The ```google.py``` will write the transcriptions in the file mentioned in the *directory* of <path-where-segments-are>

### TRQA
You use ```trqa.py``` to QA the transcription:

    python trqa.py -j <protocol-file-from-google.py> -b <book-original-txt> -o <outfilename> [-h]

TRQA will try to do as much automatically as it can, but since the transcription may (WILL!) contain lots of errors, you need to do the QA yourself. TRQA will show you a screen and show you two lines:

* First line will show the *current* line progress, then a '|' and then the next line from the google transcription.
* Second line will show you what TRQA thinks it is in the book, then a ' | ' and then the continuation of that text.

Using '+' and '-', you can move the word-pointer. Once you think you have found the correct text, hit <ENTER> and TRQA will take it and go to the next transcription.

At any time, you can hit <q> and quit the program.

If you want to continue where you left of last time, please start TRQA with the '-h' parameter for 'history'. 

*WARNING: You must provide the same -j, -b, and -o in order to continue where you left off...*

### Alternative TRQA use
You can also start ```trqa.py``` *without* any parameters. In this case, it will ask for the JSON-File and the BOOK-file. The outfile will automatically be written to the directory where the JSON-file was with the filename ```alignments.json```

### Installation

Please check out the repository. Then you need to install the following packages:

    spacy
    nltk
    editdistance

You can do so by:

    sudo -H pip install -U spacy nltk editdistance
    python -m spacy download de

Afterwards, you will need to download the NLTK-corpi:

    bash$ python
    >>> import nltk
    >>> nltk.download()

Please choose "all" and download them.
# audioprocessing
