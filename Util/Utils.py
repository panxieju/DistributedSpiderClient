#!usr/bin/python
# -*- coding:utf-8 -*-

'''
Created on 2017年4月19日

@author: Administrator
'''
import hashlib
import socket
import time
import uuid

import requests
import datetime
from datetime import timedelta
import re


class Utils(object):
    @staticmethod
    def geoSearch(city, address):
        key = 'e792003c6a2cc903c4f6a6529dab06b5'
        parameters = {'city': city, 'address': address, 'key': key}
        baseUrl = 'http://restapi.amap.com/v3/geocode/geo?'
        response = requests.get(baseUrl, parameters)
        answer = response.json()
        if answer is None:
            return None
        try:
            geocodes = answer['geocodes'][0]
            location = geocodes['location']
            lon = float(location.split(',')[0])
            lat = float(location.split(',')[1])
            return lat, lon
        except:
            return 0, 0

    @staticmethod
    def geoSearchWithAddress(city, address):
        key = 'e792003c6a2cc903c4f6a6529dab06b5'
        parameters = {'city': city, 'address': address, 'key': key}
        baseUrl = 'http://restapi.amap.com/v3/geocode/geo?'
        response = requests.get(baseUrl, parameters)
        answer = response.json()
        if answer is None:
            return None
        try:
            if int(answer['count']) >0 :
                geocodes = answer['geocodes'][0]
                location = geocodes['location']
                address = geocodes['formatted_address']
                lon = float(location.split(',')[0])
                lat = float(location.split(',')[1])
                return lat, lon, address
            else:
                raise ValueError('GetLatLon: %s, %s' % (city, address))
        except:
            raise ValueError('GetLatLon: %s, %s' % (city, address))

    @staticmethod
    def regeoSearch(lat, lon):
        location = lon + ',' + lat
        key = 'e792003c6a2cc903c4f6a6529dab06b5'
        parameters = {'location': location, 'key': key, 'radius': 50, 'output': 'json'}
        baseUrl = 'http://restapi.amap.com/v3/geocode/regeo?'
        response = requests.get(baseUrl, parameters)
        answer = response.json()
        if answer is None:
            return None
        try:
            regeocodes = answer['regeocode']
            address = regeocodes['formatted_address']
            return address
        except:
            return None

    @staticmethod
    def getCurrentDate():
        now = datetime.datetime.now()
        return datetime.datetime.strftime(now, '%Y-%m-%d')

    @staticmethod
    def getCurrentTime():
        now = datetime.datetime.now()
        return datetime.datetime.strftime(now, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def formatChineseDate(chinsesDate):
        # date = "2017年03月15日"
        date_ = chinsesDate.replace("年", "-").replace("月", "-").replace("日", "")
        date = datetime.datetime.strptime(date_, '%Y-%m-%d')
        return date.strftime('%Y-%m-%d')

    @staticmethod
    def formatUncompleteDate(date):
        # date = '04-17'
        year = datetime.datetime.now().year
        return '%s-%s' % (year, date)

    @staticmethod
    def formatBackSlantDate(chinsesDate):
        # date = "2017/03/15"
        date_ = chinsesDate.replace("/", "-")
        date = datetime.datetime.strptime(date_, '%Y-%m-%d')
        return date.strftime('%Y-%m-%d')

    @staticmethod
    def formatDate(date):
        date_ = datetime.datetime.strptime(date, '%Y-%m-%d')
        return date_

    @staticmethod
    def caculateDateInterval(date1, date2):
        date1_ = datetime.datetime.strptime(date1, '%Y-%m-%d')
        date2_ = datetime.datetime.strptime(date2, '%Y-%m-%d')
        delta = date1_ - date2_
        return delta.days

    @staticmethod
    def isLegalDate(date, limit):
        currentDate = datetime.datetime.now().strftime('%Y-%m-%d')
        cdate = datetime.datetime.strptime(currentDate, '%Y-%m-%d')
        date_ = datetime.datetime.strptime(date, '%Y-%m-%d')
        delta = cdate - date_
        if delta.days <= limit:
            return True
        else:
            return False

    @staticmethod
    def isLegalDateForUrls(date):
        currentDate = datetime.datetime.now().strftime('%Y-%m-%d')
        cdate = datetime.datetime.strptime(currentDate, '%Y-%m-%d')
        date_ = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        delta = cdate - date_
        return delta.days > 15

    @staticmethod
    def getLigalDate(limit):
        currentDate = datetime.datetime.now().strftime('%Y-%m-%d')
        cdate = datetime.datetime.strptime(currentDate, '%Y-%m-%d')
        date = cdate - datetime.timedelta(days=limit)
        return date

    @staticmethod
    def getExpiredDate():
        today = datetime.datetime.now()
        expired_date = (today - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        return expired_date

    @staticmethod
    def write_error(message):
        logfile = open(r'./spider_error.log', 'a')
        logfile.write("%s: %s\n" % (Utils.getCurrentTime(), message))
        logfile.close()

    @staticmethod
    def write_log(message):
        logfile = open(r'./spide_log.txt', 'a')
        logfile.write("%s: %s\n" % (Utils.getCurrentTime(), message))
        logfile.close()

    @staticmethod
    def write_firewall_error(message):
        logfile = open(r'./spider_firewall_error.log', 'a')
        logfile.write("%s: %s\n" % (Utils.getCurrentTime(), message))
        logfile.close()

    @staticmethod
    def format_date(date_):
        month = date_.split('-')[1]
        if int(month) < 10:
            month = '0' + month
        year = date_.split('-')[0]
        day = date_.split('-')[2]
        if int(day) < 10:
            day = '0' + day
        return year + '-' + month + '-' + day

    @staticmethod
    def get_city_pinyin_table(self, city):
        if re.search(r'广州', city):
            table = 'guangzhou'
        if re.search(r'深圳', city):
            table = 'shenzhen'
        if re.search(r'北京', city):
            table = 'beijing'
        if re.search(r'上海', city):
            table = 'shanghai'
        return table

    # 根据日期字符串计算与当前的距离
    # date： 2017-10-01
    # 返回值：天数
    @staticmethod
    def getDeltaDays(date):
        timedelta = datetime.datetime.now() - datetime.datetime.strptime(date, '%Y-%m-%d')
        return timedelta.days

    @staticmethod
    def getDeltaDate(minutes=0, hours=0, days=0):
        now = datetime.datetime.now()
        date = now - datetime.timedelta(minutes=minutes, hours=hours, days=days)
        date_ = date.strftime('%Y-%m-%d')
        return date_

    @staticmethod
    def generateMD5(str):
        generator = hashlib.md5()
        generator.update(str.encode('utf-8'))
        return generator.hexdigest()

    @staticmethod
    def get_city_by_url(url):
        if re.search('gz|guangzhou', url):
            return '广州'
        if re.search('sz|shenzhen', url):
            return '广州'
        if re.search('bj|beijing', url):
            return '广州'
        if re.search('sh|shanghai', url):
            return '广州'

        return None

    @staticmethod
    def get_duration(start_time):
        now = datetime.datetime.now()
        duration = now - start_time
        seconds = duration.seconds
        second = seconds % 60
        minute = seconds % 3600 // 60
        hour = seconds % (24 * 3600) // 3600
        day = duration.days
        print(seconds, '>', day, hour, minute, second)
        day_str = '%d天' % day if day > 0 else ''
        hour_str = '%d小时' % hour if hour > 0 else ''
        minute_str = '%d分' % minute if minute > 0 else ''
        second_str = '%d秒' % second if second > 0 else ''
        return day_str + hour_str + minute_str + second_str

    @staticmethod
    def transformHouseType(str):
        if str is None:
            return 0
        chinese_digit = {
            '一': 1,
            '两': 2,
            '二': 2,
            '三': 3,
            '四': 4,
            '五': 5,
            '六': 6,
            '七': 7,
            '八': 8,
            '九': 9,
            '十': 10
        }
        if re.search(r'^.*房', str):
            number = str.split('房')[0]
            try:
                rooms = chinese_digit[number]
                return int(rooms)
            except:
                return int(number)

        elif re.search(r'^.*室', str):
            number = str.split('室')[0]
            try:
                rooms = chinese_digit[number]
                return int(rooms)
            except:
                return int(number)

        else:
            return 0

    @staticmethod
    def convertVerified(verified):
        fyear = datetime.datetime.now().year
        verified = str(fyear) + verified[2:]
        return verified

    @staticmethod
    def convertAlive(alive_str):
        minutes = 0
        hours = 0
        days = 0

        if re.search(r'\d+分钟', alive_str):
            minutes = re.findall(r'\d+', alive_str)[0]
        elif re.match(r'\d+小时', alive_str):
            hours = re.findall(r'\d+', alive_str)[0]
        elif re.search(r'\d+天', alive_str):
            days = re.findall(r'\d+', alive_str)[0]
        else:
            return -1
        return int(minutes) * 60 + int(hours) * 60 * 60 + int(days) * 60 * 60 * 24

    @staticmethod
    def transformDate(_date):
        dateConverted = str
        if re.search('分钟', _date):
            ago = int(re.findall('\d+', _date)[0])
            dateConverted = (datetime.datetime.now() - timedelta(minutes=ago)).strftime('%Y-%m-%d')
        elif re.search('小时', _date):
            ago = int(re.findall('\d+', _date)[0])
            dateConverted = (datetime.datetime.now() - timedelta(hours=ago)).strftime('%Y-%m-%d')
        elif re.search('今天', _date):
            dateConverted = Utils.getCurrentDate()
        elif re.match('\d*天前', _date):
            ago = int(re.findall('\d+', _date)[0])
            dateConverted = (datetime.datetime.now() - timedelta(days=ago)).strftime('%Y-%m-%d')
        elif re.match('\d+-\d+-\d+', _date):
            dateConverted = _date
            pass
        elif re.match('\d+-\d+', _date):
            dateConverted = Utils.formatUncompleteDate(_date)
        elif re.match('\d+年\d+月\d+日', _date):
            dateConverted = Utils.formatChineseDate(_date)
        return dateConverted

    @staticmethod
    def getTime():
        import datetime
        return int(datetime.datetime.now().timestamp() * 1000000)

    @staticmethod
    def getMacAddress():
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

    @classmethod
    def getHostName(cls):
        return socket.getfqdn(socket.gethostname())

    @classmethod
    def getIp(cls):
        return socket.gethostbyname(cls.getHostName())

if __name__ == '__main__':
    b1 = 0
    b2 = 0.0
    print(b1 == b2)
