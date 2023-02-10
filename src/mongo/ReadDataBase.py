import pojo.Mongo as connect


class ReadColle (object):
    def __init__(self) -> None:
        self.con = connect.Conn()
        self.condb = self.con.getDB()
        # 数据中存在的文档名
        self.collist = self.condb.list_collection_names()
        pass

    # 查找数据，设定一些限制
    def findDocument(self, collection_name, query={}, projection={}, limit=1, page=0):
        # print(limit, page)
        cols = self.condb[collection_name]
        if limit == -1:
            docs = cols.find(query, projection)
        else:
            docs = cols.find(query, projection).limit(limit).skip(page*limit)
        return list(docs)

    # 随机查找数据，设定一些限制
    # collection_names 是一个列表，可以为一个也可以多个，但是第0个必须是主表
    def aggregateDocument(self, collection_name, querys=[]):
        cols = self.condb[collection_name]
        docs = cols.aggregate(querys)
        return list(docs)
