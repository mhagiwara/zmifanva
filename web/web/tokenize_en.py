#!/usr/bin/env python
# coding: utf-8

#### ENGLISH TOKENIZER ###############################################################################
# Tokenizer divides a sequence of characters into words and sentences using regular expressions.
# Special care is given to punctuation marks. We need to guess which punctuation marks are part
# of a word (e.g. abbreviations) and which mark word and sentence breaks.

# Based on:
# - CNTS tokenizer.pl - S. Buchholz, E. Tjong Kim Sang, J. Meyhi, 1998-2005
# - CNTS tokenizer.py - V. Van Asch, 2008

# This tokenizer is branched off from the tokenizer included in MBSP: http://www.clips.ua.ac.be/pages/MBSP
# License: GNU General Public License, see LICENSE.txt in the MBSP package 


__author__    = "Tom De Smedt, Vincent Van Asch"
__version__   = "1.3"
__date__ = "July 2010"
__copyright__ = "Copyright (c) 2010 CLiPS"

######################################################################################################
# Note for developers: 
# For performance, always compile regular expressions once, outside of the functions.

import re, sys, getopt

PUNCTUATION = [ch for ch in """(){}[]<>!?.:;,`'"@#$%^&*+-|=~/\\_"""]
LETTERS     = [ch for ch in "abcdefghijklmnopqrstuvwxyz"]
CONSONANTS  = [ch for ch in "bcdfghjklmnpqrstvwxz"] # Need this for Mr. Mss. abbreviations.
WHITESPACE  = [ch for ch in " \t\n\r\f\v"]          # Need this to split words.
DASHES      = [ch for ch in u"–—"]                  # Not to be confused with hyphen.

is_uppercase   = lambda s: len(s)>0 and s==s.upper()                          # Goodbye => True
is_capitalized = lambda s: len(s)>0 and s[0].isalpha() and s[0]==s[0].upper() # GOODBYE => True

digits = re.compile("^[0-9]+$")
is_int = lambda s: digits.search(s) != None

# regex pattern for entities: &amp; &#164;
entity = "&[a-z]+;|&#[0-9]+;"

#### RANGES ##########################################################################################
# Sets that match a range of words: all abbreviations, all numeric strings, all hyperlinks, ...
# The Range class is a dictionary enriched with regular expression patterns.
# You can do handy "word in Range()" or in_any(word, ranges) checks.

class Range(dict):
    
    def __init__(self, items=[]):
        dict.__init__(self, items)
        self.patterns = []
        
    def __contains__(self, str):
        if dict.__contains__(self, str): 
            return True
        for p in self.patterns:
            if p.search(str) != None: 
                return True
        return False

def in_any(word, ranges=[]):
    for rng in ranges:
        if word in rng: return True

#--- ABBREVIATIONS -----------------------------------------------------------------------------------

abbreviations = [
    "Adm.", "Ala.", "Ariz.", "Ark.", "Aug.", "B.C.", "Bancorp.", "Bhd.", "Brig.", "Bros.", "CO.", 
    "CORP.", "COS.", "ca.", "Calif.", "Capt.", "Cie.", "Cmdr.", "Co.", "Col.", "Colo.", "Conn.", "Corp.", 
    "Cos.", "Cpl.", "D-Mass.", "D.C.", "Dec.", "Del.", "Dept.", "Dr.", "E.g.", "Etc.", "Ex.", "Exch.", 
    "Feb.", "Fla.", "Fri.", "Ga.", "Gen.", "Gov.", "INC.", "Ill.", "Inc.", "Ind.", "Jan.", "Jansz.", 
    "Jos.", "Jr.", "Kan.", "Ky.", "L.A.", "La.", "Lt.", "Ltd.", "Maj.", "Mass.", "Md.", "Messrs.", 
    "Mfg.", "Mich.", "Minn.", "Miss.", "Mo.", "Mon.", "Mr.", "Mrs.", "Ms.", "Mt.", "N.C.", "N.J.", 
    "N.Y.", "NFATc.", "Neb.", "Nev.", "No.", "Nos.", "Nov.", "O.J.", "Oct.", "Okla.", "Ont.", "Ore.", 
    "P.T.", "Pa.", "Ph.", "Prof.", "Prop.", "Pty.", "R.I.", "R.J.", "Rep.", "Reps.", "Rev.", "S.C.", 
    "Sat.", "Sen.", "Sens.", "Sep.", "Sept.", "Sgt.", "Sol.", "Sr.", "St.", "Sun.", "Tenn.", "Tex.", 
    "Thu.", "Tue.", "U.K.", "U.N.", "U.S.", "Va.", "Vt.", "W.J.", "W.Va.", "Wash.", "Wed.", "Wis.", 
    "Wyo.", "a.m.", "cit.", "def.", "ed.", "eds.", "e.g.", "etc.", "ft.", "i.e.", "op.", "p.m.", "pp.", 
    "sc.", "v.", "vs.", "Biol.", "Chem.", "al.", "beta4.", "Struct.", "Funct.", "Natl.", "Acad.", "Sci.",
    "Biochem.", "Cell.", "Proc.", "Res.", "Lond.", "Nat.", "Dev.", "Camb.", "Profilin.", "Thymosin-beta4."
]

