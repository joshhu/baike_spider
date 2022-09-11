# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class BaikeSpiderPipeline:
    def open_spider(self, spider):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['baikehk']
        self.baike_items = self.db['baike_items']
 
    def process_item(self, item, spider):
        if item['text']:
            self.baike_items.insert_one(
                    {
                        'baike_id': item['baike_id'],
                        'title': item['title'],
                        'name': item['name'],
                        'text': item['text'],
                        'page_url': item['page_url'],
                    })
            print(item['title'])
        return item

    def close_spider(self, spider):
        self.client.close()