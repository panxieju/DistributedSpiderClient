import threading

import datetime

import re

from Bean.House import House
from Database.DbManager import DB_Manager
from Downloader import Downloader
from Util.RedisUtils import RedisUtils
from Util.Utils import Utils


def getSpiderInfo(spider):
    if spider == "Spider58":
        return '58同城', False
    if spider == "SpiderAnjuke":
        return '安居客', True
    if spider == "SpiderFang":
        return '房天下', False
    if spider == "SpiderGanji":
        return '赶集网', False


class Spider(threading.Thread):
    downloader = Downloader()
    runSpider = True
    url = ""

    def __init__(self, spider):
        super(Spider, self).__init__()
        self.spider = spider
        self.source, self.https = getSpiderInfo(spider)

    # 解析房源详情
    def parseHouse(self):
        if not self.https:
            response = self.downloader.download_html_response(self.url)
        else:
            response = self.downloader.download_https_response(self.url)
        if self.isInvalidPage(response):
            return

        if self.isMeetFireWall(response):
            self.runSpider = False
            redis = RedisUtils()
            redis.add_to_redis(self.name, self.url)
            return

        if response.status == 404:
            print('%s>%s网页不存在 %s' % (Utils.getCurrentTime(), self.source, self.url))
            Utils.write_error('%s>%s网页不存在 %s' % (Utils.getCurrentTime(), self.source, self.url))
            return

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
        house.lat, house.lon = self.getLatLon(house)
        house.md5 = Utils.generateMD5(house.url)
        house.time = Utils.getCurrentTime()

        timedelta = datetime.datetime.now() - datetime.datetime.strptime(house.date, '%Y-%m-%d')
        days = timedelta.days
        if days > 10:
            print('%s 58过期房源:%s;%s;%s' % (Utils.getCurrentTime(), house.date, house.title, house.url))
            return

        DB_Manager(house)

    @staticmethod
    def isMeetFireWall(response):
        return False

    @staticmethod
    def isInvalidPage(response):
        return False

    @staticmethod
    def getMobileUrl(response):
        return None

    # 解析图片链接
    @staticmethod
    def getImageUrl(response):
        return None

    # 解析所在城市
    @staticmethod
    def getCity(response):
        return None

    # 解析区域
    @staticmethod
    def getDistrict(response):
        return None

    # 解析月租
    @staticmethod
    def getRental(response):
        return None

    # 解析标题
    @staticmethod
    def getTitle(response):
        return None

    # 解析小区名称
    @staticmethod
    def getCampus(response):
        return None

    # 解析经纬度
    @staticmethod
    def getLatLon(house):
        return None

    # 解析地址
    @staticmethod
    def getAddress(response):
        return None

    # 解析房间数量
    @staticmethod
    def getRooms(houseType):
        return Utils.transformHouseType(houseType)

    # 解析面积
    @staticmethod
    def getArea(response):
        return None

    # 解析楼层
    @staticmethod
    def getFloor(response):
        return None

    # 解析联系人
    @staticmethod
    def getContact(response):
        return None

    # 解析联系电话
    @staticmethod
    def getPhone(response):
        return None

    # 解析出租类型
    @staticmethod
    def getRentType(response):
        return None

    # 解析房屋类型
    @staticmethod
    def getHouseType(houseType):
        return Utils.transformHouseType(houseType)

    # 解析日期
    @staticmethod
    def getDate(response):
        return None

    # 解析经纬度
    @staticmethod
    def getLatLon(house):
        return Utils.geoSearch(house.city,
                               house.district + house.campus) if house.district != "" else Utils.geoSearchWithAddress(
            house.city, house.address + house.campus)

    def run(self):
        self.parseHouse()

    def crawl(self, url):
        self.url = url
        self.start()