class Abbreviations(Range):
    
    def __init__(self, known=[]):
        """ A dictionary of known abbreviations, extended with patterns of likely abbreviations.
            word in Abbreviations() == True if word is a known or likely abbreviation.
            Periods in English are ambiguous,
            marking end of sentence, abbreviation, decimal point or ellipsis.
            - Simple rule: "every point is a sentence break" is 93.20% correct for Brown corpus.
            - Fix decimal points: 93,64% correct.
            - Fix single letter abbreviations (T. De Smedt), alternating letters (i.e. U.S.),
              and capital letter followed by consonants (Mr. Assn.): 97.7% correct.
            - Fix with dictionary of known abbreviations: up to 99,07 accuracy.
            http://bulba.sdsu.edu/~malouf/ling571/13-token-bw.pdf
        """
        Range.__init__(self, [(x,True) for x in known])
        self.patterns = [
            re.compile("^[A-Za-z]\.$"),                       # single letter, "T. De Smedt"
            re.compile("^([A-Za-z]\.)+$"),                    # alternating letters, "U.S."
            #re.compile(".+\.[,;]$"),                         # followed by punctuation, "dept.,"
            re.compile("^[A-Z]["+"|".join(CONSONANTS)+"]+.$") # capital followed by consonants, "Mr."
        ]
        
    def __contains__(self, word):
        return word.endswith(".") and Range.__contains__(self, word)

abbreviations = Abbreviations(abbreviations)

#--- NUMBERS -----------------------------------------------------------------------------------------

currencymarkers = [ "$", "£", "€", "EUR", "BEF", "US$", "C$" ] 
units = [
    "nm", "mm", "cm", "m", "km", "\"", "'", "ft",                  # length
    "g", "kg", "lb", "lbs", "oz",                                  # mass
    "l", "L", "mmol",                                              # volume
    "hrs", "hr", "h", "u", "AM", "PM", "am", "pm", "a.m.", "p.m.", # time
    "BC", "AD", "B.C.", "A.D.",                                    # epoch
    "°C", "°F",                                                    # temperature
    "KB", "MB", "GB", "TB", "kb",  "mb", "gb", "tb",               # storage capacity
    "Kb", "Mb", "Mbit", "Gb", "Tb",                                # data transfer rate
    "%"                                                            # percentage
]
# Add currencies to units
units.extend(currencymarkers)

# Make a Range() so we have the patterns for an amount starting with a currency marker (E.g. US$100)
currencies=Range()
currencies.patterns = [re.compile('^'+re.escape(x)) for x in currencymarkers]



class Numeric(Range):
    
    def __init__(self, units=[], punctuation="\.,:/"):
        """ A range for numeric strings.
            word in Numeric() == True for 0, 0-0, 000.0, 00/00/00, 00:00, 0km, 0.0KB ... 
            The range will match anything that starts with a digit
            followed by a chain of digits and .,:/ separators,
            as long as the last character is a digit,
            optionally followed by a unit of measurement.
        """
        Range.__init__(self)
        self.units = dict.fromkeys(units, True)
        # Anything that starts with a digit, ends with a digit,
        # with a mix of digits and punctuation in between, suffixed by a unit.
        # Note the 4: this is the maximum unit length.
        self.patterns = [re.compile("^(\d*["+punctuation+"])*(\d+)(.{0,4})$")]
        self._cache = ("", "", False) # (word, unit suffix, is number?)
        
    def __contains__(self, word):
        if self._cache[0] == word:
            return self._cache[2]
        elif len(word) > 0 and word[0].isalpha(): 
            u, b = "", False
        else:
            m = self.patterns[0].search(word)
            u = m!=None and m.group(3) or ""
            b = m!=None and u=="" or u in self.units
        self._cache = (word, u, b)
        return b

    def unit(self, word):
        """ Yields the unit suffix of the last word checked, e.g. 1000km => km
        """
        if word != self._cache[0]: 
            word in self
        return self._cache[1]
    
    @property
    def cached(self):
        return self._cache[0]

numeric = Numeric(units)

def split_numeric(word):
    """ Returns a list with the word, and its unit if it is numeric: "100kg" => ["100", "kg"]
    """
    u = numeric.unit(word)
    # Penn treebank's choice only split %:  100%  => 100 %
    if u == "%": 
        return [word[:-len(u)], u]
        
    # For US$100  =>  US$ 100 
    for marker in currencies.patterns:
        m = marker.match(word)
        if m:
            return [word[:m.end()], word[m.end():]]
    
    return [word]

#--- UNIFORM RESOURCE INDENTIFIERS -------------------------------------------------------------------

class UniformResourceIdentifiers(Range):
    
    def __init__(self):
        """ A range for URLs, links and e-mail adresses.
            It will match:
            - anything that starts with http://, ftp://, feed://
            - domain names: www.google.com, google.com, nodebox.net/Home
            - e-mail addresses: Tom.DeSmedt@somewhere.com
        In the last case for example we might rule againts splitting 
        Tom. <=> DeSmedt@somewhere.be as two separate sentences.
        """
        Range.__init__(self)
        self.patterns = [
            re.compile("^(http|https|ftp|feed)://"),              # url: http://xxxxxx.xxx
            re.compile("^www\."),                                 # domain: www.xxxxxx.xxx
            re.compile("\.(com|org|net|us|eu|uk|de|be)(/.*?)*$"), # domain: xxxxxx.com, xxxxxx.net/Home
            re.compile("^(.*?)@(.*?)\.(.*?)")                     # email: xxx@xxx.xxx
        ]

URI = UniformResourceIdentifiers()

#--- ENTITIES ----------------------------------------------------------------------------------------

