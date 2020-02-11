from edgar4.config import log
from edgar4.companies import matches, cik_from_name, is_unique


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


if __name__ == '__main__':
    # test('Microsoft')
    test2()
    # cik_from_name('Microsoft')
    # log(is_unique('Microsoft'))
