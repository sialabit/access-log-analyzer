import os
import sys
import getopt
import glob
import hashlib
from pprint import pprint

import apache_log_parser

LOG_DIR = "./sample-logs"
MEMORY = 2048

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(MEMORY), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

data = []

def cmd_handler():
    # if not len(sys.argv[1:]):
    #     print('Usage')
        # Usage

    try:
        opts, args = getopt.getopt(
                sys.argv[1:],
                'm:',
                ['mode='])
    except getopt.GetoptError as err:
        print str(err)

def line_parser(line):
    parser = apache_log_parser.make_parser('%h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i"')
    # pprint(parser(line))
    return parser(line)


def main():
    cmd_handler()

    for fname in glob.glob(os.path.join(LOG_DIR, '*.log')):
        with open(fname) as f:
            for l in f:
                data.append(line_parser(l))

main()