class Entities(Range):
    
    def __init__(self):
        """ A range for HTML (e.g. &eacute;) and Unicode (e.g. &#164;) entities.
            If you can, reuse a cached version of re.compile(entity) instead; it's 2x faster.                                
        """
        Range.__init__(self)
        
    def __contains__(self, word):
        if len(word) > 3 and word.startswith("&") and word.endswith(";"):
            if word[1:-1].isalpha() \
            or word[1] == "#":
                return True
        return False

entities = Entities()

##### SPLITTERS ######################################################################################
# Functions that split words, punctuation, sentences. 

#--- CONTRACTIONS ------------------------------------------------------------------------------------
# Apostrophes in contractions (he's) and possessives (father's) mark word boundaries.

# These don't necessarily contain an apostrophe so we need to check them all.
# The whole word is replaced.
contractions = {
    "cannot"  : "can not",
}
# Special English contractions containing apostrophe.
# The whole word is replaced.
contractions_apostrophe = {
    "I'm"     : "I am",
    "ain't"   : "am not",
    "can't"   : "can not",
    "won't"   : "will not",
    "shan't"  : "shall not",
    "let's"   : "let us",
    "'cause"  : "because",
    "'em"     : "them",
    "'til"    : "until",
    "'tis"    : "it is",
    "'twas"   : "it was",
    "'n'"     : "and",
    "'nother" : "another"
}


contractions_apostrophe = {} # Penn treebank's choice
# Common English verb contractions.
# The word ending is replaced.
contractions_suffixes = {
    "n't"     : "n't", # Regular don't, isn't, wasn't, doesn't, haven't, ...
    "'s"      : "'s",  # Can't disambiguate: it's been => it has been, it's hot => it is hot.
    "'d"      : "'d",  # Can't disambiguate: I'd better go => It had, he'd want to go => he would.
    "'m"      : "'m",
    "'re"     : "'re",
    "'ll"     : "'ll",
    "'ve"     : "'ve"                         
}
# Shouldn't split 60's, 1960's, 9's but not currently in use.
era = re.compile("^[0-9]+'s$")

def case_sensitive(word, replacement):
    """ Attempts to return replacement in the same case as the given word.
        If word is lowercase, yield lowercase replacement.
        If word is uppercase, yield uppercase replacement.
        If word starts with a capital, yield lowercase replacemnt with starting capital.
        - "cannot" => "can not"
        - "Cannot" => "Can not"
        - "CANNOT" => "CAN NOT"
        - "caNnOt" => "can not"
    """
    r = replacement.lower()
    if len(word) == 0:
        return r
    if word[0] == word[0].lower():
        return r
    if is_uppercase(word):
        return r.upper()
    if is_capitalized(word):
        return r.capitalize()
    return r

def case_insensitive(pattern, replacement, word):
    '''Replaces the pattern with replacement. Patterns are case-insensitively matched.
    The replacement is in the same case as the replaced chars in word (but only chooses between all-upper
    pr all-lower.
    
    creator: all lower
    Creator: all lower
    CREATOR : all upper
    
    CREATOR'S, 's, ''  => CREATOR
    CREATOR'S, or, ure  => CREATURE'S'''
    string = word
    for match in re.findall(pattern, string, re.I):
        if match.isupper():
            string = string.replace(match, replacement.upper())
        else:
            string = string.replace(match, replacement.lower())
    return string


def split_contraction(word):
    """ Apostrophes in contractions (he's) and possessives (father's) are word boundaries.
        Returns the expanded form of the word as a list of strings.
        I've => ["I", "have"]
    """
    k = word.lower()
    if k in contractions:
        return case_sensitive(word, contractions[k]).split(" ")
    if "'" in k:
        if k in contractions_apostrophe:
            return case_sensitive(word.lstrip("'"), contractions_apostrophe[k]).split(" ")
        for s in contractions_suffixes:
            if k.endswith(s) and len(k)>len(s):
                # Disambiguate between upper case and lower case to avoid insertion of an extra 's when splitting CREATOR'S
                if word.isupper():
                    return [case_insensitive(s, "", word), contractions_suffixes[s].upper()]
                else:
                    return [case_insensitive(s, "", word), contractions_suffixes[s].lower()]
    return [word]

#--- HYPHENATION -------------------------------------------------------------------------------------
# Hyphens at the end of a line mark words that have been split across lines.

# Hyphenated words are those that end in a single "-".
# Unknown cases (e.g. "blah--", "-") are ignored.
hyphen = re.compile("\w\-$")

# Coordinators are never joined to the hyphened word.
coordinators = ["and", "or"]

# Words starting with "and-" or "or-".
# Rare, e.g. rag- \nand-bone man.
coordination_prefix = "|".join([x+"-" for x in coordinators])
coordination_prefix = re.compile("^"+coordination_prefix+"-")

