# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import requests
from lxml import etree
import urllib2

class HttpProxPipeline(object):

    def __init__(self):
        '''
            初始化链接数据库,里面的参数需要自行修改
        '''
        self.conn = pymysql.connect(host='127.0.0.1',user='user_name',passwd='pass_word',db='db_name',use_unicode=True,charset='utf8')

    def process_item(self, item, spider):
        '''
            获取代理IP，并检测后，放入数据库
        :param item:
        :param spider:
        :return:
        '''
        #获得代理IP的地址，端口
        ipaddr = item['ipaddr']
        port = item['port']
        positions = item['position']
        active = '1'

        #判断数据是否正常
        if all([ipaddr,port,positions]):
            #判断数据库中是否已经存在此ip
            select_str = 'select ipaddr from iptable where ipaddr = "%s"'%item['ipaddr']
            if not self.conn.query(select_str): #如果ip不在数据库中，则测试其联通性
                #wn对应为'htts',wt对应http,判断ip对应的协议类型
                if positions =='wn':
                    proxies ={"https":"https://%s:%s"%(ipaddr,port)}
                else:
                    proxies = {"https": "https://%s:%s" % (ipaddr, port)}
                #测试连通性
                test_result = self.test_ip(proxies)
                if test_result: #如果能使用，则放入数据库
                    print 'start insert',ipaddr
                    in_str = "insert into iptable(ipaddr,port,position) values('"+ipaddr+"','"+port+"','"+positions+"');"
                    # print in_str
                    self.conn.query(in_str)
                    self.conn.commit()
                    print ipaddr,'is insert...'
                else:
                    print ipaddr,'is wrong'
        return item



    def test_ip(self,proxies):
        '''
            测试ip的联通性
,实际项目，请使用项目目标网站来测试        :param proxies:
        :return:
        '''
        url = 'http://www.baidu.com/'
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0'}
        try:
          content = requests.get(url=url,headers=headers,timeout=3,proxies=proxies)
          # print content.content
          if content.status_code == 200:
              print 'connect successed...'
              return 1
          else:
              return 0
        except Exception as e:
            print e
            pass


    def close_spider(self):
        '''
            关闭数据库连接
        :return:
        '''
        self.conn.close()