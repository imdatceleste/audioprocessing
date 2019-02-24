from __future__ import print_function, unicode_literals
import sys

reload(sys)
sys.setdefaultencoding('utf8')
import codecs
import getopt
import json
import os

from sentence_tokeniser import tokenise
from chapter_splitter import split_text
from audio_decoder import convert_audio
from aeneas.tools.execute_task import ExecuteTaskCLI
from audio_splitter import make_split
from json_to_cv import transform_all_jsons
from trim_audio_tagends import main as trim_audio_files
from progressbar import ProgressBar, Percentage, Bar, ETA, FormatLabel, AnimatedMarker

try:
    from tkinter import *
    from tkinter import filedialog
except:
    from Tkinter import *
    import tkFileDialog as filedialog

languages = {'german': 'deu',
             'french': 'fra',
             'spanish': 'spa',
             'english': 'eng',
             'turkish': 'tur',
             'italian': 'ita',
             'ukr': 'ukr',
             'pol': 'pol',
             'fra': 'fra'}

last_path = '~'


def get_path_tk(title, file_type_desc, is_directory=False, initial_dir=last_path, exit_if_none=False):
    global last_path
    root = Tk()
    root.withdraw()
    root.update()
    if is_directory:
        filename = filedialog.askdirectory(initialdir=initial_dir, title=title)
    else:
        filename = filedialog.askopenfilename(initialdir=initial_dir, title=title, filetypes=(file_type_desc,))
    root.update()
    root.destroy()
    del root
    if filename is not None and len(filename) == 0:
        filename = None
        if exit_if_none:
            print('Next time choose better')
            exit(1)
    last_path = os.path.dirname(filename)
    return filename


def ask_for_language():
    lang_str = 'Choose language: | '
    lang_list = list(languages.keys())
    for idx, lang_name in enumerate(lang_list):
        lang_str += ' {} - {} |'.format(lang_name, idx)
    print(lang_str)
    response = raw_input("Please enter your decision: ")
    try:
        result = int(response)
    except ValueError:
        print("That's not an correct choise")
        result = 0

    if result not in range(0, 8):
        result = 0
    return lang_list[result]


def set_proper_filename_id(json_filepath, filename_prefix):
    aeneas_json = json.load(codecs.open(json_filepath, 'r', 'utf-8'))
    for entry in aeneas_json['fragments']:
        s_key = entry['id']
        s_key = filename_prefix + '_' + s_key
        entry['id'] = s_key
    json.dump(aeneas_json, codecs.open(json_filepath, 'w', 'utf-8'), indent=4)


def ask_user_for_action():
    print('What would you like to do:')
    print('\t1 - Tokenise book file')
    print('\t2 - Start second stage')
    print('\t3 - Split book for chapters')
    print('\t4 - Start aeneas only')
    print('\t5 - Split audio')
    print('\t6 - Cleanup splitted audios')
    print('\t7 - Make final files arrangement')
    print('\n')
    print('\t0 - Nothing. Just leave me alone')
    response = raw_input("Please enter your decision: ")

    try:
        result = int(response)
    except ValueError:
        print("That's not an correct choise")
        result = 0

    if result not in range(0, 8):
        result = 0

    return result


def find_book_in_folder(path):
    text_file = None
    allfiles = os.listdir(path)
    for item in allfiles:
        if item.endswith('.txt'):
            text_file = os.path.join(path, item)
    return text_file


def get_text_and_audiofiles(folder_path):
    audio = list()
    texts = list()
    allitems = os.listdir(folder_path)
    for file_item in allitems:
        item_path = os.path.join(folder_path, file_item)
        if item_path.endswith('.mp3') or file_item.endswith('.wav'):
            audio.append(item_path)
        elif item_path.endswith('.txt'):
            texts.append(item_path)

    audio.sort()
    texts.sort()

    if len(audio) != len(texts):
        print('ERROR! Aeneas files finder. Worng amount of audio/text files. Should be equal')
        return None, None
    return audio, texts


