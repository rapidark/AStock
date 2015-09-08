# -*- coding: utf-8 -*-
import sys
import urllib2
import socket
import re
import time
from aclass import *

stockList = []
timePattern = re.compile(r',(\d+:\d+:\d+),')
stockPattern = re.compile(r'var hq_str_s[hz]\d{6}="([^,"]+),([^,"]+),([^,"]+),([^,"]+),([^,"]+),([^,"]+),[^,"]+,[^,"]+,[^,"]+,[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,([^,"]+),[^,"]+,[^"]+";')
lastTime = ''
lastData = []

def loadStockList():
	for index in range(1,len(sys.argv)):
		stockNumber = sys.argv[index]
		if len(stockNumber) == 8:
			# 8位长度的代码必须以sh或者sz开头
			if (stockNumber.startswith('sh') or stockNumber.startswith('sz')) and stockNumber[2:8].decode().isdecimal():
				stockList.append(stockNumber)
		elif len(stockNumber) == 6:
			if stockNumber.decode().isdigit():
				# 6位长度的0开头自动补sz，6开头补sh，3开头补sz
				if stockNumber.startswith('0'):
					stockList.append('sz' + stockNumber)
				elif stockNumber.startswith('6'):
					stockList.append('sh' + stockNumber)
				elif stockNumber.startswith('3'):
					stockList.append('sz' + stockNumber)
		elif stockNumber == 'sh':
			stockList.append('sh000001')
		elif stockNumber == 'sz':
			stockList.append('sz399001')
		elif stockNumber == 'cy':
			stockList.append('sz399006')
	if len(stockList) == 0:
		return False
	return True

def requestStockData():
	url = 'http://hq.sinajs.cn/list=' + ','.join(stockList)
	try:
		content = urllib2.urlopen(url, timeout = 3).read()
	except urllib2.URLError:
		return 1
	except socket.timeout:
		return 1
	# 判断数据时间有没有更新
	match = timePattern.search(content)
	global lastTime
	if match == None or match.group(1) == lastTime:
		return 2
	lastTime = match.group(1)
	# 循环抓取显示数据
	lastData[:] = []
	match = stockPattern.search(content)
	while match:
		stock = Stock(match.group(1), match.group(2), match.group(3), match.group(4), match.group(5), match.group(6));
		stock.calcBuyPercent([match.group(7), match.group(8), match.group(9), match.group(10), match.group(11), match.group(12), match.group(13), match.group(14), match.group(15), match.group(16)]);
		lastData.append(stock)
		match = stockPattern.search(content, match.end() + 1)
	return 0

if len(sys.argv) < 2:
	print('使用示例: python astock.py sh600000 sz000001\n自动补全：6字头股票代码脚本会自动补sh前缀，0字头和3字头补sz\n特殊代码：sh-上证指数，sz-深证指数，cy-创业板指')
elif loadStockList() == False:
	print('没有有效的股票代码')
else:
	while True:
		result = requestStockData()
		if result == 0:
			print(lastTime)
			for stock in lastData:
				stock.printStockData()
			time.sleep(5)
		elif result == 1:
			print('超时重试')
		elif result == 2:
			time.sleep(5)
		else:
			print('未知错误')
			break
