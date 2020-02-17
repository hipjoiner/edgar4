from datetime import datetime
import json
import os


def log(msg=''):
    print('%s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))


app_keyword = 'edgar4'

user_home = os.environ.get('USERPROFILE').replace('\\', '/')

user_appdata = os.environ.get('APPDATA').replace('\\', '/')

appdata = '/'.join([user_appdata, app_keyword])

config_fpath = '/'.join([appdata, 'config.json'])

defaults = {
    'home': '/'.join([user_home, app_keyword]),
}

if not os.path.isfile(config_fpath):
    os.makedirs(appdata, exist_ok=True)
    with open(config_fpath, 'w') as fp:
        json.dump(defaults, fp, indent=4)

with open(config_fpath, 'r') as fp:
    settings = json.load(fp)

home = settings['home']
os.makedirs(home, exist_ok=True)

sec_url = 'https://www.sec.gov'

log_dir = '/'.join([home, 'log'])
os.makedirs(log_dir, exist_ok=True)

cache_dir = '/'.join([home, 'cache'])
os.makedirs(cache_dir, exist_ok=True)