def get_all_json_files(folder_path):
    result = list()
    allitems = os.listdir(folder_path)
    for file_item in allitems:
        item_path = os.path.join(folder_path, file_item)
        if item_path.endswith('.json'):
            result.append(item_path)
    result.sort()
    return result


def run_pipeline(step=0, language=None, book_text_file=None, stage_source_dir=None, audio_dest_folder=None, split_word=None):
    # you define start step - all the next will be done automatically (if current step is finished without error)
    # for each step needed parameters is described

    if step == 0:  # tokenise sentences. needs: book filepath, language
        if book_text_file is not None:
            if os.path.exists(book_text_file):
                tokenise(data_file=book_text_file, language=language, sen_max_len=260)
            else:
                print('Wrong book file path')
                return False

    else:
        run_process_from_step(stage_step=step, stage_source_dir=stage_source_dir, dest_dir=audio_dest_folder, split_word=split_word, language=language)

    # step == 1:  # split book for chapters. needs: book folder, language
    # step == 2:  # audio convert. needs: audio folder, audioe destination folder, language
    # step == 3:  # run aeneas. needs: book chapters folder, language
    # step == 4:  # split audio. uses aenear result json files. needs: book chapters folder (there should be audiofiles and json files)
    # step == 5:  # collect all audio into one foolder and all metadata from json into 1 .txt file.
    # needs: book chapters folder (there should be folders with cut audiofiles and json files)
    # step == 6:  # trim all cut audios: needs folders with all audios


def run_process_from_step(stage_step=1, stage_source_dir=None, dest_dir=None, language=None, split_word=None):
    chapters_folder = None
    # stage II - you already have tokenised and manually ptocessed book

    if stage_step == 1:
        # 1) split book for chapters
        book_file = find_book_in_folder(stage_source_dir)
        print('Stage II. Start step 1: chapter split')
        if book_file is None:
            print('ERROR on step 1! Can\'t find proper original book file')
            return False

        if split_word is None:
            print('Warninn! Split word is not defined. Assumiong there is only one chapter')

        chapters_folder = split_book(book_file, split_word)
        stage_step += 1
        if chapters_folder is None:
            print('ERROR on step 1! Book is not processed')
            return False

    if stage_step == 2:
        # 2) convert audio to wav 1 channel 22050Hz into chapters folder
        if chapters_folder is None:
            chapters_folder = dest_dir
        if chapters_folder is None:
            print('ERROR on step 2! Chapters folder is not defined')
            return False

        print('Stage II. Start step 2: audio conversion')
        stage_step += 1
        if not convert_audio(stage_source_dir, chapters_folder):
            print('ERROR on step 2. Audio convertion error')
            return False

    if stage_step == 3:
        # 3) run aeneas on each pair chapter/audio
        if language is None:
            print('ERROR on step 3! Language is not provided')
            return False
        if chapters_folder is None and stage_source_dir is None:
            print('ERROR on step 3. Stage folder is not defined')
            return False
        elif chapters_folder is None:
            chapters_folder = stage_source_dir

        print('Stage II. Start step 3: aeneas process with language - {}'.format(language))
        stage_step += 1
        if not run_aeneas(chapters_folder, language):
            print('ERROR on step 3. Aeneas runner error')
            return False

    if stage_step == 4:
        # 4) split audio files regarding to generated json
        if chapters_folder is None and stage_source_dir is None:
            print('ERROR on step 4. Aeneas results folder is not defined')
            return False
        elif chapters_folder is None:
            chapters_folder = stage_source_dir

        print('Stage II. Start step 4. Audio split')
        stage_step += 1
        if not split_audio_from_aeneas(chapters_folder):
            print('ERROR on step 4. Audio split error')
            return False

    result_wavs_folder = None
    result_text_file = None
    if stage_step == 5:
        # 5) collect all chapters json into one txt file, all audios into 1 folder
        if chapters_folder is None and stage_source_dir is None:
            print('ERROR on step 5. Folder with aeneas and split results is not defined')
            return False
        elif chapters_folder is None:
            chapters_folder = stage_source_dir

        print('Stage II. Start step 5: Collect data into one place')
        stage_step += 1
        result_wavs_folder = os.path.join(chapters_folder, 'wavs')
        if not collect_all_wavs(source_folder=chapters_folder, dest_folder=result_wavs_folder):
            print('ERROR on step 5. Audio files are not co llected')
            return False

        result_text_file = os.path.join(chapters_folder, 'metadata.txt')
        if not make_result_text_file(source_folder=chapters_folder, result_file_path=result_text_file):
            print('ERROR on step 5. Result text file is not created')
            return False

    result_trimmed_wavs_folder = None
    if stage_step == 6:
        # 6) trim audiofiles
        if result_wavs_folder is None and stage_source_dir is None:
            print('ERROR on step 6. Folder with wav files for trimming is not defined')
            return False
        elif result_wavs_folder is None:
            result_wavs_folder = stage_source_dir

        print('Stage II. Start step 6: Trim wav files ')
        stage_step += 1
        result_trimmed_wavs_folder = cleanup_and_trim_audio(result_wavs_folder)
        if result_trimmed_wavs_folder is None:
            print('Error during step 6: trimming result files')
            return False

    if stage_step == 7:
        # 7) put txt file and audiofiles into result folder
        if result_trimmed_wavs_folder is None or result_text_file is None or stage_source_dir is None:
            print('Error on step 7. Please move result files manually')
            return True  # In genberal process is cirrecxt, so return true

        print('Stage II. Start step 7: moving final results to the: {}'.format(stage_source_dir))
        if not make_book_result_folder(csv_filepath=result_text_file, wavs_folder=result_trimmed_wavs_folder, dest_folder=stage_source_dir, book_name=os.path.basename(chapters_folder)):
            print('Error during moving final results')
            return True  # In genberal process is cirrecxt, so return true
    print('Process finished')


