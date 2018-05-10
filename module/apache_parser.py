#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime
import re,urllib

request_re= re.compile(r'(?P<request_method>(GET|POST|HEAD|DELETE|PUT|OPTIONS)?)\s+(?P<request_uri>.*?)\s+(?P<server_protocol>.*)$')
log_line_re = re.compile(r'(?P<remote_host>((\d{1,3}\.){3}\d{1,3})+) - - (\[(?P<date_time>\S+)\s+\S+\])\s+\"(?P<request>(.*?))\"\s+(?P<status>([1-9]\d*))\s+(?P<body_bytes_sent>(.*?))\s+\"(?P<http_referer>.*?)\"\s+\"(?P<http_user_agent>.*?)\"')
logline_re = re.compile(r'(?P<remote_host>((\d{1,3}\.){3}\d{1,3})+) - - (\[(?P<date_time>\S+)\s+\S+\])\s+\"(?P<request>(.*?))\"\s+(?P<status>([1-9]\d*))\s+(?P<body_bytes_sent>(.*?))')

"""
192.168.0.23 - - [19/Aug/2017:05:33:54 +0200] "GET /drupal/templates/blue/js/default.js HTTP/1.1" 404 402 "http://192.168.0.102/drupal/templates/blue/js/default.js" "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
ip time method url status body referer ua
"""
class ApahceParser(object):
    """将 Apache 日志解析成多个字段"""

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
        processed = log_line_re.search(line)
        if processed:
            #ip_time_tmp = line_item[2].strip().split()
            self.cdn_ip = processed.group('remote_host') # 服务器IP
            self.access_time = processed.group('date_time')# 请求发起的时间
            request = processed.group('request')
            request_ur = request_re.search(request)
            if request_ur:
                self.method = request_ur.group('request_method') # 请求方式
                self.request_url = request_ur.group('request_uri')
            self.response_status = processed.group('status') # NG 响应状态码
            self.bbytes = processed.group('body_bytes_sent') # 浏览所用时间
            if self.bbytes == "-":
                self.bbytes = ""
            self.browser = processed.group('http_user_agent')
            self.reference_url = processed.group('http_referer') # 外链URL
            '''
            self.port = line_item[6]
            self.reference_url = "" # 外链URL
            self.real_ip = line_item[8].strip()
            
             # 用户使用的浏览器
            
            '''
        else:
            processed = logline_re.search(line)
            if processed:
                self.cdn_ip = processed.group('remote_host') # 服务器IP
                self.access_time = processed.group('date_time')# 请求发起的时间
                request = processed.group('request')
                request_ur = request_re.search(request)
                if request_ur:
                    self.method = request_ur.group('request_method') # 请求方式
                    self.request_url = request_ur.group('request_uri')
                self.response_status = processed.group('status') # NG 响应状态码
                self.bbytes = processed.group('body_bytes_sent') # 浏览所用时间
                if self.bbytes == "-":
                    self.bbytes = ""

    def to_dict(self):
        """将属性(@property)的转化为dict输出
        """
        propertys = {}
        propertys['real_ip'] = self.real_ip
        propertys['cdn_ip'] = self.cdn_ip
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
        """
        解析请求的URL
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
        # Apache log 解析日志格式
        #input_datetime_format = '%d/%b/%Y:%H:%M:%S'
        input_datetime_format = '%d/%b/%Y:%H:%M:%S'
        self._access_time = datetime.datetime.strptime( access_time,input_datetime_format)

    @property
    def cdn_ip(self):
        return self._cdn_ip

    @cdn_ip.setter
    def cdn_ip(self, cdn_ip):
        self._cdn_ip = cdn_ip

if __name__ == '__main__':
    pass
    