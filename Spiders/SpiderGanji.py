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


class SpiderGanji(object):
    source = "赶集网"
    downloader = Downloader()
    runSpider = True

    def __init__(self):
        self.redis = RedisUtils(self)

    def crawl(self):
        while True:
            if self.runSpider:
                url = self.readUrls()
                if url is not None:
                    threading.Thread(target=self.parseHouse, args=(url,)).start()
                else:
                    print('%s Redis服务器中已经没有未爬取的%s链接' % (Utils.getCurrentTime(), self.__class__.__name__))
            else:
                print('%s 赶集网遇到验证码' % Utils.getCurrentTime())
            time.sleep(INTERVAL)

    def crawlSpider(self):
        while True:
            url = self.readUrls()
            if url is None:
                break
            self.parseHouse(url)
            time.sleep(random.randint(10, 30))
            if not self.runSpider:
                print('%s 遇到赶集网防火墙' % Utils.getCurrentTime())
                Utils.write_firewall_error('%s 遇到赶集网防火墙' % Utils.getCurrentTime())
                break

    # 从Redis服务器读取房源链接
    def readUrls(self):
        return self.redis.get_url()

    # 解析房源详情
    def parseHouse(self, url):
        response = self.downloader.download_html_response(url)
        if response is None:
            Utils.write_error('赶集网下载网页失败 %s' % url)
            print('%s 赶集网下载网页失败%s' % (Utils.getCurrentTime(), url))
            return True

        if self.checkVeriCode(response):
            Utils.write_error('赶集网遇到验证码')
            print('%s 赶集网遇到验证码' % Utils.getCurrentTime())
            self.runSpider = False
            return False

        if response.status == 404:
            Utils.write_error('赶集网网页不存在 %s' % url)
            print('%s 赶集网网页不存在 %s' % (Utils.getCurrentTime(), url))
            return True

        house = House()
        house.url = self.getMobileUrl(response)
        print(house.url)
        house.title = self.getTitle(response)
        house.image_url = self.getImageUrl(response)
        house.city = self.getCity(response)
        house.district = self.getDistrict(response)
        house.rental = self.getRental(response)
        house.campus = self.getCampus(response)
        house.date = self.getDate(response)
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
            print('%s 赶集网过期房源:%s;%s;%s' % (Utils.getCurrentTime(), house.date, house.title, house.url))
        elif house.isValidHouse():
            DB_Manager(house)
        return True

    # 解析手机页面链接
    @staticmethod
    def getMobileUrl(response):
        url_ = response.xpath('//meta[@name="mobile-agent"]/@content').extract()[0]
        return "https://%s" % re.findall(r'url=http://(.+)', url_)[0]

    # 解析图片链接
    @staticmethod
    def getImageUrl(response):
        return response.xpath('//div[@class="big-img-wrap"]/img/@src').extract()[0]

    # 解析所在城市
    @staticmethod
    def getCity(response):
        city_ = response.xpath('//meta[@name="location"]/@content').extract()[0]
        return re.findall(r'city=(.+?);', city_)[0]

    # 解析区域
    @staticmethod
    def getDistrict(response):
        district_ = response.xpath('//div[@class="f-crumbs f-w1190"]/a[4]/text()').extract()[0]
        return re.findall('(.*)租房', district_)[0]

    # 解析月租
    @staticmethod
    def getRental(response):
        return float(response.xpath('//li[@class="price"]/span[2]/text()').extract()[0])

    # 解析标题
    @staticmethod
    def getTitle(response):
        try:
            return response.xpath('//div[@class="big-img-wrap"]/img/@title').extract()[0]
        except:
            print('Error! getTitle()')

    # 解析小区名称
    @staticmethod
    def getCampus(response):
        try:
            return response.xpath('//ul[@class="er-list-two f-clear"]/li/span[@class="content"]/a/text()').extract()[0]
        except:
            print('Error! getCampus()')
            Utils.write_error('%s 赶集网解析小区错误 %s' % (Utils.getCurrentTime(), response.url))

    # 解析日期
    @staticmethod
    def getDate(response):
        date_ = response.xpath('//div[@class="card-status f-clear"]/ul/li/text()').extract()[0]
        return Utils.transformDate(date_)
        pass

    # 解析经纬度
    @staticmethod
    def getLatLon(house):
        try:
            return Utils.geoSearchWithAddress(house.city, house.district + house.campus)
        except:
            Utils.write_error('%s 赶集网解析经纬度错误 %s' % (Utils.getCurrentTime(), house.url))
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
        rent_ = response.xpath('//ul[@class="er-list f-clear"]/li/span[@class="content"]/text()').extract()[1]
        return re.findall('(\d+)', rent_)[0]

    # 解析楼层
    @staticmethod
    def getFloor(response):
        return response.xpath('//ul[@class="er-list f-clear"]/li/span[@class="content"]/text()').extract()[3]

    # 解析联系人
    @staticmethod
    def getContact(response):
        return response.xpath('//div[@class="user-info-top"]/p/text()').extract()[0].strip()

    # 解析联系电话
    @staticmethod
    def getPhone(response):
        try:
            return response.xpath('//div[@class="c_phone f-clear"]/@data-phone').extract()[0]
        except:
            return ''

    # 解析出租类型
    @staticmethod
    def getRentType(response):
        rent_ = response.xpath('//ul[@class="er-list f-clear"]/li/span[@class="content"]/text()').extract()[1]
        return rent_.split('\xa0')[0]

    # 解析房屋类型
    @staticmethod
    def getHouseType(response):
        return response.xpath('//ul[@class="er-list f-clear"]/li/span[@class="content"]/text()').extract()[0].strip()

    # 检查是否遇到验证码
    @staticmethod
    def checkVeriCode(response):
        try:
            content = response.xpath('//title/text()').extract()[0]
            if re.search(r'验证码', content):
                return True
            else:
                return False
        except:
            return False


if __name__ == '__main__':
    client = SpiderGanji()
    client.crawl()
    # url = 'http://sz.ganji.com/fang1/2968020430x.htm'
    # client.parseHouse(url)
    # client.parseHouse('http://sz.ganji.com/fang1/2958058371x.htm')