def split_book(book_path, split_str):
    splitted_chapter_folder = split_text(book_path, split_str, os.path.splitext(book_path)[0])
    return splitted_chapter_folder


def run_aeneas(chapters_folder, language):
    global languages

    if language in languages.keys():
        aeneas_lang = languages[language]
    else:
        aeneas_lang = language

    audiofiles, chapterfiles = get_text_and_audiofiles(chapters_folder)

    if audiofiles is None or chapterfiles is None:
        return False
    widgets = [FormatLabel('File: %(message)s [%(value)s/' + str(len(audiofiles)) + ']'), ' ', Percentage(), ' ', Bar(marker='@', left='[', right=']'), ' ', ETA()]
    pBar = ProgressBar(widgets=widgets, maxval=len(audiofiles)).start()
    for idx, audio_path in enumerate(audiofiles):
        text_path = chapterfiles[idx]
        pBar.update(idx, os.path.basename(audio_path))
        if not run_aeneas_per_file(text_path, audio_path, aeneas_lang):
            pBar.finish()
            return False
    pBar.finish()
    return True


def run_aeneas_per_file(text_path, audio_path, lang):
    json_filepath = (os.path.splitext(audio_path)[0] + '.json')  # same name as audiofile
    args = [
        "dummy",
        audio_path,
        text_path,
        'task_language={}|is_text_type=plain|os_task_file_format=json|is_audio_file_detect_head_max=1|task_adjust_boundary_nonspeech_string=REMOVE'.format(lang),
        json_filepath
    ]
    exit_code = ExecuteTaskCLI(use_sys=False).run(arguments=args)
    if exit_code != 0:
        print('Erro happened on file: {}. Exit code: {}'.format(os.path.basename(audio_path), exit_code))
        return False
    if exit_code == 0:
        set_proper_filename_id(json_filepath, os.path.basename(os.path.splitext(audio_path)[0]))
    return True


