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


class Spider58(object):
    source = "58同城"
    downloader = Downloader()
    runSpider = True

    def __init__(self):
        self.redis = RedisUtils(self)

    # 解析房源详情
    def parseHouse(self, url):
        response = self.downloader.download_html_response(url)
        if response is None:
            return True
        try:
            notExist = response.xpath('//h1/text()').extract()[0].strip()
            if re.search(r'不在这个星球上', notExist):
                print('%s 58网页不存在 %s' % (Utils.getCurrentTime(), url))
                Utils.write_error('58网页不存在 %s' % url)
                return True
            else:
                pass
        except:
            pass

        try:
            if re.search(r'firewall', response.url):
                self.runSpider = False
                return False
        except:
            pass

        if response.status == 404:
            print('%s 58网页不存在 %s' % (Utils.getCurrentTime(), url))
            Utils.write_error('58网页不存在 %s' % url)
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
        if days > 7:
            print('%s 58过期房源:%s;%s;%s' % (Utils.getCurrentTime(), house.date, house.title, house.url))
        elif house.isValidHouse():
            DB_Manager(house)
        return True #继续运行这个爬虫

    @staticmethod
    def getMobileUrl(response):
        try:
            mobileAgent = response.xpath('//meta[@http-equiv="mobile-agent"]/@content').extract()[0]
            return "http:%s" % re.findall('url=(//.*shtml)', mobileAgent)[0]
        except:
            raise IndexError('getMobileUrl:%s' % response.url)

    # 解析图片链接
    @staticmethod
    def getImageUrl(response):
        return response.xpath('//div[@class="house-basic-info"]/div/div/img/@src').extract()[0].strip()

    # 解析所在城市
    @staticmethod
    def getCity(response):
        return response.xpath('//div[@class="nav-top-bar fl c_888 f12"]/a/text()').extract()[0].split('58')[0]

    # 解析区域
    @staticmethod
    def getDistrict(response):
        try:
            return response.xpath('//div[@class="nav-top-bar fl c_888 f12"]/a/text()').extract()[2].split('租房')[0]
        except:
            return ""

    # 解析月租
    @staticmethod
    def getRental(response):
        _rental = response.xpath('//div[@class="house-pay-way f16"]/span/b/text()').extract()[0]
        if re.match(r'\d+', _rental):
            rental = float(_rental)
        else:
            rental = 0.0
        return rental

    # 解析标题
    @staticmethod
    def getTitle(response):
        return response.xpath('//div[@class="house-title"]/h1/text()').extract()[0].strip()

    # 解析小区名称
    @staticmethod
    def getCampus(response):
        return response.xpath('//div[@class="house-desc-item fl c_333"]/ul/li[4]/span[2]/a/text()').extract()[0].strip()

    # 解析日期
    @staticmethod
    def getDate(response):
        _date = response.xpath('//div[@class="house-title"]/p/text()').extract()[0].strip()
        return Utils.transformDate(_date)
        pass

    # 解析经纬度
    @staticmethod
    def getLatLon(house):
        return Utils.geoSearch(house.city, house.district + house.campus) if house.district!="" else Utils.geoSearchWithAddress(house.city, house.address+house.campus)

    # 解析地址
    @staticmethod
    def getAddress(response):
        return response.xpath('//div[@class="house-desc-item fl c_333"]/ul/li/span/text()').extract()[12].strip()

    # 解析房间数量
    @staticmethod
    def getRooms(houseType):
        return Utils.transformHouseType(houseType)

    # 解析面积
    @staticmethod
    def getArea(response):
        _area = response.xpath('//div[@class="house-desc-item fl c_333"]/ul/li/span/text()').extract()[3].split('\xa0')[
            -3].strip()
        return re.findall('\d+', _area)[0]

    # 解析楼层
    @staticmethod
    def getFloor(response):
        return response.xpath('//div[@class="house-desc-item fl c_333"]/ul/li/span/text()').extract()[5].split('\xa0')[
            -1].strip()

    # 解析联系人
    @staticmethod
    def getContact(response):
        return response.xpath('//div[@class="house-agent-info fr"]/p/a/text()').extract()[0]

    # 解析联系电话
    @staticmethod
    def getPhone(response):
        try:
            return response.xpath('//div[@class="house-chat-phone"]/span/text()').extract()[0]
        except:
            return ''

    # 解析出租类型
    @staticmethod
    def getRentType(response):
        return response.xpath('//div[@class="house-desc-item fl c_333"]/ul/li/span/text()').extract()[1]

    # 解析房屋类型
    @staticmethod
    def getHouseType(response):
        return response.xpath('//div[@class="house-desc-item fl c_333"]/ul/li/span/text()').extract()[3].strip().split(
                '\xa0')[0].strip()


if __name__ == '__main__':
    client = Spider58()
    #url = "http://sh.58.com/zufang/34349364081974x.shtml"
    #client.parseHouse(url)
    client.crawl()