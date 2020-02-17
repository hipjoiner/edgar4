import json

from edgar4.config import log
from edgar4 import companies
from edgar4.company import Company
from edgar4.filing import Filing


log('Start...')

# Find all matches for a search term
start = 'Microsoft'
matches = companies.matches(start)
log('Matches for "{}":\n'.format(start) + json.dumps(matches, indent=4))

# Use a match that looks good to instantiate a Company
cik = '0000789019'
name = 'Microsoft Corp'
company = Company(cik, name)
log('Instantiated: {}'.format(company))
log('Company URL: {}'.format(company.company_url))

# Get all filings for the company
for filing in company.filings():
    log('Filing data:\n{}'.format(json.dumps(filing, indent=4)))
print('')

all_10qs = company.filings('10-Q')
log('10-Qs:\n{}'.format(json.dumps(all_10qs, indent=4)))
last_10q = all_10qs[0]

# Get all documents associated with 10-Q filing
f = Filing(last_10q)
log('Filing:\n{}'.format(f))
docs = f.documents
print(docs)
