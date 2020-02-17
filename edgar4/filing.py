from bs4 import BeautifulSoup
import requests


class Filing:
    def __init__(self, data):
        self.filing_type = data['filing_type']
        self.filing_docs_url = data['filing_docs_url']
        self.filing_description = data['filing_description']
        self.filing_date = data['filing_date']
        self.file_film_url = data['file_film_url']
        self._documents = None

    @property
    def documents(self):
        if self._documents is not None:
            return self._documents

        # Obtain HTML for document page
        doc_resp = requests.get(self.filing_docs_url)
        doc_str = doc_resp.text

        # Find the XBRL link
        xbrl_link = ''
        soup = BeautifulSoup(doc_str, 'html.parser')
        table_tag = soup.find('table', class_='tableFile', summary='Data Files')
        rows = table_tag.find_all('tr')
        for row in rows[1:]:        # Skip header row
            cells = row.find_all('td')
            # if 'INS' in cells[3].text:
            if 'XML' in cells[3].text:
                xbrl_link = 'https://www.sec.gov' + cells[2].a['href']
        # Obtain XBRL text from document
        xbrl_resp = requests.get(xbrl_link)
        xbrl_str = xbrl_resp.text
        # Find and print stockholder's equity
        soup = BeautifulSoup(xbrl_str, 'lxml')
        tag_list = soup.find_all()
        for tag in tag_list:
            if tag.name == 'us-gaap:stockholdersequity':
                print("Stockholder's equity: " + tag.text)
