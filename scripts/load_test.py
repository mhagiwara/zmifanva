import urllib2
import re
import random

TEST_CASES = [
    ('coi', 'jb2en'),
    ('coi ro do', 'jb2en'),
    ('pa', 'jb2en'),
    ('re', 'jb2en'),
    ('ci', 'jb2en'),

    ('Hi!', 'en2jb'),
    ('Hello, everybody.', 'en2jb'),
    ('I go to the market.', 'en2jb'),
    ('1', 'en2jb'),
    ('2', 'en2jb'),
    ('3', 'en2jb')
]


def translate(src, direction):
    src = src.replace(' ', '+')
    response = urllib2.urlopen('http://lojban.lilyx.net/zmifanva/?src=%s&dir=%s' % (src, direction))

    m = re.search(r'<textarea rows="8" cols="40">(.*)', response.read())
    if m:
        return m.group(1)


while True:
    src, direction = random.choice(TEST_CASES)
    print (src, direction, translate(src, direction))
