#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime
import urllib
'''
date time           日期/时间
s-ip                服务器IP
cs-method           方法
cs-uri-stem         请求访问的页面
cs-uri-query        访问的查询字符串
s-port              服务器端口
cs-username         
c-ip                客户端IP
cs(User-Agent)      用户代理
sc-status           协议返回状态
sc-substatus        HTTP子协议的状态
sc-win32-status     Win32® 状态
time-taken          所用时间
'''
class IISLineParser(object):
    """将 Nginx 日志解析成多个字段"""

    def __init__(self):
        self._cdn_ip = '' # CDN请求IP
        self._access_time = '' # 请求时间
        self._request_url = '' # 请求的URL
        self._reference_url = '' # 外链URL
        self._response_status = '' # NG 响应状态码
        self._browser = '' # 用户使用的浏览器
        self._real_ip = '' # 用户真实IP
        self._mthod = '' # 请求方式
        self._bbytes = '' # 内容大小

    def parse(self, line):
        """通过传入的一行数据进行解析
        """
        line_item = line.strip().split(' ')

        #ip_time_tmp = line_item[2].strip().split()
        self.cdn_ip = line_item[2] # 服务器IP
        self.access_time = str(line_item[0]+" "+ line_item[1])# 请求发起的时间
        self.method = line_item[3].strip() # 请求方式
        if line_item[5].strip() == "-":
            self.request_url = line_item[4].strip() # 请求的URL
        else:
            self.request_url = line_item[4].strip()+"?"+ line_item[5].strip()
        self.port = line_item[6]
        self.reference_url = "" # 外链URL
        self.real_ip = line_item[8].strip()
        self.response_status = line_item[10].strip() # NG 响应状态码
        self.browser = line_item[9].strip() # 用户使用的浏览器
        self.bbytes = line_item[13].strip() # 浏览所用时间

    def to_dict(self):
        """将属性(@property)的转化为dict输出
        """
        propertys = {}

        propertys['real_ip'] = self.real_ip
        propertys['ser_ip'] = self.cdn_ip
        propertys['method'] = self.method
        propertys['access_time'] = self.access_time
        propertys['request_url'] = self.request_url
        propertys['reference_url'] = self.reference_url
        propertys['response_status'] = self.response_status
        propertys['browser'] = self.browser
        propertys['bbytes'] = self.bbytes
        return propertys

    @property
    def real_ip(self):
        return self._real_ip

    @real_ip.setter
    def real_ip(self, real_ip):
        self._real_ip = real_ip.split(', ')[0]

    @property
    def browser(self):
        return self._browser

    @browser.setter
    def browser(self, browser):
        self._browser = browser.replace('+',' ')

    @property
    def response_status(self):
        return self._response_status

    @response_status.setter
    def response_status(self, response_status):
        self._response_status = response_status

    @property
    def reference_url(self):
        return self._reference_url

    @reference_url.setter
    def reference_url(self, reference_url):
        """解析外链URL
        只需要解析后的域名, 如:
            传入: http://www.ttmark.com/diannao/2014/11/04/470.html
            解析成: www.ttmark.com
        """
        proto, rest = urllib.splittype(reference_url)
        res, rest = urllib.splithost(rest)
        if not res:
            self._reference_url = '-'
        else:
            self._reference_url = res

    @property
    def request_url(self):
        return self._request_url

    @request_url.setter
    def request_url(self, request_url):
        """解析请求的URL
        只需要解析后的URL路径不需要参数, 如:
            传入: /wp-admin/admin-ajax.php?postviews_id=1348
            解析成: /wp-admin/admin-ajax.php
        
        proto, rest = urllib.splittype(request_url)
        url_path, url_param = urllib.splitquery(rest)

        if url_path.startswith('/tag/'):
            url_path = '/tag/'
        """
        self._request_url = request_url

    @property
    def access_time(self):
        return str(self._access_time)

    @access_time.setter
    def access_time(self, access_time):
        # IIS log 解析日志格式
        #input_datetime_format = '%d/%b/%Y:%H:%M:%S'
        input_datetime_format = '%Y-%m-%d %H:%M:%S'
        self._access_time = datetime.datetime.strptime( access_time,input_datetime_format)

    @property
    def cdn_ip(self):
        return self._cdn_ip

    @cdn_ip.setter
    def cdn_ip(self, cdn_ip):
        self._cdn_ip = cdn_ip

if __name__ == '__main__':
    pass
    