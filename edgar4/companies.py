import os
import requests

from edgar4.config import sec_url, cache_dir


url = '{}/Archives/edgar/cik-lookup-data.txt'.format(sec_url)
cache_fpath = '{}/cik-lookup-data.txt'.format(cache_dir)


def matches(words):
    tags = words.lower().split(' ')
    results = []
    for line in raw_text():
        lline = line.lower()
        hit = True
        for t in tags:
            if t not in lline:
                hit = False
                break
        if hit:
            results.append(line)
    return results


def raw_text():
    if os.path.isfile(cache_fpath):
        with open(cache_fpath, 'r') as fp:
            return fp.read().split('\n')
    raw = requests.get(url).content.decode("latin1")
    os.makedirs(os.path.dirname(cache_fpath), exist_ok=True)
    with open(cache_fpath, 'w') as fp:
        fp.write(raw)
    return raw.split('\n')


if __name__ == '__main__':
    print(matches('Microsoft'))
