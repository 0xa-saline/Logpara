#!/usr/bin/env python
#-*- coding:utf-8 -*-

from module.apache_parser import ApahceParser
from module.iis_parser import IISLineParser
from module.nginx_parser import NgLineParser
from module.tomcat_parser import TomcatParser
from common.threadpool import new_threadpool
from optparse import OptionParser
from common.units import *

def check_file(path):
    '''
    检测文件是目录还是文件
    '''
    import os
    if os.path.isdir(path):
        return "directory"
    elif os.path.isfile(path):
        return "file"
    else:
        return False

def para(line,xtype):
    '''
    对日志类型进程分类处理
    '''
    if xtype == "apache":
        ng_line_parser = ApahceParser()
    elif xtype == "iis":
        ng_line_parser = IISLineParser()
    elif xtype == "nginx":
        ng_line_parser = NgLineParser()
    elif xtype == "tomcat":
        ng_line_parser = TomcatParser()
    else:
        return "not found,waitting...."
    if line.startswith("#"):
        pass
    else:
        try:
            ng_line_parser.parse(line)
            if ng_line_parser.real_ip:
                ippara = parser_ip(ng_line_parser.real_ip)
            else:
                ippara = parser_ip(ng_line_parser.cdn_ip)

            if ng_line_parser.browser:
                parses = parser_ua(ng_line_parser.browser)
                mydict = {
                    "status":ng_line_parser.response_status, 
                    "cdn_ip":ng_line_parser.real_ip,
                    "real_ip":ng_line_parser.cdn_ip,
                    "access_time":ng_line_parser.access_time,
                    "method":ng_line_parser.method,
                    "url":ng_line_parser.request_url,
                    "urldecode":urldecode(ng_line_parser.request_url),
                    "referer":ng_line_parser.reference_url,
                    "body_bytes":ng_line_parser.bbytes,
                    "user_agent":ng_line_parser.browser,
                    "ua_value":parses['ua'],
                    "dev_type":parses['dev'],
                    "dev_value":parses['type'],
                    "spider":parses['spider'],
                    "addr":ippara['address'],
                    "city":ippara['city'],
                    "jingdu":ippara['jingdu'],
                    "weidu":ippara['weidu'],
                    "country":ippara['country'],
                    "subdivision":ippara['subdivision'],
                    }
            else:
                mydict = {
                    "status":ng_line_parser.response_status, 
                    "cdn_ip":ng_line_parser.cdn_ip,
                    "real_ip":ng_line_parser.real_ip,
                    "access_time":ng_line_parser.access_time,
                    "method":ng_line_parser.method,
                    "url":ng_line_parser.request_url,
                    "urldecode":urldecode(ng_line_parser.request_url),
                    "referer":ng_line_parser.reference_url,
                    "body_bytes":ng_line_parser.bbytes,
                    "user_agent":ng_line_parser.browser,
                    "addr":ippara['address'],
                    "city":ippara['city'],
                    "jingdu":ippara['jingdu'],
                    "weidu":ippara['weidu'],
                    "country":ippara['country'],
                    "subdivision":ippara['subdivision'],
                    }
            resu = check_rule(ng_line_parser.request_url)
            if resu:
                if len(resu)==1:
                    mydict["rule"]= resu[0]
                else:
                    mydict["rule"]= resu
            else:
                mydict["rule"]= False
            '''
            try:
                push_msg(json.dumps(mydict))
            except Exception as e:
                try:
                    del mydict["url"]
                    del mydict["urldecode"]
                    mydict["url"] = str(ng_line_parser.request_url).decode('gbk', 'ignore').encode('utf-8', 'ignore')
                    mydict["urldecode"] = str(ng_line_parser.request_url).decode('gbk', 'ignore').encode('utf-8', 'ignore')
                    push_msg(json.dumps(mydict))
                except Exception as why:
                    print why
                    print mydict
                    pass
            '''
            return json.dumps(mydict)
        except Exception as why:
            print why
            pass

def push_para(xtype,logfile):
    '''
    对每一个文件进行处理
    '''
    with open(logfile, 'r') as f:
        #p = new_threadpool(3, calucator)
        for index, line in enumerate(f):
            print para(line,xtype)

def main(xtype,log_name):
    '''
    检测文件的类型
    '''
    xcheck = check_file(log_name)
    if not xcheck:
        print "file not found"
        return
    else:
        if xcheck == "directory":
            files = get_file(log_name)
            for xfile in files:
                push_para(xtype,log_name+"/"+xfile)
        else:
            push_para(xtype,log_name)

def get_file(mypath):
    '''
    获取文件夹下面的全部文件
    '''
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
    return onlyfiles

def init_parser():
    usage = "Usage: %prog --type IIS|Apache|Tomcat|Nginx --file file|directory"
    parser = OptionParser(usage=usage, description="log parser ")
    parser.add_option("--type", type="str", dest="type", help="chose which log type")
    parser.add_option("--file", type="str", dest="file", default=None,help="chose file or directory")
    return parser

if __name__ == '__main__':
    #main('./log/access.log.9')
    parser = init_parser()
    option, _ = parser.parse_args()
    logtype = str(option.type).lower()
    logfile  = option.file
    if not logfile or not logtype:
        parser.print_help()
    
    main(logtype,logfile)
