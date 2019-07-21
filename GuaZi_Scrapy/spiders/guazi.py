# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin
import re
from GuaZi_Scrapy.handle_mongo import mongo_url
from GuaZi_Scrapy.items import GuaziScrapyItem


class GuaziSpider(scrapy.Spider):
    name = 'guazi'
    allowed_domains = ['guazi.com']
    #从mongo数据库中获取url
    # start_urls = ['http://guazi.com/']

    def start_requests(self):
        while True:
            #如果可以取到task任务继续执行，否则证明数据库取空，跳出循环
            task = mongo_url.get_task()
            if task:
                print('正在处理：',task['task_url'])
                #第一次因没有cookies而产生异常，第二次请求会加上cookies。因一个url要爬取两次所以不能去重
                yield scrapy.Request(url=task['task_url'],callback=self.parse,dont_filter=True,errback=self.handle_err,meta={'task':task})
            else:
                break

    def handle_err(self,failure):
        # 1、通过meta传参获取task
        task = failure.request.meta['task']
        # {
        #     "_id": ObjectId("5d32f4cef8948acf1c0c4354"),
        #     "task_url": "https://www.guazi.com/zz/ford/o1i7/",
        #     "city_name": "郑州",
        #     "car_name": "福特"
        # }
        # 2、删除掉task中的_id,再重新存入MongoDB数据库
        if '_id' in task:
            task.pop('_id')
        mongo_url.save_task(task)
        print(task['task_url'],'连续3次请求失败，已存入数据库，等待再次尝试')


    #从列表页解析出detail_url、next_url
    def parse(self, response):
        if '为您找到0辆好车' in response.text:
            print('当前城市没有此品牌汽车，数据取空')
            return

        car_urls = response.xpath('//ul[@class="carlist clearfix js-top"]/li/a/@href').extract()
        for car_url in car_urls:
            detail_url = urljoin(response.url,car_url)
            print(detail_url)
            yield scrapy.Request(url=detail_url,callback=self.get_detail,dont_filter=True)
        #提取倒数第二个数字，倒数第一是：下一页
        last_number = response.xpath('//ul[@class="pageLink clearfix"]/li[last()-1]/a/span/text()').extract_first()
        # 提取到证明有下一页，否则只有一页。
        # 此方法由于一次性yield出所欲next_url因此不必自己调自己
        if last_number:
            for num in range(2, int(last_number)+1):
                # https://www.guazi.com/zz/dongnan/o1i7/
                base = f'o{num}i7'
                next_url = re.sub(r'o(\d+)i7', base, response.url)
                yield scrapy.Request(url=next_url, dont_filter=True)


    def get_detail(self,response):
        detail_infos = response.xpath('//div[@class="center js-center detail"]')
        for detail_info in detail_infos:
            item = GuaziScrapyItem()
            item['from_url'] = response.url
            item['car_id'] = detail_info.xpath('.//div[@class="right-carnumber"]/text()').extract_first().split('：')[1].strip()
            # 以下信息在一个整体div，所以封装一个总路径info
            info = detail_info.xpath('./div[@class="infor-main clearfix service-open"]/div[@class="product-textbox"]')
            item['car_name'] = info.xpath('./h2[@class="titlebox"]/text()').extract_first().strip()
            item['license_time'] = info.xpath('./ul[@class="assort clearfix"]/li[contains(.,"上牌时间")]/span/text()').extract_first()
            item['km_info'] = info.xpath('./ul[@class="assort clearfix"]/li[contains(.,"表显里程")]/span/text()').extract_first()
            item['license_location'] = info.xpath('./ul[@class="assort clearfix"]/li[contains(.,"上牌地")]/span/text()').extract_first() if info.xpath('./ul[@class="assort clearfix"]/li[contains(.,"上牌地")]/span/text()') else '上牌地未指定'
            item['desplacement_info'] = info.xpath('./ul[@class="assort clearfix"]/li[contains(.,"排量")]/span/text()').extract_first()
            item['transmission_case'] = info.xpath('./ul[@class="assort clearfix"]/li[contains(.,"变速箱")]/span/text()').extract_first()
            item['car_price'] = ''.join(info.xpath('./div[@class="pricebox js-disprice"]/span[@class="pricestype"]//text()').extract()).replace(' ','')
            yield item


