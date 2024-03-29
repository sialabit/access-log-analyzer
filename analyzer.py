import os
import sys
import getopt
import re
from glob import glob
from datetime import datetime, date, time
import json
import argparse
import hashlib
from pprint import pprint

from termcolor import colored
import apache_log_parser

LOG_DIR = './sample-logs'
CACHE_PATH = './cache.json'
MEMORY = 2048
METER_SYM = '■'
MAX_METER_LEN = 50

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
    if not re.match(r'^\d{4}/(?:0?[1-9]|1[0-2])/(?:0?[1-9]|[12]\d|3[01])(?::\d{1,2})?$', time_str):
        raise Exception('[Warning] Date format is incorrect') 
         
    h = int( time_str.split(':')[1] ) if ':' in time_str else 0
    y, m, d = map(int, time_str.split(':')[0].split('/'))
    dt = datetime(year=y, month=m, day=d, hour=h)
    return dt.timestamp()

def integrate_cnts(data):
    rtn = {}
    for d in data:
        for ts in d:
            rtn[ts] = rtn.get(ts, 0) + d[ts]
    return rtn

def filter_hour(data, start, end):
    rtn = {}
    for ts in data:
        ts_n = float(ts)
        if start and end:
            if not (start <= ts_n and ts_n <= end):
                continue
        elif start:
            if ts_n < start:
                continue
        elif end:
            if ts_n > end:
                continue
        rtn[ts] = data[ts]
    return rtn

def time_cmd_handler(args):
    each_hour = []

    search_opt = { 'start': None, 'end': None } 
    for k in ['start', 'end']:
        search_opt[k] = parse_time_str(getattr(args, k)) if getattr(args, k) else None
    
    with open(CACHE_PATH, 'r') as cachefile:
        cache = json.load(cachefile) 

    for fname in glob(os.path.join(LOG_DIR, '*.log')):

        is_same = False
        hash = md5(fname)
        abspath = os.path.abspath(fname)
        this_cache = {}

        if not abspath in cache.keys():
            cache[abspath] = {
                    'hash': hash,
                    'results': { 'time': {}, 'ip': {} }}    
            this_cache = cache[abspath]
        else:
            this_cache = cache[abspath]
            if this_cache['hash'] == hash:
                is_same = True
            else:
                cache[abspath]['hash'] = hash

        if is_same and this_cache['results']['time']:
            each_hour.append(this_cache['results']['time'])
        else:
            data = {}

            with open(fname) as f:
                for l in f:
                    parsed = line_parser(l)
                    ts = resided_ts(parsed['time_received_tz_datetimeobj'])


                    data[ts] = data.get(ts, 0) + 1

            each_hour.append(data)
            this_cache['results']['time'] = data

    each_hour = integrate_cnts(each_hour)
    each_hour = filter_hour(each_hour, **search_opt)

    # response
    for ts in sorted(each_hour, key=float, reverse=args.reverse):
        num_ts = float(ts)
        dt = datetime.fromtimestamp(num_ts)
        cnt = each_hour[ts]

        if args.graph:
            max = 0 
            for c in each_hour:
                max = each_hour[c] if max < each_hour[c] else max

            print('{0} {1}\t{2}'.format(dt.strftime('%Y/%m/%d:%H:%M~\t'), cnt, METER_SYM*int(MAX_METER_LEN*cnt/max)))
        else:
            print(dt.strftime('%Y/%m/%d:%H:%M~\t'), cnt)
    
    with open(CACHE_PATH, 'w+') as f:
        json.dump(cache, f)

def ip_cmd_handler(args):
    each_ip = []

    with open(CACHE_PATH, 'r') as cachefile:
        cache = json.load(cachefile) 

    for fname in glob(os.path.join(LOG_DIR, '*.log')):

        is_same = False
        hash = md5(fname)
        abspath = os.path.abspath(fname)
        this_cache = {}

        if not abspath in cache.keys():
            cache[abspath] = {
                    'hash': hash,
                    'results': { 'time': {}, 'ip': {} }}    
            this_cache = cache[abspath]
        else:
            this_cache = cache[abspath]
            if this_cache['hash'] == hash:
                is_same = True
            else:
                cache[abspath]['hash'] = hash

        if is_same and this_cache['results']['ip']:
            each_ip.append(this_cache['results']['ip'])
        else:
            data = {}

            with open(fname) as f:
                for l in f:
                    ip = l.split()[0]
                    data[ip] = data.get(ip, 0) + 1 
            each_ip.append(data)

            each_ip.append(data)
            this_cache['results']['ip'] = data

    each_ip = integrate_cnts(each_ip)

    # response
    for ip in sorted(each_ip, key=each_ip.__getitem__, reverse=args.reverse):
        cnt = each_ip[ip] 

        if args.graph:
            max = 0 
            for c in each_ip:
                max = each_ip[c] if max < each_ip[c] else max

            print('{0}\t{1}\t{2}'.format(ip, cnt, METER_SYM*int(MAX_METER_LEN*cnt/max)))
        else:
            print('{0}\t{1}'.format(ip, cnt))

    with open(CACHE_PATH, 'w+') as f:
        json.dump(cache, f)

def main():
    if not os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'w') as f:
            f.write('{}')

    cmd_parser = argparse.ArgumentParser(
            description='Analize access.log of Apache.',
            epilog='For show help in detail, <subcommand> --help')
    subcmd_parsers = cmd_parser.add_subparsers(
            title='subcommands'
            )

    parser_time = subcmd_parsers.add_parser('time')
    parser_time.add_argument('-s', '--start', help='Specify date after which number of accesses. FORMAT:"YYYY/MM/DD" or "YYYY/MM/DD:HH"')
    parser_time.add_argument('-e', '--end', help='Specify date before which number of accesses')
    # parser_time.add_argument('-o', '--output')
    parser_time.add_argument('-g', '--graph', action='store_true', help='show graphicaly')
    parser_time.add_argument('-r', '--reverse', action='store_true', help='show in descending')
    parser_time.set_defaults(handler=time_cmd_handler)

    parser_ip = subcmd_parsers.add_parser('ip')
    parser_ip.add_argument('-r', '--reverse', action='store_true', help='show in descending')
    parser_ip.add_argument('-g', '--graph', action='store_true', help='show graphicaly')
    parser_ip.set_defaults(handler=ip_cmd_handler)

    args = cmd_parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        if len(sys.argv) >= 2:
            print(colored('[Warning] no such a sub-command', 'red'), end='\n\n')
            cmd_parser.print_help()
        else:
            print(colored('[Warning] Include any sub-command', 'red'), end='\n\n')
            cmd_parser.print_help()

main()