def split_audio_from_aeneas(folder_path):
    json_files = get_all_json_files(folder_path)
    widgets = [FormatLabel('Splitting file: %(message)s [%(value)s/' + str(len(json_files)) + ']'), ' ', Percentage(), ' ', Bar(marker='@', left='[', right=']'), ' ', ETA()]
    pBar = ProgressBar(widgets=widgets, maxval=len(json_files)).start()

    for idx, json_file in enumerate(json_files):
        audio_file = os.path.splitext(json_file)[0] + '.wav'
        if not os.path.exists(audio_file):
            audio_file = os.path.splitext(json_file)[0] + '.mp3'
            if not os.path.exists(audio_file):
                print('Can\t find audio file with name {}'.format(os.path.basename(os.path.splitext(json_file)[0])))
                pBar.finish()
                return False

        pBar.update(idx, os.path.basename(json_file))
        if not make_split(json_file, audio_file):
            print('Error during audio split: {}'.format(os.path.basename(audio_file)))
            pBar.finish()
            return False
        pBar.finish()
    return True


def make_result_text_file(source_folder, result_file_path):
    return transform_all_jsons(source_folder, result_file_path)


def collect_all_wavs(source_folder, dest_folder):
    jsons = get_all_json_files(source_folder)
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    print('Moving files to result folder: {}'.format(dest_folder))
    widgets = [FormatLabel('Moving folder: %(message)s [%(value)s/' + str(len(jsons)) + ']'), ' ', Percentage(), ' ', Bar(marker='@', left='[', right=']'), ' ', ETA()]
    pBar = ProgressBar(widgets=widgets, maxval=len(jsons)).start()

    for idx, json_path in enumerate(jsons):
        audios = list()
        splitted_folder_path = os.path.splitext(json_path)[0]

        allfiles = os.listdir(splitted_folder_path)
        for item in allfiles:
            if item.endswith('.wav'):
                audios.append(os.path.join(splitted_folder_path, item))

        for audio_path in audios:
            dest_audio_path = os.path.join(dest_folder, os.path.basename(audio_path))
            pBar.update(idx, os.path.basename(audio_path))
            os.rename(audio_path, dest_audio_path)
    pBar.finish()
    return True


def cleanup_and_trim_audio(folder_path):
    trim_audio_files(None, folder_path, 150, -40, False, 500)
    result_folder = os.path.join(folder_path, 'trimmed')
    return result_folder


def make_book_result_folder(csv_filepath, wavs_folder, dest_folder, book_name):
    result_folder_path = os.path.join(dest_folder, book_name + '_done')
    result_text_file_name = book_name + '_' + os.path.basename(csv_filepath)
    result_wavs_folder_name = book_name + '_' + os.path.basename(wavs_folder)

    result_text_path = os.path.join(result_folder_path, result_text_file_name)
    result_wavs_path = os.path.join(result_folder_path, result_wavs_folder_name)

    if not os.path.exists(result_folder_path):
        os.makedirs(result_folder_path)

    if not os.path.exists(result_folder_path):
        print('Can\'t create folder: {}'.format(result_folder_path))
        return False
    os.rename(csv_filepath, result_text_path)
    os.rename(wavs_folder, result_wavs_path)
    return True


def print_usage(should_exit=True):
    print('Usage:')
    print('\t1 stage (sentence tokenise):                       -t <file-path> -l <language>')
    print('\t2 stage : 1 step (full parse cycle)                -s 1 -p <folder-path> -w <split-text> -l <language>')
    print('\t2 stage : 2 step (Start from convert audio step)   -s 2 -p <folder-path> -d <folder-path> -l <language>')
    print('\t2 stage : 3 step (Start from aeneas run step)      -s 3 -p <folder-path> -l <language>')
    print('\t2 stage : 4 step (Start from split audio step)     -s 4 -p <folder-path>')
    print('\t2 stage : 5 step (Start collect data step)         -s 5 -p <folder-path>')
    print('\t2 stage : 6 step (Start from trim audio step)      -s 6 -p <folder-path>')
    print('\n\n')
    print('\t-t  --tokenise         <file path>             File path to tokenised book. In this case language key is mandatory')
    print('\t-s  --step             <file path>             Step from which second stage should start 1..6')
    print('\t-p  --source_dir       <directory path>        Source directory for current step.')
    print('\t                                               Step  1 - folder with book and .mp3 files.')
    print('\t                                               Step  2 - src: folder with book and .mp3 files. dst: folder with chapters.')
    print('\t                                               Step  3 - folder with chapters and .wav files')
    print('\t-d  --dest_dir         <directory path>        Destination directory for audio convert step')
    print('\t-w  --split_word       <split-text>            Text for book split into chapters.')
    print('\t-l  --language         <language>              Please use full language names:  \'german\', \'french\', \'spanish\', \'english\', \'turkish\', \'italian\'')
    if should_exit:
        sys.exit(1)


