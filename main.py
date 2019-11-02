import os
import sys
import getopt
import glob
from datetime import datetime, date, time
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
        print(str(err))

def line_parser(line):
    parser = apache_log_parser.make_parser('%h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i"')
    return parser(line)

def resided_ts(dt):
    resided_dt = dt.replace(minute=0, second=0, microsecond=0) 
    return resided_dt.timestamp()

data = []

def main():
    cmd_handler()

    each_hour = {}

    for fname in glob.glob(os.path.join(LOG_DIR, '*.log')):
        with open(fname) as f:
            for l in f:
                # data.append(line_parser(l))
                parsed = line_parser(l)
                ts = resided_ts(parsed['time_received_tz_datetimeobj'])

                each_hour[ts] = each_hour.get(ts, 0) + 1
    
    for ts in each_hour:
        num_ts = float(ts)
        dt = datetime.fromtimestamp(num_ts)

        print(dt.strftime('%d/%b/%Y:%H:%M'), each_hour[ts])


main()