def split_hyphenation(words=[]):
    """ Joins words that have been hyphenated by line-wrapping, i.e. "mar- \nket" => "market\n". 
        Otherwise, "mar- ket" is ignored; hyphens only occur inside a word or at the end of line.
        The input is a list of split words and \n items (see split_words() below).
        The output is the restructured list:
        1) ["Great-","\n","Britain"] => ["Great-Britain","\n"]
        2) ["nineteenth-","\n","and","twentieth-century","writers"] remains unchanged
        3) ["EU-", "\n", "mandaat"] => ["EU-mandaat", "\n"]
        4) ["12-", "\n", "hour"] => ["12-hour", "\n"]
        5) ["mar-","\n","ket"] => ["market","\n"]
    """
    p, i, n = [], 0, len(words)
    while i < n:
        w1 = words[i]
        br = i<n-1 and words[i+1] or ""
        w2 = i<n-2 and words[i+2] or ""
        # Check for a break first, lazy evaluation might save us a regex lookup.
        if br == "\n" and w2 and hyphen.search(w1) != None:
            if is_capitalized(w2):                       # (1)
                p.extend([w1+w2,"\n"])
            elif w2 in coordinators \
              or coordination_prefix.search(w2) != None: # (2) + schiet- \nen-vechtgeval
                p.extend([w1,"\n",w2])
            elif is_uppercase(w1[-2]):                   # (3)
                p.extend([w1+w2,"\n"])
            elif w1[0:-1] in numeric:                    # (4)
                p.extend([w1+w2,"\n"])
            else:                                        # (5)
                p.extend([w1[0:-1]+w2,"\n"])
            i += 2
        else:
            p.append(w1)
        i += 1
    return p

#--- MISSING SPACE -----------------------------------------------------------------------------------
# Punctuation inside a word can indicate a missing space, e.g. "Hello;and goodbye".

# The general idea of how to split word internal punctuation.
# Exceptions and corrections can be handled in assert_split().
dashes = "|".join(DASHES)
missing_space = (
    re.compile("^(.*?)(\.\.+)(.*)"),       # multiple periods:               "wait..go" => "wait .. go"
 #   re.compile("^(.*?\))(\.)(.*)"),        # period preceded by parenthesis: "wait).go" => "wait) . go"
    re.compile("^(.*?\.)(\(|\[)(.*)"),     # period followed by parenthesis: "wait.(go" => "wait . (go"
    re.compile("^([^\(]*?)(\))(.*)"),      # unbalanced parenthesis:         "wait)go"  => "wait ) go"
#    re.compile("^(.*?)(\.)([A-Z].*)"),     # period followed by capital:     "wait.Go"  => "wait . Go"  # Gives problems with abbreviations U.S becomes U. S.
    re.compile("^(.*?)(,|;|:)(.+)"),     # word internal punctuation:      "wait;go"  => "wait ; go"
    re.compile("^(.*?)("+dashes+")(.*)"),  # em-dash and en-dash:            "wait—go"  => "wait — go"
    re.compile("^(.*?)("+entity+")(.*)"),  # HTML/Unicode entities:        "&eacute;go" => "&eacute; go"
#    re.compile("(\d+)(-)(\d+)"),           # number range:                   "100-200"  => "100 - 200"  # Penn treebank's choice
    re.compile("^(.*?)(\[\d+\])(.*)"),       # Wikipedia references:           "wait[1]"  => "wait [1]"
)

def assert_split(a, b, c, sets=[]):
    """ Returns (a,b) if splitting a word into a and b seems correct.
        Otherwise, return the corrected form.
    """
    if b.startswith("."):
        # Split "etc.," to ["etc.", ","] instead of ["etc", ".", ","]
        if b == ".," or in_any(a+".", sets):
            return a+".", b[1:], c
    if b == ",":
        # Split "6,000-year" to ["6", ",", "000-year"]
        # Added the  a[-1] in [')', '\''] condition for biomedical entries like: 3(R),3a(S),6a(R)-bis-tetrahydrofuranylurethane 
        if len(a)>0 and (is_int(a[-1]) or a[-1] in [')', '\'']) and \
              len(c)>0 and is_int(c[0]):
            return None, None, None
    return a, b, c

def split_missing_space(word, ignore=[abbreviations, numeric, URI, entities]):
    """ Splits words that are probably two word with missing punctuation in between.
        Returns the expanded form of the word as a list of strings, i.e.
        nice;also => ["nice", ";", "also"]
        The ignore list contains lists of known words that should not be split,
        see also abbreviations, numeric, URI, entities...
    """
    # In the case of "It's 10:45.", the 10:45 will be split because "10:45." 
    # is not validate as a number, whereas "10:45" is.
    # So we check if it is a number with the word's head and tail punctuation removed.
    # This head and tail punctuation needs to be split in a later step - see split_punctuation().
    if in_any(word.strip("".join(PUNCTUATION)), ignore): 
        return [word]
    for p in missing_space:
        m = p.search(word)
        if m != None:
            a, b, c = m.group(1), m.group(2), m.group(3)
            a, b, c = assert_split(a, b, c, ignore) # etc., => etc.][. not etc][.,
            if a == b == c == None : continue
            S = [b]
            # The split "words" in the chain may not have been examined, recurse them.
            if len(a) > 0: S = split_missing_space(a, ignore) + S
            if len(c) > 0: S+= split_missing_space(c, ignore)
            return [x for x in S if x != ""]
    return [word]
    
#--- PUNCTUATION -------------------------------------------------------------------------------------
# Deal with punctuation at the head or tail of a word.

punctuation = dict.fromkeys(PUNCTUATION, True) # Dictionary lookup is faster.

