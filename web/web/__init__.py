import sys
import re
from pyramid.config import Configurator
import xmlrpclib
import tokenize_en as vva_tokenizer
from detokenize import Detokenizer as MTMDetokenizer


# Module global Moses server instance - initialized in main() and used in translate().
MOSES_SERVER = None
MTMDetok = MTMDetokenizer()

# Maximum length of input source text.
# Text exceeding this size in length will be truncated.
MAX_TEXT_LEN = 256


def sanitize_text(text):
    """Sanitize user input by normalizing control characters etc.

    Parameters:
        text (string): text to sanitize.

    Returns:
        Sanitized text.
    """
    text = text.replace('\t', ' ')
    text = text.replace('\f', ' ')
    text = text.replace('\n', ' ')
    text = text.replace('\r', '')
    text = text.replace('\x08', '')
    text = text.replace('\x07', '')
    text = text.replace('\x1B', '')
    return text


# List of (punctuation, HTML entity) tuples.
# This is all what Moses's tokenizer.perl script supports.
PUNC_ENTITY_MAP = [
    ('&', '&amp;'),
    ('|', '&#124;'),
    ('<', '&lt;'),
    ('>', '&gt;'),
    ('\'', '&apos;'),
    ('"', '&quot;'),
    ('[', '&#91;'),
    (']', '&#93;')
]


def escape_html_entities(text):
    """Replace punctuation marks in text with HTML entities.

    Parameters:
        text (string): text to escape.

    Returns:
        string with punctuations escaped.
    """
    for punc, entity in PUNC_ENTITY_MAP:
        text = text.replace(punc, entity)
    return text


def unescape_html_entities(text):
    """Replace HTML entities with punctuation marks.
    This is the inverse of escape_html_entities() above.

    Parameters:
        text (string): text to unescape.

    Returns:
        string with HTML entities unescaped.
    """
    for punc, entity in PUNC_ENTITY_MAP:
        text = text.replace(entity, punc)
    return text


def tokenize_en(text):
    """Given an English text, tokenize it using the VVA tokenizer.

    Parameters:
        text (string): English text to tokenize.

    Returns:
        list of tokenized words (strings)
    """
    return vva_tokenizer.split2(text)[0].split(' ')


def detokenize_en(text):
    """Given an English text, tokenize it using the VVA tokenizer.

    Parameters:
        text (string): English text to tokenize.

    Returns:
        list of tokenized words (strings)
    """

    # Add whitespace after single quotes
    # so that MTMonkey detokenizer can handle contractions properly.
    text = re.sub(r'\'([^ ])', '\' \\1', text)

    try:
        text = MTMDetok.detokenize(text)
    except Exception as e:
        print >>sys.stderr, 'An exception occurred during detokenizing: %s' % e
    return text


def tokenize_jb(text):
    """Given a Lojban text, tokenize it to a list of words.
    This also normalizes individual words by stripping off periods and question marks."""

    # Moses interprets brackets '[]' in a special way, and passing them as is
    # crashes Moses. Tokenize them here.

    text = text.replace('[', ' [ ')
    text = text.replace(']', ' ] ')

    tokens = [word.strip('.?') for word in re.split(' +', text)]

    # remove the first 'i'
    if len(tokens) > 0 and tokens[0] == 'i':
        tokens = tokens[1:]
    return tokens


def translate(src, direction):
    """Translate source text according to direction.

    Parameters:
        src (string): text to translate.
        direction (string): either 'jb2en' or 'en2jb'. Throws AssertionError otherwise.

    Returns:
        Translated text.
    """

    src = src[:MAX_TEXT_LEN]
    src = sanitize_text(src)

    if direction == 'jb2en':
        # Lojban to English translation
        src = ' '.join(tokenize_jb(src))
        tgt = MOSES_SERVER.translate_jb2en(src)
        tgt = unescape_html_entities(tgt)
        tgt = detokenize_en(tgt)
        return tgt
    elif direction == 'en2jb':
        # English to Lojban translation
        src = ' '.join(tokenize_en(src))
        src = escape_html_entities(src)
        tgt = MOSES_SERVER.translate_en2jb(src)
        tgt = unescape_html_entities(tgt)
        return tgt
    else:
        assert False


def main(global_config, **settings):
    global MOSES_SERVER
    """This function returns a Pyramid WSGI application."""
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    MOSES_SERVER = xmlrpclib.ServerProxy(settings['moses_server'])
    return config.make_wsgi_app()
