def restart(self):
    return self.needRestart


def __enter__(self):
    return self


def __exit__(self, exc_type, exc_value, traceback):
    self.destroy()


def destroy(self):
    self.browser.stop_client()
    self.browser.quit()


# disable image and flash
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


def check_errors(self):
    str = self.browser.page_source
    res = str.find(u'Доступ к нашему сервису временно запрещён!')
    if res != -1:
        return True
    res = str.find(u'Нам очень жаль')
    if res != -1:
        return True
    return False


def initYandex(self):
    self.browser = webdriver.Firefox(self.profile)

    self.browser.maximize_window()
    self.browser.get('https://www.yandex.ru/')
    if self.check_errors():
        raise NeedRestartTor("initYandex")

    self.setRegion()
    time.sleep(3)
    self.submitRegion()
    time.sleep(3)
    ###browser.implicitly_wait(2)


def Search(self):
    self.findQueryYA()
    self.browser.implicitly_wait(2)
    while self.iPage < self.MAX_SERACHED_PAGE:
        if self.searchOnPage(self.YANDEX_XPATH):
            print("FOUND!!!\n")
            self.needRestart = False
            return True
            break
        self.iPage += 1
        self.nextPage()
        if self.check_errors():
            raise NeedRestartTor("Search")
    print("not found!!!\n")


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
        logging.error("nextPage not found")


# set location to Perm
def setRegion(self):
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

    # search.submit()


def restartTor(self):
    with Controller.from_port(port=9051) as controller:
        controller.authenticate("Den135790")
        controller.signal(Signal.NEWNYM)
    self.iPage = 1
    self.cntElems = 0


def searchOnPage(self, xpath):
    i = 1
    bFound = False
    while i < 2 and not bFound:
        self.browser.execute_script("window.scrollTo(0, " + str(200 * i) + ");")
        for url in self.urls:
            posInPage = -1
            try:
                elems = self.browser.find_elements_by_xpath("//div/div/span/a[@href='{0}']/../../..".format(url))

                for elem in elems:
                    try:
                        posInPage = elem.get_attribute("data-cid")
                        # TODO грязный хак, чтобы обрабатывался только 1й элемент, у второго нет атрибута data-cid
                        break
                    except:
                        logging.error("Error in get data-cid")
            except:
                logging.error(u"Error in find posInPage format url={0}".format(url))
            result = self.searchSite(url=url, xpath_query=xpath, link=self.link)
            bFound = result["res"]
            if bFound:
                posInPages = int(posInPage) + self.cntElems
                d = datetime.datetime.now()
                message = u"{0} link '{1}' Found in yandex on page {2} with Pos = {3} summaryPos = {4} by query '{5}'\n".format(
                    d.strftime(DATE_FORMAT),
                    url, str(self.iPage), posInPage, str(posInPages), self.query)
                ###file.write(message.encode('utf8'))
                ###writeUiLog(fUiLog=fUiLog, searcher="Yandex", qry=query, page_cnt=posInPage, all_cnt=posInPages, ref=link)
                logging.debug(message)
                break
        i += 1
    return bFound


def searchSite(self, xpath_query, url, link):
    bFound = False
    href = None
    try:
        sites = self.browser.find_elements_by_xpath(xpath_query.format(url))
    except:
        logging.error(u"Error in find_elements_by_xpath by url='{0}'".format(url))
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
            # TODO change print to syslog
            bFound = True
            try:
                self.browser.switch_to_window(self.browser.window_handles[0])
            except:
                logging.error("Error switching window on Serach site")
            message = "ERROR Cannot click {0} by link {1}\n".format(url, link)
            ###file.write(message.encode("utf8"))
            logging.error(message.encode("utf8"))
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
        # TODO change print to syslog
        logging.error("Cannot click " + link + "!")


def movesOnPage(self):
    MAX_DOWN_TIME = 10
    for i in range(0, MAX_DOWN_TIME):
        self.browser.execute_script("window.scrollTo(0, " + str(100 * i) + ");")
        # TODO replace 20 -> 60
        time.sleep(20 / MAX_DOWN_TIME)
