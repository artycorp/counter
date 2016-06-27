import time
import sys
import json
import datetime
import argparse
import os
import logging

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from stem import Signal
from stem.control import Controller

from rfoo.utils import rconsole

SETTINGS_FILE = os.getenv('COUNTER_SETTINGS_PATH','') + "settings.json"

class Search:
    browser = None
    profile = None
    query = None
    CITY = u'Perm'

    def __init__(self, query):
        self.query = query["text"]
        self.browser = None


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.destroy()

    def destroy(self):
        self.browser.stop_client()
        self.browser.quit()

    #disable image and flash
    def DisableImages(self):
        self.profile.set_preference('permissions.default.stylesheet', 2)
        self.profile.set_preference('permissions.default.image', 2)
        self.profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

    # settings for TOR connect
    def initPreference(self):
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('network.proxy.type', 1)
        self.profile.set_preference('network.proxy.socks', '127.0.0.1')
        self.profile.set_preference('network.proxy.socks_port', 9050)

    def initYandex(self):
        self.browser = webdriver.Firefox(self.profile)
        try:
            self.browser.maximize_window()
            self.browser.get('https://www.yandex.ru/')

            self.setRegion()
            time.sleep(3)
            self.submitRegion()
            time.sleep(3)
            ###browser.implicitly_wait(2)
        except:
            return False
        return True

    def Search(self):
        if self.checkNeedTorRestart():
            
        self.findQueryYA()

    # set location to Perm
    def setRegion(self):
        self.browser.get('https://tune.yandex.ru/region/?retpath=https%3A%2F%2Fyandex.ru%2F%3Fdomredir%3D1&amp;laas=1')

        # checkbox
        elem = self.browser.find_element_by_id("auto")
        elem.click()

        region = self.browser.find_element_by_xpath("//input[@name='name']")

        region.clear()
        time.sleep(3)

        ActionChains(self.browser) \
            .move_to_element(region) \
            .click(region) \
            .send_keys_to_element(region, self.CITY) \
            .send_keys_to_element(region, Keys.ENTER) \
            .click(region) \
            .double_click(region) \
            .perform()

    # submit region
    def submitRegion(self):
        btn = self.browser.find_element_by_xpath("//input[@type='submit']")

        try:
            ActionChains(self.browser) \
                .move_to_element(btn) \
                .send_keys_to_element(btn, Keys.ENTER) \
                .perform()
        except:
            logging.error("Submit Region error")

    # search query string in yandex
    def findQueryYA(self):
        search = self.browser.find_element_by_xpath("//input[@id='text']")
        ActionChains(self.browser) \
            .send_keys(Keys.HOME) \
            .send_keys(self.query) \
            .send_keys(Keys.ENTER) \
            .perform()

        #search.submit()
    def restartTor(self):
        with Controller.from_port(port=9051) as controller:
            controller.authenticate("Den135790")
            controller.signal(Signal.NEWNYM)

    # check yandex errors
    def checkNeedTorRestart(self):
        res = self.browser.find_elements_by_xpath(u"//p[contains(text(),'Нам очень жаль')]")
        return len(res) > 0

def loadSettings():
    json_data = None
    with open(SETTINGS_FILE) as json_file:
        json_data = json.load(json_file)
        # print(json_data)
    return json_data['search_texts']

def main():
    try:
        search_texts = loadSettings()
    except:
        logging.error("Cannot read {0}".format(SETTINGS_FILE))
        exit(1)
    for search_text in search_texts:
        try:
            with Search(query=search_text) as ya:
                ya.restartTor()
                ya.initPreference()
                ya.initYandex()
                ya.Search()
                time.sleep(10)
                print("exit!")
        except:
            logging.error("Cannot search {0}".format(search_text))

if __name__ == "__main__":
    main()