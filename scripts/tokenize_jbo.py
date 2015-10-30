"""
Script to tokenize Lojban text.
"""
import sys
import re

def tokenize(text):
    tokens = re.split(' +', text)
    return tokens


def main():
    """Main function"""
    for line in sys.stdin:
        tokens = tokenize(line.rstrip())
        print ' '.join(tokens)

if __name__ == '__main__':
    main()
