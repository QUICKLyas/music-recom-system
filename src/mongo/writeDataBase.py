import pojo.Mongo as connect


class WriteColle (object):
    def __init__(self) -> None:
        self.con = connect.Conn()
        self.condb = self.con.getDB()
        # 数据中存在的文档名
        self.collist = self.condb.list_collection_names()
        pass

    # 创建collection
    def createCollection(self, collection_name):
        # 判断是否存在collection，若不存在创建，若存在需要连接
        if self.isCollectionExist(collection_name):
            # print(collection_name + " exists!")
            pass
        cols = self.condb[collection_name]
        cols.insert_one({"name": "playlist"})
        cols.delete_one({"name": "playlist"})
        return

    # 插入数据
    def writeDocument(self, docs: list, collection_name):
        # 确保该collection是存在的
        self.createCollection(collection_name)
        cols = self.condb[collection_name]
        # 将每段数据存储到数据库中
        # print(cols.estimated_document_count())
        n = 0
        # 循环该list
        for i in docs:
            # 判断是否存在该数据，不存在，将数据插入 存在就更新数据
            if self.isDocExtists(i, collection_name) != True:
                cols.insert_one(i)
            else:
                # update_one 需要生成两个重要的字典控制更新
                cols.update_one()

    # 判断该字段该段是否存在与数据库中，通过id判断是否存在
    # 判断数据在指定的collection是否已经存在，
    # 存在了返回true，
    # 不存在返回false
    def isDocExtists(self, doc, collection_name):
        self.col = self.condb[collection_name]
        length = len(list(self.col.find({'id': doc['id']})))
        if length != 0:
            return True
        else:
            return False
    # 判断collection 是否存在

    def isCollectionExist(self, collection_name="test"):
        if collection_name in self.collist:
            return True
        else:
            return False
