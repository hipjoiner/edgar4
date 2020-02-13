from edgar4.config import log
from edgar4.companies import matches, cik_from_name, is_unique, cache_json
from edgar4.company import Company


def test(tag):
    hits = matches(tag)
    log('Matches for "%s": ' % tag)
    for cik, name in hits.items():
        log('  %s (%s)' % (name, cik))
    if not len(hits):
        log('  [No matches]')


def test2():
    val = 'Microsoft Corp'
    result = cik_from_name(val)
    log('CIK for "%s" is %s' % (val, result))


def test3():
    name = 'Microsoft Corp'
    cik = cik_from_name(name)
    c = Company(name, cik)
    doc = c.get_10k()
    print(doc)


if __name__ == '__main__':
    # test('Microsoft')
    # test2()
    # print(cik_from_name('Microsoft Corp'))
    # log(is_unique('Microsoft'))
    # print(cache_fpath)
    test3()
