#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pygeoip, geoip2.database, os, re

class GeoIPUtil():
    def __init__(self):
        self.geocity = pygeoip.GeoIP(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../GeoIPData', 'GeoLiteCity.dat'))
        self.geoasn = pygeoip.GeoIP(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../GeoIPData', 'GeoIPASNum.dat'))
        self.as_re = re.compile('AS(?P<num>\d+)(?: (?P<name>.+))?')

    def get_AS_info_by_ip(self, ip):
        asn = self.geoasn.asn_by_addr(ip)
        if asn != None:
            (asnum, asname) = self.as_re.match(asn).groups()
        else:
            (asnum, asname) = (0, 'None')
        return (asnum, asname)
    
    def get_lat_alt(self, ip):
        loc=self.geocity.record_by_name(ip)
        if loc is None:
            return None
        return [loc['longitude'],loc['latitude']]

class GeoIP2Util():
    def __init__(self):
        self.reader = geoip2.database.Reader(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../GeoIPData', 'GeoLite2-City.mmdb'))

    def get_lat_alt(self, ip):
        response = self.reader.city(ip)
        if response is None:
            return None
        return [response.location.longitude, response.location.latitude]

    def get_ip_location(self, ip):
        response = self.reader.city(ip)

        if response.country.names.has_key('zh-CN'):
            country = response.country.names['zh-CN']
        else:
            country = response.country.name
        if response.subdivisions.most_specific.names.has_key('zh-CN'):
            subdivision = response.subdivisions.most_specific.names['zh-CN']
        else:
            subdivision = response.subdivisions.most_specific.name
        if response.city.names.has_key('zh-CN'):
            city = response.city.names['zh-CN']
        else:
            city = response.city.name
        return (country, subdivision, city)

if __name__ == '__main__':
    gi = GeoIPUtil()
    longitude,latitude = gi.get_lat_alt('220.181.171.119')
    print latitude,",",longitude
    gi = GeoIP2Util()
    #longitude1,latitude1 = gi.get_lat_alt('220.181.171.119')
    #print longitude1,latitude1
    country, subdivision, city =  gi.get_ip_location('220.181.171.119')
    print country, subdivision, city
