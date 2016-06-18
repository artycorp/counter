#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# from selenium.common.exceptions import NoSuchElementException

# CONSTANTS
CITY = u'Perm'
MAX_SERACHED_PAGE = 50
#YANDEX_XPATH = u"//div/div/span/a[@href='{0}']"
YANDEX_XPATH = u"//a[@href='{0}']"
#/html/body/div[1]/div[5]/div[4]/div[7]/div[1]/div[3]/div/div[3]/div[2]/div/div/div/div/div[1]/div/h3/a
#GOOGLE_XPATH = u"//div[@class='rc']/h3/a[@href='{0}']"
GOOGLE_XPATH = u"//div/h3/a[@href='{0}']"
SETTINGS_FILE = os.getenv('COUNTER_SETTINGS_PATH','') + "settings.json"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

# page = 7
# TODO читать из файла, например в json формате
search_texts = [
    {"text": u'ремонт посудомоечных машин пермь',
     "urls": [u"http://perm-remont.com/"],
     "site_url": 'http://www.orgpage.ru/areas/perm/'},
    # {"text": u'ремонт посудомоечных машин пермь', "urls": [u"http://perm-remont.com/"],
    # "site_url": '/remont-stiralnyh-mashin-v-permi/'},
    {"text": u'ремонт холодильников пермь',
     # "urls": [u"http://holodilniki.perm-remont.com/", u"http://perm-remont.com/"],
     "urls": [u"http://perm-remont.com/"],
     "site_url": '/remont-stiralnyh-mashin-v-permi/'
     # "urls": [u"http://perm.startwithme.ru/remont-ustanovka-bitovoi-tehniki/", u"http://perm-remont.com/"]
     }, {"text": u'ремонт холодильников', "urls": [u"http://perm-remont.com/"],
         "site_url": '/remont-stiralnyh-mashin-v-permi/'}]

fUiLog = open(os.getenv('COUNTER_SETTINGS_PATH','') + "ui.log", "a", 0)

#TODO перепилить
def writeUiLog(fUiLog, searcher, qry, page_cnt, all_cnt, ref):
    dt = d = datetime.datetime.now()
    fUiLog.write("{0} | ".format(d.strftime(DATE_FORMAT)))
    fUiLog.write("{0} | ".format(searcher.encode("utf8")))
    fUiLog.write("{0} | ".format(qry.encode("utf8")))
    fUiLog.write("{0} | ".format(page_cnt))
    fUiLog.write("{0} | ".format(all_cnt))
    fUiLog.write("{0}\n".format(ref.encode("utf8")))


# settings for TOR connect
def initPreference():
    profile = webdriver.FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.socks', '127.0.0.1')
    profile.set_preference('network.proxy.socks_port', 9050)

    #disable image and flash
    profile.set_preference('permissions.default.stylesheet', 2)
    profile.set_preference('permissions.default.image', 2)
    profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    return profile


# set location to Perm
def setRegion(browser):
    browser.get('https://tune.yandex.ru/region/?retpath=https%3A%2F%2Fyandex.ru%2F%3Fdomredir%3D1&amp;laas=1')

    # checkbox
    elem = browser.find_element_by_id("auto")
    elem.click()

    region = browser.find_element_by_xpath("//input[@name='name']")

    region.clear()
    time.sleep(3)

    ActionChains(browser) \
        .move_to_element(region) \
        .click(region) \
        .send_keys_to_element(region, CITY) \
        .send_keys_to_element(region, Keys.ENTER) \
        .click(region) \
        .double_click(region) \
        .perform()


# submit region
def submitRegion(browser):
    btn = browser.find_element_by_xpath("//input[@type='submit']")

    try:
        ActionChains(browser) \
            .move_to_element(btn) \
            .send_keys_to_element(btn, Keys.ENTER) \
            .perform()
    except:
        logging.error("Submit Region error")


# search query string in yandex
def findQueryYA(browser, query):
    search = browser.find_element_by_xpath("//input[@id='text']")
    ActionChains(browser) \
        .send_keys(Keys.HOME) \
        .send_keys(query) \
        .send_keys(Keys.ENTER) \
        .perform()

    #search.submit()


