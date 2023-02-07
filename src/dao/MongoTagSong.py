import pojo.Mongo as mongoConnect


class MongoTagSong(object):
    def __init__(self) -> None:
        self.con = mongoConnect.Conn()
        self.condb = self.con.getDB()
        self.conlist = self.condb.list_collection_names()
        pass

    # 获取tags
    def getTagCollections(self, collection_name,
                          query={}, projection={},
                          ):
        cols = self.condb[collection_name]
        docs = cols.find(query, projection)
        return list(docs)