if __name__ == '__main__':
    try:
        options, arguments = getopt.getopt(sys.argv[1:], 't:s:p:d:w:l:', ['--tokenise', '--step', '--source_dir', '--dest_dir', '--split_word', '--language'])
    except getopt.GetoptError:
        print_usage()

    language = 'english'
    book_text_file = None
    source_dir = None
    split_word = None
    dest_dir = None
    step = -1

    for opt, arg in options:
        if opt in ('-t', '--tokenise'):
            step = 0
            book_text_file = arg
        if opt in ('-s', '--step'):
            step = int(arg)
        if opt in ('-p', '--source_dir'):
            source_dir = arg
        if opt in ('-d', '--dest_dir'):
            dest_dir = arg
        if opt in ('-l', '--language'):
            language = arg
        if opt in ('-w', '--split_word'):
            split_word = arg

    if step >= 0:
        run_pipeline(step=step, language=language, book_text_file=book_text_file, stage_source_dir=source_dir, audio_dest_folder=dest_dir, split_word=split_word)
    else:  # ask user for action
        print_usage(should_exit=False)
        print('\n\n')
        action_number = ask_user_for_action()
        step = action_number - 1
        if action_number == 0:
            print('Goodbye')
            exit(0)

        elif action_number == 1:  # tokenise. needs: book path, language
            book_text_file = get_path_tk(title='Select book file to tokenise', is_directory=False, file_type_desc=('Text Files', '.txt'), exit_if_none=True)
            language = ask_for_language()

        elif action_number == 2:  # full cycle. needs: folder with a tokenised book and .mp3 files
            language = ask_for_language()
            split_word = raw_input('Please enter chapter sepatarion text:  ')
            source_dir = get_path_tk(title='Select folder with book', is_directory=True, exit_if_none=True, file_type_desc=None)

        elif action_number == 3:  # convert audio. needs: source path, destination path (with splitted chapters), language
            language = ask_for_language()
            print('please pick fodler with audiofiles to convert')
            source_dir = get_path_tk(title='Select folder audiofiles to convert', is_directory=True, exit_if_none=True, file_type_desc=None)
            print('please pick destination folder (folder with split chapters)')
            dest_dir = get_path_tk(title='Select folder with splitted book chapters', is_directory=True, exit_if_none=True, file_type_desc=None)

        elif action_number == 4:  # aeneas start. needs: splitted chapters folder, language
            language = ask_for_language()
            print('please pick source folder (folder with split chapters)')
            source_dir = get_path_tk(title='Select folder with splitted book chapters', is_directory=True, exit_if_none=True, file_type_desc=None)

        elif action_number == 5:  # split audio. needs: splitted chapters folder
            print('please pick source folder (folder with split chapters)')
            source_dir = get_path_tk(title='Select folder with splitted book chapters', is_directory=True, exit_if_none=True, file_type_desc=None)

        elif action_number == 6:  # colect data. needs: splitted chapters folder
            print('please pick source folder with wav files)')
            source_dir = get_path_tk(title='Select folder with splitted book chapters', is_directory=True, exit_if_none=True, file_type_desc=None)

        elif action_number == 7:  # trim audiofiles. needs: folder with audiofiles
            source_dir = get_path_tk(title='Select folder with audiofiles to trim', is_directory=True, exit_if_none=True, file_type_desc=None)

        if step >= 0:
            run_pipeline(step=step, language=language, book_text_file=book_text_file, stage_source_dir=source_dir, audio_dest_folder=dest_dir, split_word=split_word)