# A number of words to keep intact:
punctuation_head = Range()
punctuation_head.patterns = [
    re.compile("^\.[0-9]+"),             # calibre: .22
    re.compile("^'[0-9][0-9](-|$)"),     # year: '93 '93-'94
    re.compile("^\([A-Za-z]+(-\)|\)-)"), # rare: (oud-)student (her)-introductie
]
punctuation_subst = Range()
punctuation_subst.patterns = [
    re.compile("^\([A-Za-z]+(-\)|\)-)$"), # rare: livers of bile duct ligation (BDL)- or ethinyl estradiol (EE)-injected rats
]
punctuation_tail = Range()
punctuation_tail.patterns = [
    re.compile(".\([A-Za-z]+\)$"),       # rare: koning(in)
]

def split_chars(word, chunk=".-"):
    """ Returns a list of characters in the given string.
        Characters in the defined chunk will be kept together,
        i.e. split_chars("Hello...", chunk="l.") => ["H", "e", "ll", "o", "..."]
    """
    p = [""]
    for ch in word:
        if ch in chunk and p[-1].startswith(ch):
            p[-1] += ch
        else:
            p.append(ch)
    return p[1:] or [""]

def split_punctuation(word, ignore=[abbreviations, numeric, URI, entities]):
    """ Splits punctuation from the head and tail of the word.
        Returns the expanded form of the word as a list of strings, i.e.
        goodbye. => ["goodbye", "."]
        The ignore list contains lists of known words that should not be split,
        see also abbreviations, numeric, URI, entities...
        Some other rare exceptions are hard-coded not to split 
        (see punctuation_head and punctuation_tail above).
    """
    if len(word) == 0 or word[0].isalnum() and word[-1].isalnum():
        # Nothing to do: there is no punctuation at the head or tail of the word.
        # This shortcut makes the function call 2x faster.
        return [word]
    if in_any(word, ignore):
        # If the word is in a known range (e.g. a HTML entity or abbreviation),
        # no further processing is required. We do split any number unit (e.g. 1000km => 1000 km).
        return split_numeric(word)
    if word in contractions_suffixes:
        return [word]
    if word in punctuation_subst:
        # For cases like: livers of bile duct ligation (BDL)- or ethinyl estradiol (EE)-injected rats
        return [word]
        
    # Find the head and the tail of the word containing punctuation.
    p, i, j = [], 0, len(word)-1
    while i<=j and word[i] in punctuation:
        if i==j:
            i+=1
        elif word[i+1] not in '0123456789':
            i+=1
        elif word[i] != '.':
            i+=1
        else:
            break

    
    while j>=0 and word[j] in punctuation: j-=1
    # Discard the head or tail if the punctuation is valid (e.g. .22 calibre).

    try:
        if word[j+1] == ')' and word[i:j+1].count('(') - word[i:j+1].count(')') > 0:
            # There are more closing than opening brackets in the part of the word that is kept
            # so leave the closing bracket(s) attached
            
            #This is a bit more intelligent than the old: if word in punctuation_tail: j=len(word)
            j += word[i:j].count('(') - word[i:j].count(')')
    except IndexError:
        pass

    if word in punctuation_head \
    or word[:j+1] in contractions_apostrophe: i=0
    # If the head and the tail are the same,
    # i.e. the word consists entirely out of punctuation), discard the tail.
    a, b, c = word[:i], word[i:j+1], j>-1 and word[j+1:] or ""
    b, c, X = assert_split(b, c, "", ignore) # etc., => etc.][. not etc][.,
    if b == c == X == None: return [word]
    # Split the punctuation.
    a = split_chars(a, chunk=".-'\"<>") # Keep dashes, ellipsis etc. together: -- ...
    c = split_chars(c, chunk=".-'\"<>")
    # Split units from numbers: We ran a 100km. => We ran a 100 km .
    b = split_numeric(b)
    return [x for x in a+b+c if x != ""]

#---- WORDS ------------------------------------------------------------------------------------------

def split_words(string, keep="\n"):
    """ Returns a list of words in the given string.
        All whitespace characters except those defined as keepers are replaced by a standard space.
        Multiple spaces are collapsed to a single space, 
        so that each word is separated by exactly one space.
        Words can contain punctuation marks at the start or end, we need to process these separately.
        We retain \n (newline) in the output is because we need it to process hyphenation.
    """
    w = "|".join(filter(lambda ch: ch not in keep, WHITESPACE))
    for ch in keep:
        # Collapse keepers, e.g, "\n \n" => "\n".
        # We will be splitting on spaces in a minute,
        # so ensure there is a space around each keeper.
        string = re.sub(ch+"["+ch+"|\s]+", ch, string)
        string = re.sub("\s{0,1}\n\s{0,1}", " "+ch+" ", string)
    string = string.strip()
    string = re.compile(w).sub(" ", string)
    string = re.sub(" +", " ", string)
    return string.split(" ")

def split_word(word, ignore=[abbreviations, numeric, URI, entities]):
    """ Splits contracted words, joined words with a missing space, punctuation.
        Returns the expanded form of the word as a list of strings, i.e.
        can't... => ["cannot", "..."]
    """
    if word.lower() == 'cannot':
        #Special rule for cannot because the split_contraction is not called on all alpha words
        a=[word]
        b = []; [b.extend(split_contraction(word)) for word in a]; return b
    
    if word.isalpha():
        # We're in luck: the word contains only alphabetic characters, no disambiguation needed.
        # This shortcut saves about 15-50% time depending on the complexity of the text.
        return [word]
    if in_any(word, ignore):
        # If the word is in a known range (e.g. a HTML entity or abbreviation),
        # no further processing is required. We do split any number unit (e.g. 1000km => 1000 km).
        return split_numeric(word)
    a = [word]
    b = []; [b.extend(split_missing_space(word, ignore)) for word in a]; a=b
    b = []; [b.extend(split_punctuation(word, ignore)) for word in a]; a=b
    b = []; [b.extend(split_contraction(word)) for word in a]; a=b
    return a

