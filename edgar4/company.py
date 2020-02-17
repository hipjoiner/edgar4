from functools import lru_cache
from lxml import html, etree
import os
import requests

from edgar4.config import home


base_url = 'https://www.sec.gov'


class Company:
    def __init__(self, name, cik):
        self.name = name
        self.cik = cik
        self._document_urls = []

    @property
    def base_url(self):
        return 'https://www.sec.gov'

    @property
    @lru_cache()
    def company_info(self):
        doc = requests.get(self.company_url).content
        page = html.fromstring(doc)
        if page.xpath("//div[@class='companyInfo']"):
            return page.xpath("//div[@class='companyInfo']")[0]
        return None

    @property
    @lru_cache()
    def sic(self):
        if self.company_info:
            indent_info = self.company_info.getchildren()[1]
            if len(indent_info.getchildren()) > 2:
                return indent_info.getchildren()[1].text
        return ''

    @property
    @lru_cache()
    def us_state(self):
        if self.company_info:
            indent_info = self.company_info.getchildren()[1]
            if len(indent_info.getchildren()) > 4:
                return indent_info.getchildren()[3].text
        return ''

    @property
    def company_url(self):
        return '%s/cgi-bin/browse-edgar?action=getcompany&CIK=%s' % (self.base_url, self.cik)

    @property
    def document_urls(self):
        return list(set(self._document_urls))

    def get_filings_url(self, filing_type="", prior_to="", ownership="include", no_of_entries=100):
        url = self.company_url + \
              "&type=" + filing_type + \
              "&dateb=" + prior_to + \
              "&owner=" + ownership + \
              "&count=" + str(no_of_entries)
        return url

    def get_all_filings(self, filing_type="", prior_to="", ownership="include", no_of_entries=100):
        url = self.get_filings_url(filing_type, prior_to, ownership, no_of_entries)
        page = requests.get(url)
        return html.fromstring(page.content)

    def group_document_type(self, tree, document_type):
        result = []
        grouped = []
        for i, elem in enumerate(tree.xpath('//*[@id="seriesDiv"]/table/tr')):
            if i == 0:
                continue
            url = elem.xpath("td")[1].getchildren()[0].attrib["href"]
            grouped.append(url)
            if elem.xpath("td")[0].text == document_type:
                result.append(grouped)
                grouped = []
        return result

    def get_document_type_from_10k(self, document_type, no_of_documents=1):
        tree = self.get_all_filings(filing_type="10-K")
        url_groups = self.group_document_type(tree, "10-K")[:no_of_documents]
        result = []
        for url_group in url_groups:
            for url in url_group:
                url = self.base_url + url
                self._document_urls.append(url)
                content_page = Company.get_request(url)
                table = content_page.find_class("tableFile")[0]
                for row in table.getchildren():
                    if document_type in row.getchildren()[3].text:
                        href = row.getchildren()[2].getchildren()[0].attrib["href"]
                        href = self.base_url + href
                        doc = Company.get_request(href)
                        result.append(doc)
        return result

    def get_data_files_from_10k(self, document_type, no_of_documents=1, isxml=False):
        tree = self.get_all_filings(filing_type="10-K")
        url_groups = self.group_document_type(tree, "10-K")[:no_of_documents]
        result = []
        for url_group in url_groups:
            for url in url_group:
                url = self.base_url + url
                self._document_urls.append(url)
                content_page = Company.get_request(url)
                table_file = content_page.find_class("tableFile")
                if len(table_file) < 2:
                    continue
                table = table_file[1]
                for row in table.getchildren():
                    if document_type in row.getchildren()[3].text:
                        href = row.getchildren()[2].getchildren()[0].attrib["href"]
                        href = self.base_url + href
                        doc = Company.get_request(href, isxml=isxml)
                        result.append(doc)
        return result

    def get_10ks(self, no_of_documents=1):
        tree = self.get_all_filings(filing_type="10-K")
        elems = tree.xpath('//*[@id="documentsbutton"]')[:no_of_documents]
        result = []
        for elem in elems:
            url = self.base_url + elem.attrib["href"]
            content_page = Company.get_request(url)

            cache_fpath = home + elem.attrib['href']
            print('Cache fpath: %s' % cache_fpath)
            if not os.path.isfile(cache_fpath):
                os.makedirs(os.path.dirname(cache_fpath), exist_ok=True)
                with open(cache_fpath, 'w') as fp:
                    text = html.tostring(content_page).decode()
                    fp.write(text)

            table = content_page.find_class("tableFile")[0]
            last_row = table.getchildren()[-1]
            href = last_row.getchildren()[2].getchildren()[0].attrib["href"]
            cache_fpath = home + href
            doc_url = self.base_url + href
            doc = Company.get_request(doc_url)
            result.append(doc)

            print('Cache fpath: %s' % cache_fpath)
            if not os.path.isfile(cache_fpath):
                os.makedirs(os.path.dirname(cache_fpath), exist_ok=True)
                with open(cache_fpath, 'w') as fp:
                    text = html.tostring(doc).decode()
                    fp.write(text)

        return result

    def get_10k(self):
        return self.get_10ks(no_of_documents=1)[0]

    @classmethod
    def get_request(cls, href, isxml=False):
        page = requests.get(href)
        if isxml:
            p = etree.XMLParser(huge_tree=True)
            return etree.fromstring(page.content, parser=p)
        else:
            return html.fromstring(page.content)

    @classmethod
    def get_documents(cls, tree, no_of_documents=1):
        elems = tree.xpath('//*[@id="documentsbutton"]')[:no_of_documents]
        result = []
        for elem in elems:
            url = base_url + elem.attrib["href"]
            content_page = cls.get_request(url)
            print("URL:", url)
            print("FORM:", content_page.find_class("formContent")[0].text_content())
            url = base_url + content_page.xpath('//*[@id="formDiv"]/div/table/tr[2]/td[3]/a')[0].attrib["href"]
            filing = cls.get_request(url)
            result.append(filing)
        return result

    @classmethod
    def get_cik_from_company(cls, company_name):
        tree = cls.get_request("https://www.sec.gov/cgi-bin/browse-edgar?company=" + company_name)
        cik_list = tree.xpath('//*[@id="seriesDiv"]/table/tr[*]/td[1]/a/text()')
        names_list = []
        for elem in tree.xpath('//*[@id="seriesDiv"]/table/tr[*]/td[2]'):
            names_list.append(elem.text_content())
        return list(zip(cik_list, names_list))


def test():
    com = Company("Oracle Corp", "0001341439")
    tree = com.get_all_filings(filing_type="10-K")
    return Company.get_documents(tree)
