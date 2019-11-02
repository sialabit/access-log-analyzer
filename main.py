import os
import sys
import getopt
import glob

import hashlib

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


def main():
    cmd_handler()

    for fname in glob.glob(os.path.join(LOG_DIR, '*.log')):
        with open(fname) as f:
            for l in f:
                data.append(l)

    print(len(data))

main()