# search query string in google
def findQueryGoogle(browser, query):
    try:
        search = browser.find_elements_by_xpath("//input")
    except:
        logging.error("findQueryGoogle error find element")
    i = 1
    for s in search:
        try:
            time.sleep(4)
            i += 1
            logging.debug(str(i) + " text is " + s.text)
            ActionChains(browser) \
                .click(s) \
                .key_down(Keys.CONTROL, s) \
                .send_keys_to_element(query, s) \
                .key_up(Keys.CONTROL, s) \
                .send_keys_to_element(Keys.ENTER, s) \
                .perform()
            s.submit()
        except:
            logging.error("findQueryGoogle error find element")
            # .send_keys_to_element(query, search) \
            # .send_keys_to_element(Keys.ENTER, search) \


def searchSite(browser, xpath_query, url, link, file):
    bFound = False
    href = None
    try:
        sites = browser.find_elements_by_xpath(xpath_query.format(url))
    except:
        logging.error(u"Error in find_elements_by_xpath by url='{0}'".format(url))
        sites = None
    for site in sites:
        try:
            href = site.get_attribute("href")
            ActionChains(browser) \
                .move_to_element(site) \
                .send_keys_to_element(site, Keys.ENTER) \
                .perform()
            handle = browser.window_handles[1]
            browser.switch_to_window(handle)
            findInSite(browser, link=link)
            browser.switch_to_window(browser.window_handles[0])
            bFound = True
            break
        except:
            # TODO change print to syslog
            bFound = True
            try:
                browser.switch_to_window(browser.window_handles[0])
            except:
                logging.error("Error switching window on Serach site")
            message = "ERROR Cannot click {0} by link {1}\n".format(url, link)
            file.write(message.encode("utf8"))
            logging.error(message.encode("utf8"))
            break
    return {"res":bFound,"href":href}


def searchOnPage(browser, xpath, urls, iPage, query, link, file, cntElems):
    i = 1
    bFound = False
    while i < 9 and not bFound:
        browser.execute_script("window.scrollTo(0, " + str(200 * i) + ");")
        for url in urls:
            posInPage = -1
            try:
                elems = browser.find_elements_by_xpath("//div/div/span/a[@href='{0}']/../../..".format(url))
                #elems = browser.find_elements_by_xpath("//a[@href='http://master-catalog.ru/catalog/perm']/../../..".format(url))

                for elem in elems:
                    try:
                        posInPage = elem.get_attribute("data-cid")
                        #print("!!!!posInPage = {0}".format(posInPage))
                        #TODO грязный хак, чтобы обрабатывался только 1й элемент, у второго нет атрибута data-cid
                        break;
                    except:
                        logging.error("Error in get data-cid")
            except:
                logging.error(u"Error in find posInPage format url={0}".format(url))
            result = searchSite(browser=browser, xpath_query=xpath, url=url, link=link, file=file)
            bFound = result["res"]
            if bFound:
                posInPages = int(posInPage) + cntElems
                d = datetime.datetime.now()
                message = u"{0} link '{1}' Found in yandex on page {2} with Pos = {3} summaryPos = {4} by query '{5}'\n".format(d.strftime(DATE_FORMAT),
                                                                                                url, str(iPage),posInPage, str(posInPages), query)
                file.write(message.encode('utf8'))
                writeUiLog(fUiLog=fUiLog, searcher="Yandex", qry=query, page_cnt=posInPage, all_cnt=posInPages, ref=link)
                logging.debug(message)
                break
        i += 1
    return bFound


def nextPage(browser):
    nexts = browser.find_elements_by_xpath(u"//a[contains(text(),'дал')]")

    try:
        for next in nexts:
            ActionChains(browser) \
                .move_to_element(next) \
                .send_keys_to_element(next, Keys.ENTER) \
                .perform()
            return
    except:
        # TODO change print to syslog
        logging.error("nextPage not found")


# check yandex errors
def checkNeedTorRestart(browser):
    res = browser.find_elements_by_xpath(u"//p[contains(text(),'Нам очень жаль')]")
    return len(res) > 0


# restart TOR
def restartTor():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate("Den135790")
        controller.signal(Signal.NEWNYM)



def destroy(browser):
    browser.stop_client()
    browser.quit()