#--- TAGS --------------------------------------------------------------------------------------------
# By default, all tags are removed.
# If they need to be retained someone needs to add checks.
# Beware: <a href="foo" onclick="do();" fontsize=12> is a valid HTML tag...

tags = re.compile("</{0,1}.*?>")

# Before strippping tags, replace the following:
HTML_LIST_ITEM = "HTML___LIST___ITEM "
tags_replace = {
    re.compile("<head.*?>.*?</head>")     : "",             # Remove HTML metadata.
    re.compile("<style.*?>.*?</style>")   : "",             # Remove HTML CSS.
    re.compile("<script.*?>.*?</script>") : "",             # Remove HMTL Javascript.
    re.compile("<li.*?>")                 : HTML_LIST_ITEM, # Add list markers for split_lists().
    re.compile("\.{0,1}</h\d>")           : ". ",           # A <h1> block always ends sentence,
}                                                           # accomplished by adding a perdiod.

def strip_tags(string, replace=tags_replace):
    """ Strips all tags from the given string.
    """
    for p,r in replace.items():
        string = p.sub(r, string)
    return tags.sub("", string)

#--- SENTENCES ---------------------------------------------------------------------------------------

# Separated period always ends sentence.
# Punctuation like ? and ! end sentence when followed by a capitalized letter.
stop_always = ["."]
stop_assert = [ "?", "!", "..", "...", "....", "etc."]

# Parenthesis and quotes can be part of the sentence even if the period preceeds it.
# We will check for open/close balance, e.g.:
# - "Stop!" he shouted => the ! does not end sentence.
# - "Stop!" He shouted => the ! ends sentence and the quote after it is part of that sentence.
parenthesis = [")", "]", "}"]
start_parenthesis = ["(", "[", "{"]
quotes = ["\"", "'", "''", "'''", "\"\"\""]
continuation = [":", ";"]

ASSERT = "assert"
SENTENCE_BREAK  = "SENTENCE___BREAK"

# No spaces allowed in patterns!
# (Adams, A. E. M., D. Botstein, and D. G. Drubin. 1991. Nature (Lond.). 354:404-408.)
# (Adams, A. E. M., and D. Botstein. 1989. Genetics. 121:675-683.)
# (Drubin, D. G., K. G. Miller, and D. Botstein. 1988. J. Cell Biol. 107: 2551-2561.)
# [Pantaloni, D., et al. (1984)J. Biol. Chem. 259, 6274-6283]
nobreak = ( re.compile('\([A-Za-z,.]+\d\d\d\d\.[A-Z-a-z().]+\d+:\d+-\d+\.?\)'),
            re.compile('\[[A-Za-z,.]+\(\d{4}\)[A-Za-z.]+\d+,\d+-\d+\]') )  # This is ok and should be in a final version but because we added this patterns after processing Biograph it's turned off.

def prohibited_sentence_break(words=[]):
    '''Ad hoc function that makes that the patterns in nobreak
    are preserved.
    
    Returns a list of token indices that cannot be preceded by a sentence break. 
    '''
    output=[]; links=[]
    for i,word in enumerate(words):
        links.extend([i for j in range(len(word))])

    string =  ''.join(words)
    for prohibited in nobreak:
        for m in prohibited.finditer(string):        
            start = links[m.start()]+1
            stop = links[m.end()]
            if start == stop:     
                output.append(start)
            else:
                output.extend(range(start, stop))

    return output 
    


def add_sentence_breaks(words=[], marker=SENTENCE_BREAK):
    """ Returns the list of words with injected "<sentence />" breaks.
        ["Hello", ".", "Having", "fun", "?"] =>
        ["Hello", ".", "<sentence />", "Having", "fun", "?", "<sentence />"]
    """
    quote_count = {}
    p, i, n = [], 0, len(words)
    stop = False
    
    prohibited = prohibited_sentence_break(words)
    
    for i in range(n):
        word = words[i]
        # We count the occurences of quotes.
        # If at any time the count for a quote is uneven, this means we are inside a quotation, e.g.
        # "All work and no play. => if the period is followed by a ", it is part of this sentence.
        if word in quotes:
            quote_count[word] = quote_count.get(word,0)+1
        # Periods, ellipsis and some other punctuation mark the end of the sentence,
        # but we need to continue scanning if quotes or parenthesis follow 
        # that are still part of this sentence before adding the break.
        p.append(word)
        #print word, stop, p
        if i not in prohibited:
            if stop != False:
                if word in parenthesis:                  # hello!) Goodbye   => hello!) ][ Goodbye
                    pass
                elif word in quotes: 
                    if quote_count.get(word,0) % 2 != 0: # Hello. "Goodbye". => Hello. ][ "Goodbye".
                        p.insert(len(p)-1, marker)
                        stop = False
                    else:                                # "Hello." Goodbye. => "Hello." ][ Goodbye.
                        pass
                elif stop == True and word in continuation:   # For the case of "dilution series in pet.:0.3%-1%" don't split before the :
                    stop=False
                elif stop == True \
                  or stop == ASSERT and (is_capitalized(word) or word in start_parenthesis):    # The startparenthesis check is because . ( often marks a new sentence starting with ( 
                    p.insert(len(p)-1, marker)
                    stop = False
                else:
                    stop = False
            # Separated period or ellipsis always ends sentence.
            # For other punctuation marks we verify if it is followed by a capitalized letter.
            if stop == True and word in parenthesis:
                stop = ASSERT
            else:
                if word in stop_always:
                    stop = True
                elif word in stop_assert:
                    stop = ASSERT
        else:
            stop=False
            
            
            
    # Don't forget the sentence break at the end of the list,
    # e.g. ["'", "Enough", "of", "this", "!", "'"]
    if stop == True:
        p.append(marker)
    return p
            
