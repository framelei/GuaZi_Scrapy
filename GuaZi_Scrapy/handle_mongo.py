import pymongo

class Handle_mongo_guazi(object):
    def __init__(self,collection_name):
        myclient = pymongo.MongoClient("mongodb://root:Mongo_Lei@129.28.200.147:27017")
        #创建数据库
        self.db = myclient['guazi_task']
        #创建数据库表
        self.collection = self.db[collection_name]

    #1、存储task_url
    # 使用update_one代替insert_one，以task_url为主键，避免重复插入
    def save_task(self,task):
        # {'task_url': 'https://www.guazi.com/zz/chery/o1i7/', 'city_name': '郑州', 'car_name': '奇瑞'}
        print('MongoDB正在存储：%s'%task)
        task = dict(task)
        # self.collection.insert_one(task)
        self.collection.update_one({'task_url':task['task_url']},{'$set':task},True)

    #2、提取task_url，取一条删一条，绝不重复
    def get_task(self):
        # TypeError: find_one_and_delete() missing 1 required positional argument: 'filter'
        task = self.collection.find_one_and_delete({})
        return task

    #3、向数据库写入爬取car数据
    def save_data(self,data):
        #
        # print('MongoDB正在存储：%s'%data)
        self.collection.update_one({'car_id':data['car_id']},{'$set':data},True)

# 直接在handle_mongo.py中完成类的实例化，将实例化对象给调用方使用
#1、用于存、取url
mongo_url = Handle_mongo_guazi(collection_name='guazi_url')
#2、用于向数据库写入爬取car的数据
mongo_data = Handle_mongo_guazi(collection_name='guazi_data')