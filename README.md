# Access Log Analyzer
Access Log Analyzer shows number of accesses either per hour or per IP from access.log created by Apache.

## Environment

```
$ python --version
Python 3.7.3
```

## Features

- When analyzing same access.log, it is more faster to complete from the second time because of caching.
- You can specify a order; ascending or descending.
- This can show in graphicaly

ex)
```
$ python analyzer.py ip --graph
...
14.160.65.22	50	■■■■■
50.139.66.106	52	■■■■■
66.249.73.185	56	■■■■■
208.91.156.11	60	■■■■■■
65.55.213.73	60	■■■■■■
108.171.116.194	65	■■■■■■
208.115.113.88	74	■■■■■■■
198.46.149.143	82	■■■■■■■■
208.115.111.72	83	■■■■■■■■
100.43.83.137	84	■■■■■■■■
68.180.224.225	99	■■■■■■■■■■
209.85.238.199	102	■■■■■■■■■■
50.16.19.13	113	■■■■■■■■■■■
75.97.9.59	273	■■■■■■■■■■■■■■■■■■■■■■■■■■■■
130.237.218.86	357	■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
46.105.14.53	364	■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
66.249.73.135	482	■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
...
```

## Usage

```
$ python analyzer.py time --help

usage: analyzer.py time [-h] [-s START] [-e END] [-g] [-r]

optional arguments:
  -h, --help            show this help message and exit
  -s START, --start START
                        Specify date after which number of accesses.
                        FORMAT:"YYYY/MM/DD" or "YYYY/MM/DD:HH"
  -e END, --end END     Specify date before which number of accesses
  -g, --graph           show graphicaly
  -r, --reverse         show in descending
```

```
$ python analyzer.py ip

usage: analyzer.py ip [-h] [-r] [-g]

optional arguments:
  -h, --help     show this help message and exit
  -r, --reverse  show in descending
  -g, --graph    show graphicaly --help
```

## Note
I used sample Apache log files from [here](https://raw.githubusercontent.com/elastic/examples/master/Common%20Data%20Formats/apache_logs/apache_logs) and fixed it.