def split_sentences(words=[], marker=SENTENCE_BREAK):
    """ Returns a list of sentences. Each sentence is a list of tokens.
        The input list of words is expected to have been treated with through add_sentence_breaks().
    """
    sentences = [[]]
    for i, word in enumerate(words):
        if word == marker:
            sentences.append([])
        else:
            sentences[-1].append(word)
    return [s for s in sentences if len(s) > 0]

#--- LISTS -------------------------------------------------------------------------------------------

list_marker = re.compile("^(\d+\.|\d+\)|\*|\-|[a-z]\.|[a-z]\))$") # 1. 1) * - a. a)

def split_lists(words=[], marker=SENTENCE_BREAK):
    """ Adds sentence breaks before list item markers.
        A list item marker is only taken into account when at the start of a new line.
        Occurences of HTML_LIST_ITEM (i.e. <li>, see strip_tags()) also get a sentence break.
        There is no continuity check, e.g. 2) followed by a) is also regarded as a list.
    """
    p = []
    for i, word in enumerate(words):
        if word == HTML_LIST_ITEM:
            p.append(marker)
        elif i==0 or words[i-1] == "\n" and list_marker.search(word):
            p.append(marker)
            p.append(word)
        elif i>0 and words[i-1] == "\n":
            # If a linebreak occured and no list item follows,
            # this marks the end of the list. Add a sentence break.
            p.append(marker)
            p.append(word)
        else:
            p.append(word)
    return p

######################################################################################################

# Punctuation replacements for unicode characters.
# This makes our life easier - in the rest of the module we can simply work with ' and ".
unicode_replacements = {
    u"‘’‚‛`´ʹʻʼʾʿˋˊ˴" : "'",   # Single quote lookalikes.
         u"“”„‟ʺˮ˵˶˝" : "\"",  # Double quote lookalikes.
                 u"…" : "...", # Unicode ellipsis.
                 u"«" : "<<",
                 u"»" : ">>",
}

def split(string, tags=True, replace=unicode_replacements):
    """ Splits the string into a list of sentences.
        Punctuation is split from words as individual tokens.
        With tags=False, removes SGML-tags (i.e. anything resembling "<...>") first.
        The replace dictionary contains (unicode) strings to normalize.
    """
    # Make sure we have a unicode string.
    if isinstance(string, str):
        string = string.decode("utf-8")
    for k,v in replace.items():
        for k in k:
            string = re.sub(k,v, string)
    if not tags:
        string = strip_tags(string)
    # Collapse whitespace and split on each space.
    # We keep \n as a separate token because we still need it to check lists and hyphenation.
    words = split_words(string, keep="\n")
    words = split_lists(words)
    words = split_hyphenation(words)
    words = [word for word in words if word != "\n"]
    # Split words with missing spaces, contractions, etc.
    # Keep list item markers at the start of the sentence intact - see split_lists().
    p = []
    list_marker_encounter=None
    for i, word in enumerate(words):
        list_marker_char = list_marker.search(word)
        if list_marker_char is not None:
            if i==0 or words[i-1] == SENTENCE_BREAK:
                p.append(word)
                
                try:
                    list_marker_encounter=int(list_marker_char.group().rstrip('.'))
                except ValueError:
                    pass
                                        
            elif list_marker_encounter is not None:
                try:
                    clm = int(list_marker_char.group().rstrip('.'))
                except ValueError:
                    pass
                    
                # For a very special case like in:
                # The number of SMemb-positive glomerular cells increased on days 2 and 4. 4 .
                # We examined whether levels of alpha-smooth-muscle actin
                # Where the second 4. is the listmarker
                if i < len(words)-1:
                    try:
                        next=int(list_marker.search(words[i+1]).group().rstrip('.'))
                    except Exception:
                        #Nice try but just go one
                        pass
                    else:
                        if next == clm:
                            #This means that we are in the special case (the first 4.), so just split this occurrence
                            p.extend(split_word(word))
                            continue
                            
                if clm == list_marker_encounter+1:
                    # Only don't split 2. etc. if we already saw a listmarker 1.
                    p.append(word)
                    list_marker_encounter = clm
                else:
                    #Split normally
                    p.extend(split_word(word))
            else:
                #Split normally
                p.extend(split_word(word))
        else:
            p.extend(split_word(word))
    # Add sentence breaks after periods and other punctuation that indicate the end of the sentence.
    # Parse sentence breaks and create a list of individual sentence strings.
    p = add_sentence_breaks(p)
    p = split_sentences(p)
    p = [" ".join(sentence) for sentence in p]
    
    if tags:
        check(string, '\n'.join(p))
    
    return p
    
