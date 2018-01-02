# !/usr/bin/env python

import daemon
import sys
sys.path.append("/home/ubuntu/git_repository/server")
import logging
import urllib2
import json
import time
import orderBookService

from time import sleep
from datetime import datetime

def createTimeStamp(datestr, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, format))

logging.basicConfig()

file_logger = logging.FileHandler("/tmp/dmon_order_book" + sys.argv[1] +".log", "w")

logger = logging.getLogger()
logger.addHandler(file_logger)
logger.setLevel(logging.INFO)

hdr = {'User-Agent': 'Mozilla/5.0', 'referer' : 'http://m.naver.com'}

exchange_url = {}
exchange_url['poloniex'] = 'https://poloniex.com/public?command=returnOrderBook&currencyPair=' #USDT_ZEC&depth=5'
exchange_url['coinone'] = 'https://api.coinone.co.kr/orderbook?currency=' #BTC
exchange_url['bithumb'] = 'https://api.bithumb.com/public/orderbook/' #BTC
exchange_url['coinnest'] = 'https://api.coinnest.co.kr/api/pub/depth?coin='
exchange_url['korbit'] = 'https://api.korbit.co.kr/v1/ticker?currency_pair='

coin_list = {}
coin_list['poloniex'] = ['BTC', 'ETH', 'LTC', 'XRP', 'ETC', 'ZEC', 'NXT', 'STR', 'DASH' ,'XMR' ,'REP', 'BCH']
coin_list['bithumb'] = ['BTC', 'ETH', 'DASH', 'LTC', 'ETC', 'XRP', 'XMR', 'ZEC', 'BCH', 'QTUM'];
coin_list['coinone'] = ['BTC', 'ETH', 'ETC', 'XRP', 'BCH', 'QTUM', 'IOTA']
coin_list['coinnest'] = ['TRON', 'INK', 'TSL']
coin_list['korbit'] = ['BTC', 'BCH', 'XRP', 'ETH', 'ETC', 'LTC']

class restFulApi:
    def __init__(self, command):
        self.exch = command

    def api_query(self, coin, req={}):
        ret = urllib2.urlopen(urllib2.Request(exchange_url[self.exch] + coin, headers=hdr))
        self.jObj = json.loads(ret.read())
        return self.jObj

    def request(self, coin):
        if self.exch == "poloniex" :
            return self.api_query("USDT_" + coin + "&depth=5")
        elif self.exch == "coinnest" :
            return self.api_query(coin.lower())
        else :
            return self.api_query(coin)

    def returnCommon(self):
        if self.exch == "bithumb" :
            return orderBookService.bithumb()
        if self.exch == "coinone" :
            return orderBookService.coinone()
        if self.exch == "poloniex":
            return orderBookService.poloniex()
        if self.exch == "coinnest":
            return orderBookService.coinnest()


with daemon.DaemonContext(files_preserve=[file_logger.stream.fileno()]):
    argu = sys.argv[1]
    restFul = restFulApi(argu)
    common = restFul.returnCommon()
    while True:
        for coin in coin_list[argu]:
            jObj = restFul.request(coin)
            common.setJsonObj(jObj)
            common.odBookParse(coin)
        # message = "RECEIVE SUCCESS"
        # time = str(datetime.now())
        # logger.info(time + ' : ' + message)
        sleep(1)