def initYandex(query):
    browser = webdriver.Firefox(initPreference())
    try:
        browser.maximize_window()
        browser.get('https://www.yandex.ru/')

        setRegion(browser)
        time.sleep(3)
        submitRegion(browser)
        time.sleep(3)
        #TODO not need now?
        findQueryYA(browser, query)
        browser.implicitly_wait(2)
    except:
        return False, browser
    return True, browser


def initGoogle(query):
    browser = webdriver.Firefox(initPreference())
    browser.maximize_window()
    browser.delete_all_cookies()
    #browser.get('https://www.yandex.ru')
    browser.get(u'https://www.google.ru?q=' + query)
    time.sleep(8)
    submitGoogle(browser)
    time.sleep(8)
    return browser

def getCntElems(browser,query):
    elems = browser.find_elements_by_xpath(query)
    return len(elems)


def searchYandex(search_texts, file, fUiLog):
    for search_text in search_texts:
        browser = None
        try:
            query = search_text['text']
            link = search_text['site_url']
            urls = search_text['urls']
            result, browser = initYandex(query)
            if not result:
                raise Exception('error init Yandex search')

            iPage = 1
            bFound = False
            cntElems = 0 # количество элементов для поиска на странице
            while iPage < MAX_SERACHED_PAGE:
                while checkNeedTorRestart(browser):
                    destroy(browser)
                    browser = initYandex(query)
                    restartTor()
                    # start from beginning
                    iPage = 1
                    cntElems = 0
                time.sleep(3)

                try:
                    bFound = searchOnPage(browser=browser, xpath=YANDEX_XPATH, urls=urls, iPage=iPage,
                                      query=query, link=link, file=file,cntElems = cntElems)
                except:
                    logging.error("error in searchOnPage")
                if bFound:
                    break
                iPage += 1
                try:
                    cntElems += getCntElems(browser,"//div[@data-cid]")
                except:
                    logging.error("error in getCntElems")
                nextPage(browser)

            if iPage == MAX_SERACHED_PAGE:
                d = datetime.datetime.now()
                writeUiLog(fUiLog=fUiLog, searcher="NOT found on Yandex", qry=query, page_cnt=iPage, all_cnt=100, ref=link)
                message = u"{0} link '{1}' NOT Found in yandex on pages {2} by query '{3}'\n".format(
                    d.strftime(DATE_FORMAT), u''.join(urls), str(iPage), query)
                file.write(message.encode('utf8'))
                logging.debug(message)

            # move to windows
            # for handle in browser.window_handles:
            #    browser.switch_to.window(handle)
            destroy(browser)
        except:
            #os.kill(browser.binary.process.pid,signal.SIGKILL)
            logging.error("Unexpected error on yandex search:" + sys.exc_info()[0])
        if browser != None:
            destroy(browser)

def submitGoogle(browser):
    btn = browser.find_element_by_xpath("//button[@type='submit']")

    try:
        ActionChains(browser) \
            .move_to_element(btn) \
            .send_keys_to_element(btn, Keys.ENTER) \
            .perform()
    except:
        logging.error("submitGoogle")


def nextPageGoogle(browser):
    nexts = browser.find_elements_by_xpath(u"//a[@id='pnnext']")

    try:
        for next in nexts:
            ActionChains(browser) \
                .move_to_element(next) \
                .send_keys_to_element(next, Keys.ENTER) \
                .perform()
            return
    except:
        # TODO change print to syslog
        logging.error("oups nextPageGoogle not found")


def isCaptcha(browser, xpath):
    return len(browser.find_elements_by_xpath(xpath)) > 0


def movesOnPage(browser):
    MAX_DOWN_TIME = 10
    for i in range(0, MAX_DOWN_TIME):
        browser.execute_script("window.scrollTo(0, " + str(100 * i) + ");")
        # TODO replace 20 -> 60
        time.sleep(20 / MAX_DOWN_TIME)


def findInSite(browser, link):
    movesOnPage(browser)
    site = browser.find_element_by_xpath(u"//a[@href='{0}']".format(link))
    try:
        ActionChains(browser) \
            .move_to_element(site) \
            .send_keys_to_element(site, Keys.ENTER) \
            .perform()
        movesOnPage(browser)
    except:
        # TODO change print to syslog
        logging.error("Cannot click " + link + "!")

