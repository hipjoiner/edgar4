from functools import lru_cache
import json
import os
import requests

from edgar4.config import base_url, home, log


data_path = 'Archives/edgar/cik-lookup-data.txt'
url = '%s/%s' % (base_url, data_path)
cache_fpath = '%s/%s' % (home, data_path)


@lru_cache()
def all_companies():
    if os.path.isfile(cache_fpath):
        log('Loading from %s...' % cache_fpath)
        with open(cache_fpath, 'r') as fp:
            data = json.load(fp)
    else:
        log('Loading from %s...' % url)
        raw_text = requests.get(url).content.decode("latin1")
        data = transform_raw(raw_text)
        log('Writing to %s...' % cache_fpath)
        os.makedirs(os.path.dirname(cache_fpath), exist_ok=True)
        with open(cache_fpath, 'w') as fp:
            json.dump(data, fp)
    return data


def cik_from_name(name):
    if not is_unique(name, split=False):
        raise ValueError('"%s" does not map to a unique CIK' % name)
    return list(matches(name).keys())[0]


def is_unique(tag, split=True):
    return len(matches(tag, split=split)) == 1


@lru_cache()
def matches(words, split=True):
    if not split:
        tags = [str(words).lower()]
    else:
        tags = words.lower().split(' ')
    results = {}
    data = all_companies()
    for key, (cik, name) in data.items():
        hit = True
        for t in tags:
            if t not in cik and t not in name.lower():
                hit = False
                break
        if hit:
            results[cik] = name
    return results


def name_from_cik(cik):
    if not is_unique(cik, split=False):
        raise ValueError('"%s" does not map to a unique company name' % cik)
    return list(matches(cik).values())[0]


def test(tag):
    hits = matches(tag)
    log('Matches for "%s": ' % tag)
    for cik, name in hits.items():
        log('  %s (%s)' % (name, cik))
    if not len(hits):
        log('  [No matches]')


def transform_raw(text):
    data = {}
    lines = text.split('\n')
    for line in lines:
        toks = line.split(':')[:-1]
        if len(toks) < 2:
            continue
        name, cik = ':'.join(toks[:-1]), toks[-1]
        if not name or not cik:
            continue
        data[name] = [cik, name]
        data[cik] = [cik, name]
    return data


if __name__ == '__main__':
    # test('Microsoft')
    result = cik_from_name('Microsoft Corp')
    log(result)
