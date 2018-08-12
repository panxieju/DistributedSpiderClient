import json


class House(object):
    title = str
    url = str
    image_url = str
    lat = float
    lon = float
    rental = float
    house_type = str
    rent_type = str
    area = str
    floor = str
    campus = str
    city = str
    district = str
    date = str
    rooms = int
    address = str
    source = str
    contact = str
    phone = str
    md5 = str
    time = str

    def isValidHouse(self):
        if self.url is None or self.url == "":
            return False
        if self.title is None or self.title == "":
            return False
        if self.house_type is None or self.house_type == "":
            return False
        if self.district is None or self.district == "":
            return False
        if self.campus is None or self.campus == "":
            return False
        if self.lat == 0.0:
            return False
        return True


