from bs4 import BeautifulSoup
import json
import os
import requests

from edgar4.config import sec_url, cache_dir


class Company:
    def __init__(self, cik, name):
        self.cik = cik
        self.name = name
        self._all_filings = None
        if os.path.isfile(self.cache_fpath):
            self.load()
        else:
            self.save()

    def __repr__(self):
        return '{} {}'.format(self.name, self.cik)

    @property
    def all_filings(self):
        if self._all_filings is not None:
            return self._all_filings
        self._all_filings = []
        for url in self.filings_urls():
            edgar_str = requests.get(url).text
            soup = BeautifulSoup(edgar_str, 'html.parser')
            table_tag = soup.find('table', class_='tableFile2')
            if table_tag is None:
                break
            rows = table_tag.find_all('tr')
            for row in rows[1:]:  # Skip table header
                cells = row.find_all('td')
                filing = {
                    'filing_type': cells[0].text,
                    'filing_docs_url': sec_url + cells[1].a['href'],
                    'filing_description': cells[2].text.strip(),
                    'filing_date': cells[3].text,
                    'file_film_url': None,
                }
                if cells[4].a:
                    filing['file_film_url'] = sec_url + cells[4].a['href']
                self._all_filings.append(filing)
        return self._all_filings

    @property
    def cache_fpath(self):
        return '{}/{}/company.json'.format(cache_dir, self.cik)

    @property
    def company_url(self):
        return '{}/cgi-bin/browse-edgar?action=getcompany&CIK={}'.format(sec_url, self.cik)

    def filings(self, doc_type=None):
        result = []
        for f in self.all_filings:
            if f['filing_type'] == doc_type:
                result.append(f)
        return result

    def filings_url(self, doc_type=None, dateb=None, owner=None, start=None, count=None):
        url = self.company_url
        if doc_type is not None:
            url += '&type={}'.format(doc_type)
        if dateb is not None:
            url += '&dateb={}'.format(dateb)
        if owner is not None:
            url += '&owner={}'.format(owner)
        if start is not None:
            url += '&start={}'.format(start)
        if count is not None:
            url += '&count={}'.format(count)
        return url

    def filings_urls(self, doc_type=None, dateb=None, owner=None):
        count = 100
        start = 0
        while True:
            url = self.filings_url(doc_type=doc_type, dateb=dateb, owner=owner, start=start, count=count)
            yield url
            start += count

    def load(self):
        with open(self.cache_fpath, 'r') as fp:
            data = json.load(fp)
            self._all_filings = data['filings']

    def save(self):
        data = {
            'cik': self.cik,
            'name': self.name,
            'filings': self.all_filings,
            'url': self.company_url,
        }
        os.makedirs(os.path.dirname(self.cache_fpath), exist_ok=True)
        with open(self.cache_fpath, 'w') as fp:
            json.dump(data, fp, indent=4)


def test():
    com = Company('0001341439', 'Oracle Corp')
    print(com)


if __name__ == '__main__':
    test()
