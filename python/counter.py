#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import json
import traceback

import argparse
import os
import logging

from search import Search
from search import NeedRestartTor


SETTINGS_FILE = os.getenv('COUNTER_SETTINGS_PATH', '') + "settings.json"
DATE_FORMAT = "%d/%m/%Y %H:%M:%S"

def getLogger():
    logger = logging.getLogger("counter")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', DATE_FORMAT)
    #ch = logging.StreamHandler()
    ch = logging.FileHandler(os.getenv('COUNTER_SETTINGS_PATH','') + "mylog.log")
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def loadSettings():
    json_data = None
    with open(SETTINGS_FILE) as json_file:
        json_data = json.load(json_file)
        # print(json_data)
    return json_data['search_texts']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("count", type=int, help="interation count")
    parser.add_argument("depth", type=int, help="max page search")
    args = parser.parse_args()
    logger = getLogger()

    try:
        search_texts = loadSettings()
    except:
        logger.error("Cannot read {0}".format(SETTINGS_FILE))
        exit(1)
    for i in range(0, args.count):
        logger.info("start iteration {0}".format(i + 1))
        for search_text in search_texts:
            try:
                with Search(query=search_text, logger=logger, max_pages=args.depth) as ya:
                     logger.info(search_text)
                     while ya.restart():
                         ya.restartTor()
                         ya.initPreference()
                         try:
                             ya.initYandex()
                             ya.Search()
                         except NeedRestartTor as err:
                             ya.browser.close() # close browser window
                             print(err.message)
                     ya.destroy()

                    #         #time.sleep(10)
            except Exception as err:
                traceback.print_exc()
                logger.error("Cannot search {0}".format(search_text))
                logger.error("Message error {0}".format(err.message))
        logger.info("end iteration {0}\n".format(i + 1))

if __name__ == "__main__":
    main()