from pymongo import MongoClient

import utils.MongoUser as cu


class Conn (object):
    def __init__(self) -> None:
        # 创建数据库连接
        self.client = MongoClient(
            "mongodb://"
            + cu.user['mongoDB']['username'] + ":"
            + cu.user['mongoDB']['password'] + "@"
            + cu.user['IP'] + ":"
            + cu.user['port'] + "/"
            + cu.user['database']
            + "?authMechanism=DEFAULT&tls=false&authSource=nobody"
        )  # Host以及port
        # 选择数据库
        self.db = self.client['nobody']

    def getClient(self):
        return self.client

    def getDB(self):
        return self.db
