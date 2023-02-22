import mongo.ReadDataBase as rdb
import mongo.WriteDataBase as wdb
import numpy as np
import time as t
import scipy.sparse
# 生成二维矩阵的方法
from scipy.sparse import coo_matrix, csr_matrix
import panda.SongUser as supd
# import pandas as pd

# ps 此段程序是对整体用户集进行一次统一的推荐
# 生成推荐歌曲，默认是song_num=50推荐歌曲数量


class UserSongRecom (object):
    def __init__(self) -> None:
        self.user_name = []
        # self.song_name = []
        self.user_id = []
        self.song_id = []
        self.matrix = []

        self.rdb = rdb.ReadColle()
        self.wdb = wdb.WriteColle()
        # self.sup = supd.SUPandas()
        # 设置projection ,知识不需要_id(ObjectId)
        self.projections = {
            "_id": 0,
            "name": 1,
            "id": 1,
            "songs.id": 1,
            # "songs.name": 1
        }
        pass

    # app调用这个方法来启动数据计算
    def makeRecomSongAnswer(self, limit="ALL"):
        print("[" + t.asctime(t.localtime()) + "]" +
              "Start" + "make recommend song answer")
        if limit == "ALL":
            self.saveUserSongRecomAnswer(self.makeRecomAnswerLoop(limit=-1))
        else:
            self.saveUserSongRecomAnswer(self.makeRecomAnswerLoop())
    # 保存操作

    def saveUserSongRecomAnswer(self, diction: dict):
        docs = self.changeDataFormat(diction=diction, list_keys=list(diction))
        self.wdb.writeDocument(
            docs=docs, collection_name="recom",
        )
        print("successfully done")
        return

    # 获取数据库中的信息，包括 用户 name，
    # 用户下的tags songs {name 和 id}
    # 处理collection = like
    # page 失去的页数总计
    # limit 是取的每页大小
    def makeRecomAnswerLoop(self, limit=50, page=0):
        matrix_id = []
        user_col = []
        song_row = []

        n = 0
        while True:
            if n > page:
                break
            docs = self.rdb.findDocument(
                collection_name="like",
                projection=self.projections,
                limit=limit, page=n)
            # 判断是否为空数据
            if len(docs) <= 0:
                break
            # 翻页
            n += 1
            # print(len(docs[0]['songs']), len(docs[1]['songs']))
            # print(list(docs['0']))
            for item in docs:
                # 横轴坐标 x
                # 对应添加id 之后生成的数据存储的时候用上
                self.user_name.append(item['name'])
                self.user_id.append(item['id'])
                # 第 index_col 列
                index_col = docs.index(item)
                # 用于暂存当前用户的song 的id
                list_tmp = []
                # 暂存当前用户index
                col_tmp = []
                for song in item['songs']:
                    # 0: 0-202 1:203-818 819-1028
                    # self.song_name.append(song['name'])
                    list_tmp.append(song['id'])
                    # 第index_col 列
                    col_tmp.append(int(index_col))
                # 纵轴坐标 y
                self.song_id.extend(list_tmp)
                # 按顺序存储数据到list中
                matrix_id += list_tmp
                user_col += col_tmp
                # 去重
                self.song_id = list(set(self.song_id))
            # 当每个用户都已经扫描过后
            # 开始通过matrix_id 和 self.song_id确认 song_row
            # 设置单独的犯法
            song_row = self.scanSongId(
                song_id=self.song_id, matrix_id=matrix_id)
        # song_row 第 y 行
        # user_col 第 x 列
        # matrix_id 对应的 数据
        data = self.makeMatrixSongUser(
            row=song_row, col=user_col, id=matrix_id)
        data = list(map(list, data.toarray()))
        # data = list(data.toarray())
        # data,二维数据表
        # 横轴坐标  self.user_name
        # 纵轴坐标  self.song_id
        # 一次生成我们的pandas 表格
        # 调用方法 makeRecomAnswer 生成相似推荐的结果字典
        dict_recom = self.makeRecomDcition(df=supd.SUPandas(
            datas=data, songs=self.user_name, users=self.song_id))
        return dict_recom

    # song_num=50 默认推荐50 首
    def makeRecomDcition(self, df: supd.SUPandas, song_num=50):
        diction = df.makeRecomUserSong(
            topN=df.makeTopNUsers(
                similar=df.makeSimilarityBetweenUserSong()),
            song_num=song_num)
        return diction

    def scanSongId(self, song_id, matrix_id):
        # 存储对应位置的数据
        list_tmp_row = []
        for id in matrix_id:
            # print(song_id.index(id))
            list_tmp_row.append(song_id.index(id))
            matrix_id[matrix_id.index(id)] = 1
        return list_tmp_row

    def makeMatrixSongUser(self, row, col, id):
        row_y = np.array(row)
        col_x = np.array(col)
        data = np.array(id)
        return coo_matrix((data, (row_y, col_x)))

    # 返回的结果是一个diction，所以需要重组，生成保存所需要的list
    # 同时需要有 id,name,RecomSong
    # 通过id进行数据存在判断，

    def changeDataFormat(self, diction: dict, list_keys: list):
        docs = []
        for key in list_keys:
            diction_tmp = {
                "id": self.user_id[self.user_name.index(key)],
                "name": key,
                "RecomSong": diction[key]
            }
            docs.append(diction_tmp)
        return docs
