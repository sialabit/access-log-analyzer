import os
import sys
import getopt
from glob import glob
from datetime import datetime, date, time
import argparse
import hashlib
from pprint import pprint

import apache_log_parser

LOG_DIR = './sample-logs'
CACHE_PATH = './cache.json'
MEMORY = 2048

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(MEMORY), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def line_parser(line):
    parser = apache_log_parser.make_parser('%h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i"')
    return parser(line)

def resided_ts(dt):
    resided_dt = dt.replace(minute=0, second=0, microsecond=0) 
    return resided_dt.timestamp()

def parse_time_str(time_str):
    h = int( time_str.split(':')[1] ) if ':' in time_str else 0
    y, m, d = map(int, time_str.split(':')[0].split('/'))
    dt = datetime(year=y, month=m, day=d, hour=h)
    return dt.timestamp()

def time_cmd_handler(args):
    each_hour = {}
    search_opt = { 'start': None, 'end': None } 
    for k in ['start', 'end']:
        search_opt[k] = parse_time_str(getattr(args, k)) if getattr(args, k) else None

    for fname in glob(os.path.join(LOG_DIR, '*.log')):
        with open(fname) as f:
            for l in f:
                parsed = line_parser(l)
                ts = resided_ts(parsed['time_received_tz_datetimeobj'])

                if search_opt['start'] and search_opt['end']:
                    if not (search_opt['start'] <= ts and ts <= search_opt['end']):
                        continue
                elif search_opt['start']:
                    if ts < search_opt['start']:
                        continue
                elif search_opt['end']:
                    if ts > search_opt['end']:
                        continue

                each_hour[ts] = each_hour.get(ts, 0) + 1
    
    for ts in each_hour:
        num_ts = float(ts)
        dt = datetime.fromtimestamp(num_ts)

        print(dt.strftime('%d/%m/%Y:%H:%M~\t'), each_hour[ts])

def ip_cmd_handler(args):
    each_ip = {}

    for fname in glob(os.path.join(LOG_DIR, '*.log')):
        with open(fname) as f:
            for l in f:
                ip = l.split()[0]
                each_ip[ip] = each_ip.get(ip, 0) + 1 

    for ip in sorted(each_ip, key=each_ip.__getitem__, reverse=True):
        print('{0}\t{1}'.format(ip, each_ip[ip]))

def main():
    cmd_parser = argparse.ArgumentParser()
    subcmd_parsers = cmd_parser.add_subparsers()

    parser_time = subcmd_parsers.add_parser('time')
    parser_time.add_argument('-s', '--start')
    parser_time.add_argument('-e', '--end')
    parser_time.add_argument('-o', '--output')
    parser_time.add_argument('-g', '--graph', action='store_true')
    parser_time.set_defaults(handler=time_cmd_handler)

    parser_ip = subcmd_parsers.add_parser('ip')
    parser_ip.add_argument('-r', '--reverse', action='store_true')
    parser_ip.add_argument('-g', '--graph', action='store_true')
    parser_ip.set_defaults(handler=ip_cmd_handler)

    args = cmd_parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        print('no such a sub-command')

main()
