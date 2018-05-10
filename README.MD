## Logpara
> 一个对常见的web日志进行解析处理的粗糙DEMO。  

[![Python 2.7](https://img.shields.io/badge/python-2.7-yellow.svg)](https://www.python.org/)  [![License](https://img.shields.io/badge/license-GPLv2-red.svg)]

#### 目标
- 对被请求的URL进行解析，解析出是否常见的攻击方式
- 对来访的IP进行深度解析，包含经纬度,物理地址
- 对来访的UA进行深度解析，解析出设备，是否爬虫
- 把全部的日志解析了入库，做RELK处理


### TO DO
- 对入库elasticsearch的日志进行处理并展示


### Useage
- 使用之前先修改common/units.py
    ```
    redis_host = '192.168.87.222'
    redis_port = 6379
    redis_pass = 'cft67ygv'
    redis_db = 0
    redis_key = 'logstash:redis'
    ```

- 使用

```
Usage: main.py --type IIS|Apache|Tomcat|Nginx --file file|directory

log parser

Options:
  -h, --help   show this help message and exit
  --type=TYPE  chose which log type
  --file=FILE  chose file or directory
```

RELK是什么
----
* elasticsearch
* logstash
* kibana
* redis


以上这些程序的首字母、简称，每次都打出全部的感觉好累，就这样简称吧。

服务器要求
----
```
elk+redis 一台    简称为ELK机器
```

RELK机器配置
----

##### redis设置密码

##### 修改 ElasticSearch 配置 `sudo vim /etc/elasticsearch/elasticsearch.yml`，搜索`network.host`，修改如下配置
```
network.host: localhost
```

##### 添加 Logstash 配置 `sudo vim /etc/logstash/conf.d/config.conf`
```
input {    
    redis {
        host => '127.0.0.1'
        password => 'password'
        data_type => 'list'
        key => 'logstash:redis'
    }
}
output {
    elasticsearch { hosts => localhost }
    stdout { codec => rubydebug }
}
```

##### 运行Logstash
```
sudo nohup /opt/logstash/bin/logstash -f /etc/logstash/conf.d/ &
```

##### 修改 Kibana 配置 `sudo vim /opt/kibana/config/kibana.yml`，搜索`server.host`，修改如下配置：
```
server.host: "0.0.0.0"
```

##### 以上修改配置之后均要重启一次服务。


流程

## FAQ
- 非常规配置的日志不能识别？  
    不能识别也是很难受，但是自己修改正则去匹配吧
- 没有weblogic/oracle日志模块？  
    暂时没有测试环境


## 免责
日志分析的项目仅用于学习，自检网络安全，禁止用于其他用途。

