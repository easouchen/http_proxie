# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from lxml import etree
from http_prox.items import HttpProxItem

class XcipSpider(scrapy.Spider):
    '''
        爬取xcip.com中的代理ip
    '''
    name = 'xcip'
    allowed_domains = ['xicidaili.com']
    start_urls = ['http://www.xicidaili.com/']

    def parse(self, response):
        '''
            定义爬取的页数
        :param response:
        :return:
        '''
        #wn:https,wt:http
        nav_list = ['wn','wt']

        #主要爬取两种协议：http,https
        for i in nav_list:
            # if i =='wt':return
            #定义爬取1到50页
            for y in range(1,51):
                # if y>1:return
                url ='http://www.xicidaili.com/%s/%s'%(i,y)
                yield Request(url=url,callback=self.get_ip,meta={'type':i})

    def get_ip(self,response):
        '''
            爬取ip地址，并保存至item中
        :param response:
        :return:
        '''
        item = HttpProxItem()
        # print response.body

        #由于返回的数据在response.body中，所以不能直接使用response.xpath
        #先使用lxml.etree模块将数据格式化，再使用xpath来匹配ip数据
        html_etree = etree.HTML(response.body)
        ip_list = html_etree.xpath("//tr[position()>1]/td[position()<4]/text()")
        # print ip_list

        #得到ip、端口这两个数据后，在列表中，每两个为一组，分别保存起来
        for i in range(0,len(ip_list),2):
            item['ipaddr']=ip_list[i]
            item['port'] = ip_list[i+1]
            item['position'] = response.meta['type']
            print item['ipaddr'],item['port']
            yield item