def posOnPageInGoogle(browser, xpath_query, href):

    elems = browser.find_elements_by_xpath('//div/h3/a')
    i = 0

    for elem in elems:
        if elem.get_attribute("href") == href:
            return i
        i += 1
    return -1

def searchGoogle(search_texts, file):
    for search_text in search_texts:
        browser = None
        try:
            query = search_text['text']
            link = search_text['site_url']
            browser = initGoogle(query)

            while isCaptcha(browser, "//div[contains(.,'To continue, please type the characters below:')]"):
                logging.debug("Found CAPTCHA, try restart")
                destroy(browser)
                browser = initGoogle(query)
                restartTor()
            logging.debug("CAPTCHA, not found")

            iPage = 1
            cntElems = 0
            while iPage < MAX_SERACHED_PAGE:
                for url in search_text['urls']:
                    posInPage = posOnPageInGoogle(browser,GOOGLE_XPATH.format(url),url)
                    result = searchSite(browser=browser, xpath_query=GOOGLE_XPATH, url=url, link=link, file=file)
                    if result["res"]:
                        d = datetime.datetime.now()
                        cntElems += posInPage
                        message = u"{0} link '{1}' Found in google on page {2} posInPage = {5} summaryPos={3} by query '{4}'\n".format(
                            d.strftime(DATE_FORMAT), url, str(iPage),str(cntElems), query, str(posInPage))
                        file.write(message.encode("utf8"))
                        logging.debug(message)
                        time.sleep(10)
                        break
                nextPageGoogle(browser)
                time.sleep(3)
                iPage += 1
                cntElems += getCntElems(browser=browser, query= "//div[@class ='g']")
                while isCaptcha(browser, "//div[contains(.,'To continue, please type the characters below:')]"):
                    try:
                        logging.debug("Found CAPTCHA, try restart")
                        destroy(browser)
                        browser = initGoogle(query)
                        restartTor()
                        iPage = 1
                        cntElems = 0
                    except:
                        logging.error("try restart")

            if iPage == MAX_SERACHED_PAGE:
                d = datetime.datetime.now()
                message = u"{0} link '{1}' NOT Found in google on pages {2} by query '{3}'\n".format(
                    d.strftime(DATE_FORMAT), url, str(iPage), query)
                file.write(message.encode("utf8"))
                logging.debug(message)
                # print("iPage = " + str(iPage))

            destroy(browser)
        except:
            try:
                if browser != None:
                    destroy(browser)
            except:
                logging.error("cannot destroy browser search in google")
                continue
            logging.error("Unexpected error on google search:" + sys.exc_info()[0])


def loadSettings():
    json_data = None
    with open(SETTINGS_FILE) as json_file:
        json_data = json.load(json_file)
        # print(json_data)
    return json_data['search_texts']


def main():
    bufsize = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("count",type=int, help="interation count")
    parser.add_argument("depth", type=int, help="max page search")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG, filename=u'mylog.log')
    #print args.count

    global MAX_SERACHED_PAGE
    MAX_SERACHED_PAGE = args.depth
    for i in range(0, args.count):
        print("iteration {0}\n".format(str(i)))

        file = open(os.getenv('COUNTER_SETTINGS_PATH','') + "result.log", "a", bufsize)
        d = datetime.datetime.now()
        file.write("----------------------------\n")
        file.write("start at {0}\n".format(d.strftime(DATE_FORMAT)))

        try:
            search_texts = loadSettings()
        except:
            print("Cannot read {0}".format(SETTINGS_FILE))
        try:
            searchYandex(search_texts, file, fUiLog)
        except:
            logging.error("Error in yandex search")
        try:
            #TODO uncomment this in release
            #searchGoogle(search_texts, file)
        except:
            logging.error("Error in google search")

        d = datetime.datetime.now()
        file.write("end at {0}\n".format(d.strftime(DATE_FORMAT)))
        file.write("++++++++++++++++++++++++++++\n")

        file.close()
    fUiLog.close()


if __name__ == "__main__":
    print("COUNTER_SETTINGS_PATH = " + os.getenv("COUNTER_SETTINGS_PATH",""))
    print("PATH = " + os.getenv("PATH",""))
    print("PWD = " + os.getenv("PWD", ""))
    rconsole.spawn_server()
    main()
