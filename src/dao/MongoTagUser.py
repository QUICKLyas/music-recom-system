import mongo.ReadDataBase as rdb
import mongo.WriteDataBase as wdb
import panda.TagUser as tu
import time as t


# 设计 对用户听歌的习惯进行一个计算，统计出用户的听歌偏好偏好
class TagofSongUserRecom():
    # 目的： 判断用户听歌倾向
    # 条件： 用户的tags，用户喜欢的歌曲信息
    # 结果： 1. 用户的tags 的统计
    # 再创建这个class 的同时可以写找的对象的id 或者不写，默认找到的是最开是的对象
    def __init__(self, user_id=None) -> None:
        # 如果user_id 不为空那么只对这个用户进行tags分析
        self.user_id = user_id
        # 用于更新的时候使用的查找条件
        self.id = None
        self.page = 0
        self.doc_length = -1
        self.tags = {}
        self.songs = []
        self.user_name = []
        # mongo
        self.rdb = rdb.ReadColle()
        self.wdb = wdb.WriteColle()
        # panda
        # 设置query
        if self.user_id == None:
            self.query = {}
        else:
            self.query = {
                'id': self.user_id
            }
        # 设置projection ,知识不需要_id(ObjectId)
        self.projections = {
            "_id": 0
        }
        pass

    # 生成最后的tag表 开始的函数方法，
    # 如果我们是app调用程序
    # 从此处启动相关程序
    def makeTagRateAnswer(self):
        print("[" + t.asctime(t.localtime()) + "]" +
              "Start" + "make tag's rate answer")
        while True:
            # 如果 doc 的长度为 0 设置推出循环
            if self.doc_length == 0:
                break
            # 如果 doc 的长度为 非 0 运行下面的程序 步骤
            diction = self.makeTagUserRateDataPandas()
            # save 操作
            self.wdb.updateDocumentSimple(
                query={
                    'id': self.id
                }, projection={
                    '$set': {"tags_rate": diction}
                }, collection_name="recom")
            self.page += 1
        print("successfully done")
        return

    def makeTagUserRateDataPandas(self) -> list:
        # 当前方法是开始方法
        self.getTagFromMongo(self.user_id)
        # print(self.tags)
        for item in self.songs:
            # 记录tags 出现的次数
            tags = item['union'][0]['tags']
            for tag in tags:
                self.tags[tag] += 1
        # 统计最后的数据
        return self.makeTagCountPandas(self.tags)

    # 获得需要的数据重点
    # 本class内部调用这个方法
    def getTagFromMongo(self, user_id, limit=1, n=0) -> None:
        self.query["user_id"] = user_id
        # 获取 数据 重点
        doc = self.rdb.findDocument(
            collection_name="like",
            query=self.query,
            projection=self.projections,
            limit=1, page=self.page)
        if len(doc) < 1:
            self.doc_length = 0
            return
        doc = doc[0]
        list_tags = doc['tags']
        # 设置判断数据 非重点 方便处理数据
        for item in list_tags:
            self.tags[item] = 0
        self.user_name = doc['name']
        self.id = doc['id']
        self.songs = doc['songs']
        return

    # 统计 tag 的 关系
    def makeTagCountPandas(self, diction: dict) -> list:
        # print(len(self.songs))
        tag_col = list(diction)
        data = list(diction.values())
        for i in data:
            data[data.index(i)] = [tag_col[data.index(i)], i]
        # print(data)
        taguser = tu.TUPandas(datas=data, tags=tag_col,
                              users=["name", "count"])
        # print(taguser.df)
        taguser.computeRateofTag()
        list_diction = taguser.df.to_dict(orient='records')
        # print("list_diction:", list_diction)
        return list_diction
