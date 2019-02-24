# -*- encoding: utf8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from .de_num_normalize import de_normalize_numbers
from .en_num_normalize import en_normalize_numbers
from .uk_num_normalize import uk_normalize_numbers
from .ru_num_normalize import ru_normalize_numbers
from .tr_num_normalize import tr_normalize_numbers
from .es_num_normalize import es_normalize_numbers
from .it_num_normalize import it_normalize_numbers
from .pl_num_normalize import pl_normalize_numbers
from .fr_num_normalize import fr_normalize_numbers


def normalize_numbers(text, language):
    if language == 'de':
        return de_normalize_numbers(text)
    elif language == 'en':
        return en_normalize_numbers(text)
    elif language == 'uk':
        return uk_normalize_numbers(text)
    elif language == 'ru':
        return ru_normalize_numbers(text)
    elif language == 'tr':
        return tr_normalize_numbers(text)
    elif language == 'es':
        return es_normalize_numbers(text)
    elif language == 'it':
        return it_normalize_numbers(text)
    elif language == 'pl':
        return pl_normalize_numbers(text)
    elif language == 'fr':
        return fr_normalize_numbers(text)
    else:
        return text
