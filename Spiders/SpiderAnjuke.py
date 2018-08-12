import datetime
import random
import re
import threading
import time

from Bean.House import House
from Database.DbManager import DB_Manager
from Downloader.Downloader import Downloader
from Util.RedisUtils import RedisUtils
from Util.Utils import Utils

INTERVAL = 30


class SpiderAnjuke(object):
    source = "安居客"
    downloader = Downloader()
    runSpider = True

    def __init__(self):
        self.redis = RedisUtils(self)

    # 解析房源详情
    def parseHouse(self, url):
        response = self.downloader.download_https_response(url)
        if response is None:
            return True

        if re.search(r'访问验证', response.body.decode('utf-8')):
            self.runSpider = False
            self.redis.add_to_redis("SpiderAnjuke", response.url)
            return False

        if response.status == 404:
            print('%s 安居客网页不存在 %s' % (Utils.getCurrentTime(), url))
            Utils.write_error('安居客网页不存在 %s' % url)
            return True
        house = House()
        house.url = self.getMobileUrl(response)
        house.title = self.getTitle(response)
        house.image_url = self.getImageUrl(response)
        house.city = self.getCity(response)
        house.district = self.getDistrict(response)
        house.rental = self.getRental(response)
        house.campus = self.getCampus(response)
        house.date = self.getDate(response)
        house.address = self.getAddress(response)
        house.source = self.source
        house.house_type = self.getHouseType(response)
        house.rooms = self.getRooms(house.house_type)
        house.area = self.getArea(response)
        house.floor = self.getFloor(response)
        house.contact = self.getContact(response)
        house.phone = self.getPhone(response)
        house.rent_type = self.getRentType(response)
        house.lat, house.lon, house.address = self.getLatLon(house)
        house.md5 = Utils.generateMD5(house.url)
        house.time = Utils.getCurrentTime()

        timedelta = datetime.datetime.now() - datetime.datetime.strptime(house.date, '%Y-%m-%d')
        days = timedelta.days
        if days > 7:
            print('%s 安居客过期房源:%s;%s;%s' % (Utils.getCurrentTime(), house.date, house.title, house.url))
        elif house.isValidHouse():
            DB_Manager(house)
        return True

    # 解析手机页面链接
    @staticmethod
    def getMobileUrl(response):
        try:
            url_ = response.xpath('//meta[@name="mobile-agent"]/@content').extract()[0]
            return re.findall(r'url=(.+)', url_)[0]
        except:
            print('Error!getMobileUrl()')

    # 解析图片链接
    @staticmethod
    def getImageUrl(response):
        try:
            return response.xpath('//div[@class="switch_list"]/div/img/@data-src').extract_first()
        except:
            print('Error!getImageUrl()')

    # 解析所在城市
    @staticmethod
    def getCity(response):
        try:
            return response.xpath('//div[@class="cityselect"]/div/text()').extract()[0].strip()
        except:
            print('Error!getCity()')

    # 解析区域
    @staticmethod
    def getDistrict(response):
        try:
            district_ = response.xpath('//div[@class="p_1180 p_crumbs"]/a[3]/text()').extract()[0]
            return re.findall('(.*)租房', district_)[0]
        except:
            print('Error!getDistrict()')

    # 解析月租
    @staticmethod
    def getRental(response):
        try:
            return float(response.xpath('//div[@class="title-basic-info clearfix"]/span/em/text()').extract()[0])
        except:
            print('Error!getRental()')

    # 解析标题
    @staticmethod
    def getTitle(response):
        try:
            return response.xpath('//h3[@class="house-title"]/text()').extract()[0]
        except:
            print('Error!getTitle()')

    # 解析小区名称
    @staticmethod
    def getCampus(response):
        try:
            return response.xpath('//ul[@class="house-info-zufang cf"]/li/a/text()').extract()[-3]
        except:
            print('Error!getCampus()')

    # 解析日期
    @staticmethod
    def getDate(response):
        try:
            date_ = response.xpath('//div[@class="mod-title bottomed"]/div/text()').extract()[0]
            date = re.findall(r'\d+年\d+月\d+日', date_)[0]
            return Utils.transformDate(date)
        except:
            print('Error!getDate()')

    # 解析经纬度
    @staticmethod
    def getLatLon(house):
        try:
            return Utils.geoSearchWithAddress(house.city, house.district + house.campus)
        except:
            Utils.write_error("%s 安居客无法解析经纬度和地址 %s" % (Utils.getCurrentTime(), house.url))
            return 0, 0, ''

    # 解析地址
    @staticmethod
    def getAddress(response):
        return ''

    # 解析房间数量
    @staticmethod
    def getRooms(houseType):
        return Utils.transformHouseType(houseType)

    # 解析面积
    @staticmethod
    def getArea(response):
        try:
            return response.xpath('//span[@class="info-tag no-line"]/em/text()').extract()[0]
        except:
            print('Error!getArea()')

    # 解析楼层
    @staticmethod
    def getFloor(response):
        try:
            return response.xpath('//ul[@class="house-info-zufang cf"]/li/span[@class="info"]/text()').extract()[3]
        except:
            print('Error!getFloor()')

    # 解析联系人
    @staticmethod
    def getContact(response):
        try:
            return response.xpath('//h2[@class="broker-name"]/text()').extract()[0].strip()
        except:
            print('Error!getContact()')

    # 解析联系电话
    @staticmethod
    def getPhone(response):
        try:
            return response.xpath('//div[@class="broker-mobile"]/text()').extract()[0].strip()
        except:
            pass

    # 解析出租类型
    @staticmethod
    def getRentType(response):
        try:
            return response.xpath('//li[@class="title-label-item rent"]/text()').extract_first().strip()
        except:
            print('Error!getRentType()')

    # 解析房屋类型
    @staticmethod
    def getHouseType(response):
        try:
            rooms = response.xpath('//span[@class="info-tag"]/em/text()').extract()[0].strip()
            halls = response.xpath('//span[@class="info-tag"]/em/text()').extract()[1].strip()
            return '%s室%s厅' % (rooms, halls)
        except:
            print('Error!getHouseType()')


if __name__ == '__main__':
    client = SpiderAnjuke()
    # url = 'https://sz.zu.anjuke.com/fangyuan/1137006349'
    # client.parseHouse(url)
    client.crawl()
