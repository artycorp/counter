#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import datetime


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from stem import Signal
from stem.control import Controller

DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

class NeedRestartTor(Exception):
    pass

class Search:
    logger = None
    ui_log = None
    browser = None
    profile = None
    query = None
    urls = None
    CITY = u'Perm'
    link = None
    iPage = 1 # page number on search
    cntElems = 0 # количество элементов для поиска на странице
    MAX_SERACHED_PAGE = 50
    YANDEX_XPATH = u"//a[@href='{0}']"
    needRestart = True


    def __init__(self, query, logger,max_pages):
        self.logger = logger
        self.query = query["text"]
        self.urls = query["urls"]
        self.link = query["site_url"]
        self.browser = None
        self.MAX_SERACHED_PAGE = max_pages
        self.ui_log = open(os.getenv('COUNTER_SETTINGS_PATH','') + "ui.log", "a")

    def __enter__(self):
        return self

    def destroy(self):
        self.browser.stop_client()
        self.browser.quit()
        self.ui_log.close()
        self.ui_log = None

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.info("__exit__")
        self.destroy()

    def writeUiLog(self, searcher, qry, page_cnt, all_cnt, ref):
        d = datetime.datetime.now()
        self.ui_log.write("{0} | ".format(d.strftime(DATE_FORMAT)))
        self.ui_log.write("{0} | ".format(searcher.encode("utf8")))
        self.ui_log.write("{0} | ".format(qry.encode("utf8")))
        self.ui_log.write("{0} | ".format(page_cnt))
        self.ui_log.write("{0} | ".format(all_cnt))
        self.ui_log.write("{0}\n".format(ref.encode("utf8")))

    def clean(self):
        """Reset values to default"""
        self.iPage = 1
        self.cntElems = 0

    def restart(self):
        self.ui_log = open(os.getenv('COUNTER_SETTINGS_PATH', '') + "ui.log", "a")
        return self.needRestart

    def restartTor(self):
        """Get new tor session"""
        with Controller.from_port(port=9051) as controller:
            controller.authenticate("Den135790")
            controller.signal(Signal.NEWNYM)
        self.clean()
        self.logger.debug("success restart tor")

    def initPreference(self):
        """settings for TOR connect"""
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('network.proxy.type', 1)
        self.profile.set_preference('network.proxy.socks', '127.0.0.1')
        self.profile.set_preference('network.proxy.socks_port', 9050)
        self.logger.debug("success init preference")

    def check_errors(self):
        str = self.browser.page_source
        res = str.find(u'Доступ к нашему сервису временно запрещён!')
        if res != -1:
            return True
        res = str.find(u'Нам очень жаль')
        if res != -1:
            return True
        res = str.find(u'Введите, пожалуйста, символы с картинки в поле ввода')
        if res != -1:
            return True
        return False

    def setRegion(self):
        """set location to Perm"""
        self.browser.get('https://tune.yandex.ru/region/?retpath=https%3A%2F%2Fyandex.ru%2F%3Fdomredir%3D1&amp;laas=1')
        if self.check_errors():
            raise NeedRestartTor("setRegion")

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

    def initYandex(self):
        """setup yandex to start search"""
        self.browser = webdriver.Firefox(self.profile)

        self.browser.maximize_window()
        self.browser.get('https://www.yandex.ru/')
        if self.check_errors():
            raise NeedRestartTor("initYandex")

        self.setRegion()
        time.sleep(5)
        self.submitRegion()
        time.sleep(3)


    def submitRegion(self):
        """push submit region button"""
        btn = self.browser.find_element_by_xpath("//input[@type='submit']")

        try:
            ActionChains(self.browser) \
                .move_to_element(btn) \
                .send_keys_to_element(btn, Keys.ENTER) \
                .perform()
        except:
            self.logger.error("Submit Region error")

    # search query string in yandex
    def findQueryYA(self):
        #search = self.browser.find_element_by_xpath("//input[@id='text']")
        ActionChains(self.browser) \
            .send_keys(Keys.HOME) \
            .send_keys(self.query) \
            .send_keys(Keys.ENTER) \
            .perform()

    def getCntElems(self, query):
        elems = self.browser.find_elements_by_xpath(query)
        return len(elems)

    def Search(self):
        self.findQueryYA()
        self.browser.implicitly_wait(2)
        while self.iPage < self.MAX_SERACHED_PAGE:
            if self.searchOnPage(self.YANDEX_XPATH):
        #        print("FOUND!!!\n")
                self.logger.debug("Found!")
                self.needRestart = False
                return True
        #        break
            self.iPage += 1
            try:
                self.cntElems += self.getCntElems("//div[@data-cid]")
            except:
                self.logger.error("error in getCntElems")
            self.nextPage()
            if self.check_errors():
                raise NeedRestartTor("Search")

        self.writeUiLog(searcher="Not found Yandex", qry=self.query, page_cnt=-1, all_cnt=self.MAX_SERACHED_PAGE,
                                ref=self.link)
        #print("not found!!!\n")

    def searchOnPage(self, xpath):
        i = 1
        bFound = False
        while i < 2 and not bFound:
            self.browser.execute_script("window.scrollTo(0, " + str(200 * i) + ");")
            for url in self.urls:
                posInPage = -1
                try:
                    #class ,'serp-item') and @ data-cid]
                    #elems = self.browser.find_elements_by_xpath("//div/div/span/a[@href='{0}']/../../..".format(url))
                    elems = self.browser.find_elements_by_xpath("//div/div/a[@href='{0}']/../../../..".format(url))

                    for elem in elems:
                        try:
                            posInPage = elem.get_attribute("data-cid")
                            # TODO грязный хак, чтобы обрабатывался только 1й элемент, у второго нет атрибута data-cid
                            break
                        except:
                            self.loger.error("Error in get data-cid")
                except:
                    self.logger.error(u"Error in find posInPage format url={0}".format(url))
                result = self.searchSite(url=url, xpath_query=xpath, link=self.link)
                bFound = result["res"]
                if bFound:
                    posInPages = int(posInPage) + self.cntElems
                    d = datetime.datetime.now()
                    message = u"{0} link '{1}' Found in yandex on page {2} with Pos = {3} summaryPos = {4} by query '{5}'\n".format(
                        d.strftime(DATE_FORMAT),
                        url, str(self.iPage), posInPage, str(posInPages), self.query)
                    ###file.write(message.encode('utf8'))
                    self.writeUiLog(searcher="Yandex", qry=self.query, page_cnt=posInPage, all_cnt=posInPages, ref=self.link)
                    self.logger.debug(message)
                    break
            i += 1
        return bFound

    def nextPage(self):
        nexts = self.browser.find_elements_by_xpath(u"//a[contains(text(),'дал')]")
        try:
            for next in nexts:
                ActionChains(self.browser) \
                    .move_to_element(next) \
                    .send_keys_to_element(next, Keys.ENTER) \
                    .perform()
                return
        except:
            # TODO change print to syslog
            self.logger.error("nextPage not found")

    def searchSite(self, xpath_query, url, link):
        bFound = False
        href = None
        try:
            sites = self.browser.find_elements_by_xpath(xpath_query.format(url))
        except:
            self.logger.error(u"Error in find_elements_by_xpath by url='{0}'".format(url))
            sites = None
        for site in sites:
            try:
                href = site.get_attribute("href")
                ActionChains(self.browser) \
                    .move_to_element(site) \
                    .send_keys_to_element(site, Keys.ENTER) \
                    .perform()
                time.sleep(2)
                handle = self.browser.window_handles[1]
                self.browser.switch_to_window(handle)
                self.findInSite(link=link)
                self.browser.switch_to_window(self.browser.window_handles[0])
                bFound = True
                break
            except:
                bFound = True
                try:
                    self.browser.switch_to_window(self.browser.window_handles[0])
                except:
                    self.logger.error("Error switching window on Serach site")
                message = "ERROR Cannot click {0} by link {1}\n".format(url, link)
                ###file.write(message.encode("utf8"))
                self.logger.error(message.encode("utf8"))
                break
        return {"res": bFound, "href": href}

    def findInSite(self, link):
        self.movesOnPage()
        site = self.browser.find_element_by_xpath(u"//a[@href='{0}']".format(link))
        try:
            ActionChains(self.browser) \
                .move_to_element(site) \
                .send_keys_to_element(site, Keys.ENTER) \
                .perform()
            self.movesOnPage()
        except:
            self.logger.error("Cannot click " + link + "!")
        self.browser.close()

    def movesOnPage(self):
        MAX_DOWN_TIME = 10
        for i in range(0, MAX_DOWN_TIME):
            self.browser.execute_script("window.scrollTo(0, " + str(100 * i) + ");")
            # TODO replace 20 -> 60
            time.sleep(60 / MAX_DOWN_TIME)
