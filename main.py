#!/usr/bin/env python3

import os
import sys
import toml
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

log = logging.getLogger('AutoReport')
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter('[%(asctime)s %(levelname)s] %(message)s'))
log.addHandler(handler)

try:
    with open(os.path.join(os.path.dirname(__file__), 'conf.toml')) as f:
        conf = toml.loads(f.read())
except:
    log.critical('cannot open conf.toml')
    sys.exit(-1)

options = Options()
options.headless = conf['firefox']['headless']
profile = webdriver.FirefoxProfile()
profile.set_preference('network.proxy.type', 0)
ff = webdriver.Firefox(profile, options=options)
log.info('Firefox started')

log.debug('Loading login page')
ff.get('https://thos.tsinghua.edu.cn')
log.info('Login page loaded')

username = ff.find_element_by_id('i_user')
username.send_keys(conf['credentials']['username'])
password = ff.find_element_by_id('i_pass')
password.send_keys(conf['credentials']['password'])
log.debug('Ready to submit credentials')
password.submit()
log.info('Logged in')

ff.implicitly_wait(30)
log.debug('Finding daily')
daily = ff.find_element_by_css_selector('div[serveid=d42b05be-1ad8-4d96-8c1e-14be2bb24e26]')
daily.click()
log.info('Entered daily report page')

log.info('Waiting for the form to be loaded')
wait(ff, 60).until(EC.invisibility_of_element((By.ID, 'exam-loader-text')))
wait(ff, 60).until(EC.frame_to_be_available_and_switch_to_it('formIframe'))
log.info('The iframe loaded')

ff.switch_to.parent_frame()
log.debug('Ready for commiting the daily report')
commit_btn = ff.find_element_by_id('commit')
commit_btn.click()
log.info('Daily report commited')

wait(ff, 10).until(EC.presence_of_element_located((By.ID, 'procinst_id')))
log.info('Successfully commited the daily report')

log.debug('Browser quit')
ff.quit()
