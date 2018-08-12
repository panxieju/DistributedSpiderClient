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


class SpiderFang(object):
    source = "房天下"
    downloader = Downloader()
    runSpider = True

    def __init__(self):
        self.redis = RedisUtils(self)

    # 解析房源详情
    def parseHouse(self, url):
        response = self.downloader.download_html_response(url)
        if response is None:
            print('%s 房天下下载网页失败%s' % (Utils.getCurrentTime(), url))
            return True

        if response.status == 404:
            Utils.write_error('房天下网页不存在 %s' % url)
            print('%s 房天下网页不存在 %s' % (Utils.getCurrentTime(), url))
            return True

        if self.titleNotExist(response):
            Utils.write_error('房天下网页不存在 %s' % url)
            print('%s 房天下网页不存在 %s' % (Utils.getCurrentTime(), url))
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
        house.lat, house.lon = self.getLatLon(house)
        house.md5 = Utils.generateMD5(house.url)
        house.time = Utils.getCurrentTime()

        timedelta = datetime.datetime.now() - datetime.datetime.strptime(house.date, '%Y-%m-%d')
        days = timedelta.days
        if days > 7:
            print('%s 房天下过期房源:%s;%s;%s' % (Utils.getCurrentTime(), house.date, house.title, house.url))
        elif house.isValidHouse():
            DB_Manager(house)
        return True


    @staticmethod
    def checkExpired(response):
        try:
            tip = response.xpath('//div[@class="tipBox"]/h3/text()').extract()[0].encode('gb2312')

            if re.search(r'很抱歉',tip):
                return True
            else:
                return False
        except:
            return False

    # 解析手机页面链接
    @staticmethod
    def getMobileUrl(response):
        try:
            url_ = response.xpath('//meta[@name="mobile-agent"]/@content').extract()[0]
            mobile_url = re.findall('http.*', url_)[0].split('?')[0]
            return mobile_url
        except:
            return None

    # 解析图片链接
    @staticmethod
    def getImageUrl(response):
        try:
            return response.xpath('//div[@class="bigImg"]/img/@src').extract()[0]
        except:
            print("无法解析图像链接:%s"%response.url)
            return ""

    # 解析所在城市
    @staticmethod
    def getCity(response):
        return response.xpath('//div[@class="s4Box"]/a/text()').extract()[0]

    # 解析区域
    @staticmethod
    def getDistrict(response):
        return response.xpath('//div[@class="trl-item2 clearfix"]/div[2]/a/text()').extract()[1]

    # 解析月租
    @staticmethod
    def getRental(response):
        try:
            rental = response.xpath('//div[@class="trl-item sty1"]/i/text()').extract()[0]
            return rental
        except IndexError:
            print("爬取房租错误")
    # 解析标题
    @staticmethod
    def getTitle(response):
        try:
            return response.xpath('//h1[@class="title"]/text()').extract()[0].strip()
        except:
            print("getTitleError:%s"%response.url)

    @staticmethod
    def titleNotExist(response):
        try:
            title = response.xpath('//h1')
            if title is not None and len(title) > 0:
                return False
            else:
                return True
        except:
            return True
    # 解析小区名称
    @staticmethod
    def getCampus(response):
        return response.xpath('//div[@class="trl-item2 clearfix"]/div[2]/a/text()').extract()[0]

    # 解析日期
    @staticmethod
    def getDate(response):
        datetime = response.xpath('//p[@class="gray9 fybh-zf"]/span[2]/text()').extract()[0]
        _date = re.findall(r'\d+-\d+-\d+', datetime)[0]
        return Utils.transformDate(_date)

    # 解析经纬度
    @staticmethod
    def getLatLon(house):
        return Utils.geoSearch(house.city, house.district + house.campus)

    # 解析地址
    @staticmethod
    def getAddress(response):
        return response.xpath('//div[@class="trl-item2 clearfix"]/div[2]/a/text()').extract()[3]

    # 解析房间数量
    @staticmethod
    def getRooms(houseType):
        return Utils.transformHouseType(houseType)

    # 解析面积
    @staticmethod
    def getArea(response):
        return response.xpath('//div[@class="tr-line clearfix"]/div/div[@class="tt"]/text()').extract()[2]

    # 解析楼层
    @staticmethod
    def getFloor(response):
        return response.xpath('//div[@class="tr-line clearfix"]/div/div[@class="tt"]/text()').extract()[4]

    # 解析联系人
    @staticmethod
    def getContact(response):
        return response.xpath('//div[@class="tjcont-list-c "]/div/span/a/text()').extract()[0]

    # 解析联系电话
    @staticmethod
    def getPhone(response):
        try:
            return response.xpath('//div[@class="tjcont-list-c "]/div[3]/text()').extract()[0]
        except:
            return ''

    # 解析出租类型
    @staticmethod
    def getRentType(response):
        return response.xpath('//div[@class="tr-line clearfix"]/div/div[@class="tt"]/text()').extract()[0]

    # 解析房屋类型
    @staticmethod
    def getHouseType(response):
        return response.xpath('//div[@class="tr-line clearfix"]/div/div[@class="tt"]/text()').extract()[1]

if __name__ == '__main__':
    client = SpiderFang()
    url = "http://zu.sh.fang.com/chuzu/3_324751882_1.htm"
    #client.parseHouse(url)
    client.parseHouse(url)
