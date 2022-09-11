import scrapy
import re
import urllib
from baike_spider.items import BaikeSpiderItem
from pymongo import MongoClient


class BaikeSpider(scrapy.Spider):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['baikehk']
    baike_items = db['baike_items']
    olds = set([item['title'] for item in baike_items.find({}, {'title': 1})])
   
    name = 'baike'
    allowed_domains = ['baike.baidu.hk']
    start_urls = ['https://baike.baidu.hk/search/none?word=%E7%8E%8B']

    def parse(self, response):
        page_url = response.request.url
        item_name = re.sub('/', '', re.sub('https://baike.baidu.hk/item/',
                                           '', urllib.parse.unquote(response.url)))
        head_title = ''.join(response.xpath('//dd[@class="lemmaWgt-lemmaTitle-title"]/h1/text()').getall()).replace('/', '')
        sub_title = ''.join(response.xpath('//dd[@class="lemmaWgt-lemmaTitle-title"]/h2/text()').getall()).replace('/', '')
        title = head_title + sub_title
        if title in self.olds:
            print('*' * 20)
            return
     
        baike_item = BaikeSpiderItem()
        baike_item['page_url'] = page_url
        baike_item['baike_id'] = item_name
        baike_item['title'] = title
        baike_item['name'] = head_title
        baike_item['text'] = ''
        for para in response.xpath('//div[@class="main-content"]/div[@class="para"] |//div[@class="main_tab main_tab-defaultTab  curTab"]/div[@class="para"] | //div[@class="lemma-summary"]/div[@class="para"]'):
                texts = para.xpath('.//text()').extract()
                for text in texts:
                    baike_item['text'] += text.strip('\n')
        yield baike_item
        self.olds.add(title)

        items = set(response.xpath(
            '//a[contains(@href, "/item/")]/@href').re(r'/item[/A-Za-z0-9%#?=/\u4E00-\u9FA5]+'))
        for item in items:
            new_url = 'https://baike.baidu.hk' + urllib.parse.unquote(item)
            # yield scrapy.Request(new_url, callback=self.parse)
            yield response.follow(new_url, callback=self.parse)