def split2(string, tags=True, replace=unicode_replacements):
    """ Does NOT split the string into a list of sentences.
        Punctuation is split from words as individual tokens.
        With tags=False, removes SGML-tags (i.e. anything resembling "<...>") first.
        The replace dictionary contains (unicode) strings to normalize.
    """
    # Make sure we have a unicode string.
    if isinstance(string, str):
        string = string.decode("utf-8")
    for k,v in replace.items():
        for k in k:
            string = re.sub(k,v, string)
    if not tags:
        string = strip_tags(string)
    # Collapse whitespace and split on each space.
    # We keep \n as a separate token because we still need it to check lists and hyphenation.
    words = split_words(string, keep="\n")
    words = split_lists(words)
    words = split_hyphenation(words)
    words = [word for word in words if word != "\n"]
    # Split words with missing spaces, contractions, etc.
    # Keep list item markers at the start of the sentence intact - see split_lists().
    p = []
    for i, word in enumerate(words):
        if i==0 or words[i-1] == SENTENCE_BREAK and list_marker.search(word) != None:
            p.append(word)
        else:
            try:
                p.extend(split_word(word))
            except Exception:
                print >>sys.stderr, 'ERROR', words
                raise
    # Add sentence breaks after periods and other punctuation that indicate the end of the sentence.
    # Parse sentence breaks and create a list of individual sentence strings.
    #p = add_sentence_breaks(p)
    p = split_sentences(p)
    p = [" ".join(sentence) for sentence in p]
    
    if tags:
        check(string, '\n'.join(p))
    
    return p
    
    
def sentence_split(string, tags):
    '''Splits in sentences without tokenisation
    
    tags: not used'''
    string = string.decode('utf8')
    
    output=[]
    i=0
    start=0
    stop=0
    data = split(string)
    for s in data:
        for c in s:
            if c == string[i]:
                stop+=1
                i+=1
            elif c.strip():
                if string[i].strip():
                    print 'c', repr(c)
                    print 'i', i
                    print 'string[i]', repr(string[i])
                    print 'ss', start, stop, repr(string[start:stop])
                    raise ValueError('Not alignable')
                else:
                    while not string[i].strip():
                        i+=1
                        stop+=1
                    if c == string[i]:
                        stop+=1
                        i+=1
                    elif c.strip():
                        print 'c', repr(c)
                        print 'i', i
                        print 'string[i]', repr(string[i])
                        print 'ss', start, stop, repr(string[start:stop])
                        raise ValueError('Not alignable 2')
                        
                    
        #We got all chars
        output.append(string[start:stop].strip())
        start = stop
        stop = start
        
    if stop != len(string.strip()):
        print >>sys.stderr, 'stop', stop
        print >>sys.stderr, 'len', len(string.strip())
        print 'output', output
        raise ValueError('Did not cover all chars')
        
    if len(output) != len(data):
        raise ValueError('Did retrieve all sentences')
        
    return output
    
    
    
    
    
    

#####################################################################################################

def check(original, tokenized):
    '''Takes the original string and the tokenized string and returns True if every non-white character
    of original is in tokenized. Otherwise raises an error'''
    if ''.join(original.split()) != ''.join(tokenized.split()):
        print >>sys.stderr, 'Original:', original
        print >>sys.stderr, 'O', len(''.join(original.split())), ''.join(original.split())
        print >>sys.stderr, 'T', len(''.join(tokenized.split())), ''.join(tokenized.split())
        raise ValueError('not the same chars')
    
    return True
    
######################################################################################################

test1 = u"""
The U.S. Army likes Shock and Awe. 
U.N. regulations are not a part of their concern–Isn't it? 
Yes! "I'd rather have a walk", Ms. Comble sighed. 
'Me too!', Mr. P. Delaware cried. 
They ran about 10km.
But then the 6,000-year ice age came...
"""

test2 = u"""
From “The Eskimo Cookbook”:
1. cut the flippers off from the oogruk
2. put the flippers in fresh blubber
3. let them stay there for about two weeks
4. take the loose fur off the flipper
5. cut flipper into small pieces and eat the meat
http://www.recipesource.com/ethnic/americas/eskimo/oogruk-flippers1.html
"""


def _usage():
    print >>sys.stderr, '''
Tokenizes raw texts.

USAGE
    python tokenizer.py [-s|-n] txtfile > output
    
OPTIONS
   -s: Don't split into tokens only split into sentences.
   -n: Don't split into sentences; only split into tokens.
   
REMARKS
    Assumes UTF8 encoded input    
    
%s (version %s)''' %(__date__, __version__)


if __name__ == '__main__':
    try:
        opts,args=getopt.getopt(sys.argv[1:],'nsh', ['help'])
    except getopt.GetoptError:
        # print help information and exit:
        _usage()
        sys.exit(2)

    nosentencesplit = False
    notokenisation = False

    for o, a in opts:
        if o in ('-h', '--help'):
            _usage()
            sys.exit()
        if o in ('-n',):
            # Don't split sentences
            nosentencesplit =True 
        if o in ('-s',):
            # Only split sentences
            notokenisation = True
            
    if nosentencesplit and notokenisation:
        print >>sys.stderr , 'Error: you can only specify either option -n or option -s'
        sys.exit(1)
                
    if len(args) != 1:
        _usage()
        sys.exit(1)
    
    
    if nosentencesplit:
        splitter = split2
    elif notokenisation:
        splitter = sentence_split
    else:
        splitter = split


    f = open(args[0], 'rU')
    try:
        for string in f:
            string = string.strip()
        
            if string:
                print '\n'.join(splitter(string, tags=True)).encode('utf8')
        
    finally:
        f.close()
    
