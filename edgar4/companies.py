from functools import lru_cache
import json
import os
import requests

from edgar4.config import base_url, home, log


data_path = 'Archives/edgar/cik-lookup-data'
url = '%s/%s.txt' % (base_url, data_path)
cache_raw = '%s/%s.txt' % (home, data_path)
cache_json = '%s/%s.json' % (home, data_path)


@lru_cache()
def all_companies():
    if os.path.isfile(cache_json):
        with open(cache_json, 'r') as fp:
            data = json.load(fp)
    else:
        os.makedirs(os.path.dirname(cache_raw), exist_ok=True)
        raw_text = requests.get(url).content.decode("latin1")
        with open(cache_raw, 'w') as fp:
            fp.write(raw_text)
        data = transform_raw(raw_text)
        with open(cache_json, 'w') as fp:
            json.dump(data, fp, indent=4)
    return data


def cik_from_name(name):
    result = list(matches(name, split=False).keys())
    if len(result) != 1:
        raise ValueError('"%s" does not map to a unique CIK; matches:\n%s' % (name, result))
    return result[0]


def is_unique(tag, split=True):
    return len(matches(tag, split=split)) == 1


@lru_cache()
def matches(words, split=True):
    if not split:
        tags = [str(words).lower()]
    else:
        tags = words.lower().split(' ')
    data = all_companies()
    # The trivial case: exact match
    if len(tags) == 1 and tags[0] in data:
        cik, name = data[tags[0]]
        return {cik: name}
    # No exact match.  Do it the hard way.
    results = {}
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
    result = list(matches(cik, split=False).values())
    if len(result) != 1:
        raise ValueError('CIK %s does not map to a unique name; matches:\n%s' % (cik, result))
    return result[0]


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
        data[name.lower()] = [cik, name]
        data[cik] = [cik, name]
    return data
