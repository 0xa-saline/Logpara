#!/usr/bin/env python
#-*- coding:utf-8 -*-
import redis
import os,re,json
from GeoIPUtils import GeoIPUtil,GeoIP2Util
from convert import urldecode,htmlunescape
try:
    from user_agents import parse as ua_parse
except:
    print "try to pip install pyyaml ua-parser user-agents"

import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
    
EXCLUDE_EXTENSIONS = ("ico","3ds", "3g2", "3gp", "7z", "DS_Store", "a", "aac", "adp", "ai", "aif", "aiff", "apk", "ar", "asf", "au", "avi", "bak", "bin", "bk", "bmp", "btif", "bz2", "cab", "caf", "cgm", "cmx", "cpio", "cr2", "dat", "deb", "djvu", "dll", "dmg", "dmp", "dng", "doc", "docx", "dot", "dotx", "dra", "dsk", "dts", "dtshd", "dvb", "dwg", "dxf", "ear", "ecelp4800", "ecelp7470", "ecelp9600", "egg", "eol", "eot", "epub", "exe", "f4v", "fbs", "fh", "fla", "flac", "fli", "flv", "fpx", "fst", "fvt", "g3", "gif", "gz", "h261", "h263", "h264", "ico", "ief", "image", "img", "ipa", "iso", "jar", "jpeg", "jpg", "jpgv", "jpm", "jxr", "ktx", "lvp", "lz", "lzma", "lzo", "m3u", "m4a", "m4v", "mar", "mdi", "mid", "mj2", "mka", "mkv", "mmr", "mng", "mov", "movie", "mp3", "mp4", "mp4a", "mpeg", "mpg", "mpga", "mxu", "nef", "npx", "o", "oga", "ogg", "ogv", "otf", "pbm", "pcx", "pdf", "pea", "pgm", "pic", "png", "pnm", "ppm", "pps", "ppt", "pptx", "ps", "psd", "pya", "pyc", "pyo", "pyv", "qt", "rar", "ras", "raw", "rgb", "rip", "rlc", "rz", "s3m", "s7z", "scm", "scpt", "sgi", "shar", "sil", "smv", "so", "sub", "swf", "tar", "tbz2", "tga", "tgz", "tif", "tiff", "tlz", "ts", "ttf", "uvh", "uvi", "uvm", "uvp", "uvs", "uvu", "viv", "vob", "war", "wav", "wax", "wbmp", "wdp", "weba", "webm", "webp", "whl", "wm", "wma", "wmv", "wmx", "woff", "woff2", "wvx", "xbm", "xif", "xls", "xlsx", "xlt", "xm", "xpi", "xpm", "xwd", "xz", "z", "zip", "zipx")

def push_msg(msg):
    '''
    redis连接池
    '''
    redis_host = '192.168.87.222'
    redis_port = 6379
    redis_pass = 'cft67ygv'
    redis_db = 0
    redis_key = 'logstash:redis'
    try:
        #r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db, password=redis_pass)
        pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db, password=redis_pass)
        r = redis.StrictRedis(connection_pool=pool)
        r.rpush(redis_key, msg)
    except Exception as e:
        print str(e),msg

def is_intranet(ip):
    """
    匹配内网ip地址
    """
    ret = ip.split('.')
    if not len(ret) == 4:
        return True
    if ret[0] == '10':
        return True
    if ret[0] == '127' and ret[1] == '0':
        return True
    if ret[0] == '172' and 16 <= int(ret[1]) <= 32:
        return True
    if ret[0] == '192' and ret[1] == '168':
        return True
    return False

def parser_ua(ua_string):
    '''
    解析user-agent
    '''
    info = {}
    info['spider'] = False
    try:
        msg = ua_parse(ua_string)

        if msg.is_pc:
            info['dev'] = 'PC'
        elif msg.is_tablet:
            info['dev'] = 'Pad'
        elif msg.is_mobile:
            info['dev'] = 'MObile'
        else:
            info['dev'] = 'Unknow'

        if msg.is_bot:
            info['spider'] = True
        info["type"] = msg.os.family+' '+str(msg.os.version_string)

        info["ua"] = msg.browser.family+' '+str(msg.browser.version_string)
        return info
    except Exception as e:
        return info

def parser_ip(ipaddr):
    '''
    解析IP地址的经纬度
    '''
    info = {}
    g1 = GeoIPUtil()
    g2 = GeoIP2Util()
    if is_intranet(ipaddr):
        info["address"] = "局域网内地址"
        info['weidu'] = info['jingdu'] = info['country'] = info['subdivision'] =info['city'] =""
    else:
        try:
            longitude,latitude = g1.get_lat_alt(ipaddr)
            info['weidu'] = latitude
            info['jingdu'] = longitude
            country, subdivision, city =  g2.get_ip_location(ipaddr)
            if country == u"中国":
                if subdivision.find(u'市')==-1:
                    addr = subdivision+u"省\t"+city
                else:
                    addr = subdivision+"\t"+city
            else:
                if subdivision in [u'台北市',u'新北市',u'基隆市',u'新竹市',u'嘉义市',u'台中市',u'台南市',u'高雄市',u'屏东市']:
                    subdivision = "台湾省"
                if country in [u'香港',u'澳门']:
                    subdivision = country +' '+ subdivision
                    country = '中国'
                addr = country.replace(u'台湾',u'中国') +"\t"+subdivision+"\t"+city

            info["address"] = addr
            info["country"] = country.replace(u'台湾',u'中国')
            info["subdivision"]= subdivision
            info["city"] = city
        except Exception as e:
            return info
    return info

def check_rule(file_data):
    '''
    匹配规则
    '''
    rule = ''
    results = []
    try:
        file_data = urldecode(file_data)
    except:
        try:
            file_data = htmlunescape(file_data)
        except:
            file_data = file_data

    try:
        default_conf_path = os.path.abspath(os.path.dirname(__file__)) + "/"
        flist = default_conf_path+"rule.json"
        patterns_list = json.load(file(flist))
        for patterns in patterns_list:
            sensitive = True
            for pattern in patterns['patterns']:
                if pattern['type'] == 'match':
                    re_pattern = re.compile(pattern['part'],  re.IGNORECASE | re.DOTALL | re.MULTILINE)
                    re_result = re.findall(pattern['part'], file_data)
                    if not re_result:
                        sensitive = False
                        break
                elif pattern['type'] == 'regex':
                    re_pattern = re.compile(str(pattern['part']),  re.IGNORECASE | re.DOTALL | re.MULTILINE)
                    if re_pattern.search(file_data) == None:
                        sensitive = False
                        break

                if sensitive:
                    results.append({
                        'tag': patterns['tag'],
                        'level': patterns['level']
                    })
    except Exception as e:
        pass
    return results

if __name__ == '__main__':
    print json.dumps(parser_ip('111.122.172.163'))
    print json.dumps(parser_ip('220.181.171.119'))
    print json.dumps(parser_ip('192.168.199.233'))

    url = "/drupal/?destination=node/8153%23comment-form&q=../../../../../../../../../../WEB-INF/web.xml"
    print check_rule(url)
    ua = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.21 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.21"
    print parser_ua(ua)
    
