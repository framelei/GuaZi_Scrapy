import requests
import execjs
import re
from scrapy.selector import Selector
from GuaZi_Scrapy.handle_mongo import mongo_url


headers = {
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "Cache-Control":"no-cache",
    "Connection":"keep-alive",
    "Host":"www.guazi.com",
    "Pragma":"no-cache",
    "Referer":"https://www.guazi.com/www/buy/c-1",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
}
start_url = 'https://www.guazi.com/www/buy/c-1/'
resp = requests.get(url=start_url,headers=headers)
resp.encoding = 'utf-8'
# print(resp.status_code)     #203
# print(resp.text)            #eval(function(p,a,c,k,e,r)     <p>正在打开中,请稍后...<e style='float:right'>2019-07-20 13:54:31</e><p>

if '正在打开中,请稍后' in resp.text:
    #1、获取anti的加密参数
    string = re.search(r"anti\('(.*?)','(.*?)'\);", resp.text).group(1)         #t252Ia5xS/njljXxFuF8L4e9a5oswywo+3t3rkMlXps=
    key = re.search(r"anti\('(.*?)','(.*?)'\);", resp.text).group(2)            #541265482128722396238567

    #2、读取我们破解的js文件
    with open('guazi.js','r',encoding='utf-8') as f:
        f_read = f.read()

    #3、使用execjs包来封装这段js，传入读取后的js文件
    js = execjs.compile(f_read)
    value = js.call('anti',string,key)          #4j7070622587246G1833q7703ltO39

    #4、重新封装请求头，发起第二次请求
    headers['Cookie'] = 'antipas=' + value
    resp_second = requests.get(url=start_url,headers=headers).text

    #5、使用re匹配全国30座热门城市      # <a href="/nn/" target="_blank">南宁二手车</a>
    city_infos = re.findall(r'<a href="(.*?)" target="_blank">(.*?)二手车</a>', resp_second)

    # 6、解析所有汽车品牌
    response = Selector(text=resp_second)
    car_infos = response.xpath('//dl[@class="clearfix"]/dd/div/ul/li/p/a')

    # 7、根据城市、汽车品牌动态构造所有的url，存在一种情况：小城市里没有二手豪车
    # https://www.guazi.com/gz/dazhong/o2i7/
    # gz:广州   dazhong:大众  o2:第二页  i7:最新发布排序
    for city_info in city_infos:
        city_url, city_name = city_info         #city_url: /nn/        city_name:南宁
        if city_name == '郑州':
            for car_info in car_infos:
                car_name = car_info.xpath('./text()').extract_first()       #奥迪
                url = car_info.xpath('./@href').extract_first()         # /www/audi/c-1/#bread
                car_url = re.search(r'/.*?/(.*?)/c-1/',url).group(1)    # audi
                info = {}
                info['task_url'] = f'https://www.guazi.com{city_url}{car_url}/o1i7/'
                info['city_name'] = city_name
                info['car_name'] = car_name
                mongo_url.save_task(info)

