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
    def __init__(self, user_id=None) -> None:
        # 当针对单个用户时，设定目标
        self.user_id = user_id
        self.user_name = None

        self.x = []  # x 轴坐标
        self.y = []  # y 轴坐标
        self.users_name = []
        # self.song_name = []
        self.users_id = []
        self.song_id = None
        self.songs_id = []
        self.songs_name = []
        self.matrix = []

        self.rdb = rdb.ReadColle()
        self.wdb = wdb.WriteColle()
        # self.sup = supd.SUPandas()
        # 设置projection ,知识不需要_id(ObjectId)
        if self.user_id == None:
            self.query = {}
        else:
            self.query = {
                'id': self.user_id
            }
        self.projections = {
            "_id": 0,
            "id": 1,
            "name": 1,
            "RecomUsers": 1
            # "songs.name": 1
        }
        pass

    # app调用这个方法来启动数据计算
    # limit 为 ALL 的时候，采用 user-song的相似度来对用户群进行一个较大的一次性推荐
    # 当limit 不为 ALL 的时候，采用处理tag 后 获取的相关性最高的一批用户构建一个 user-song 形成一个推荐表，来推荐歌曲
    # 主要是获取用户对象是哪些用户
    def makeRecomSongAnswer(self, limit="ALL"):
        print("[" + t.asctime(t.localtime()) + "]" +
              "Start" + "make recommend song answer")
        if limit == "ALL":
            self.saveUserSongRecomAnswer(self.makeRecomAnswerLoop(limit=-1))
        else:  # 只获取目标用户的推荐结果，并从数据库中调用
            self.saveUserSongRecomAnswer(self.makeRecomAnswerSong())
        print("successfully done")

    def makeRecomAnswerSong(self):
        # 获取recom中之前设置的数据
        doc = self.rdb.findDocument(
            collection_name="recom", query=self.query, projection=self.projections)
        # 储存请求用户的名字
        self.user_name = doc[0]['name']
        # 跟据数据库给的RecUsers来处理数据
        list_users_id = []
        list_users_id.append(self.user_id)
        # print(self.user_id, list_users_id)
        # users_id 合集，之后会通过这个来形成x轴坐标
        list_users_id.extend(doc[0]['RecomUsers'])
        # 构成xy轴的内容源头
        docs = self.getSongsWithUserIdFromMongo(array=list_users_id)
        list_id = self.getItemFromDocs(docs=docs, key='id')
        list_name = self.getItemFromDocs(docs=docs, key='name')
        # matrix_data = data
        # pandas_x = self.x
        # pandas_y = self.y
        data = self.makeXYMatric(docs=docs)
        sudf = supd.SUPandas(datas=data, items=self.y, users=self.x)
        # 歌曲推荐的结果
        dict_user_song = self.makeRecomDcition(df_object=sudf, sign=-1)
        return dict_user_song

    # 根据用户id 获取数据
    def getSongsWithUserIdFromMongo(self, array) -> list:
        query = {'id': {"$in": array}}
        projection = {'_id': 0, 'id': 1, 'name': 1,
                      'songs.id': 1, 'songs.name': 1}
        docs = self.rdb.findDocument(
            collection_name="like", query=query, projection=projection, limit=-1)
        return docs

    # 根据docs 生成xy轴 ，矩阵
    def makeXYMatric(self, docs) -> list:
        # 存储(用户-歌曲)元素的坐标
        matric_data = []  # 矩阵中值
        matric_y = []  # 矩阵 y 值
        matric_x = []  # 矩阵 x 值
        for item in docs:
            self.x.append(item['name'])
            self.users_id.append(item['id'])
            # index_item = docs.index(item)
            # print(index_item)
            # print(self.users_name, self.users_id)
            # 循环每个item内的songs形成行标
            list_tmp_songs_id = []
            list_tmp_songs_name = []
            col_tmp = []
            # 当前这一组歌曲所在的x坐标值
            index_item = docs.index(item)
            for song in item['songs']:
                # 处理songs 中的 id 和 name
                list_tmp_songs_id.append(song['id'])
                list_tmp_songs_name.append(song['name'])
                col_tmp.append(int(index_item))
            # 构建y轴坐标
            self.y.extend(list_tmp_songs_id)  # （没有去重）
            self.y = list(set(self.y))  # 每次添加新的list_tmp后都进行一次去重，到最后就是y轴坐标
            self.songs_name += list_tmp_songs_name
            matric_x += col_tmp
            matric_data += list_tmp_songs_id
        # 循环结束将数据替换到self.users_name中，便于之后使用
        self.users_name = self.x
        # 扫描以上的matric_y 和 self.y(去重后),最后生成y值
        matric_y = self.scanItemAsMatricY(matric_y=matric_data)
        # 生成相应的矩阵数据集
        # print(matric_x)
        # print(matric_y)
        # print(len(matric_data))
        data = self.makeMatric(x=matric_x, y=matric_y,
                               matric_data=matric_data)
        return list(map(list, data.toarray()))

    # 提取docs中的内容
    def getItemFromDocs(self, docs, key) -> list:
        list_tmp = []
        for item in docs:
            list_tmp.append(item[key])
        return list_tmp

    # 扫描数据构成y轴坐标值
    def scanItemAsMatricY(self, matric_y, matric_rate_data=None) -> list:
        list_tmp_y = []
        for item in matric_y:
            list_tmp_y.append(self.y.index(item))
            # 配置其中每个数据
            matric_y[matric_y.index(item)] = 1
        return list_tmp_y

    # 生成矩阵
    def makeMatric(self, x, y, matric_data):
        col_x = np.array(x)
        row_y = np.array(y)
        data = np.array(matric_data)
        return coo_matrix((data, (row_y, col_x)))

    # 利用pandas和jaccard系数生成相似度
    # def makeRecomDcition(self, df_object: supd.SUPandas):
    #     return
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
                self.users_name.append(item['name'])
                self.users_id.append(item['id'])
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
                self.songs_id.extend(list_tmp)
                # 按顺序存储数据到list中
                matrix_id += list_tmp
                user_col += col_tmp
                # 去重
                self.songs_id = list(set(self.songs_id))
            # 当每个用户都已经扫描过后
            # 开始通过matrix_id 和 self.song_id确认 song_row
            # 设置单独的方法
            song_row = self.scanSongId(
                song_id=self.song_id, matrix_id=matrix_id)
        # song_row 第 y 行
        # user_col 第 x 列
        # matrix_id 对应的 数据
        data = self.makeMatric(
            x=song_row, y=user_col, matric_data=matrix_id)
        data = list(map(list, data.toarray()))
        # data = list(data.toarray())
        # data,二维数据表
        # 横轴坐标  self.user_name
        # 纵轴坐标  self.song_id
        # 一次生成我们的pandas 表格
        # 调用方法 makeRecomAnswer 生成相似推荐的结果字典
        dict_recom = self.makeRecomDcition(df_object=supd.SUPandas(
            datas=data, songs=self.user_name, users=self.song_id))
        return dict_recom

    # song_num=50 默认推荐50 首
    # -1 时 获取特定用户
    # 获取都有用户
    def makeRecomDcition(self, df_object: supd.SUPandas, song_num=50, sign=1):
        # 判断是只取出一个用户还是取出多个用户
        # sign == -1 的时候使用 取出一个用户的信息
        # 统一构成推荐列表
        diction = df_object.makeTopNUsers(
            similar=df_object.makeSimilarityBetweenUser(),
            sign=1)
        diction = df_object.makeRecomUserBySong(
            topN=diction, song_num=song_num)
        # print(diction)
        if sign == -1:
            # 计算所有的推荐的结果，但是返回的只有一个人
            dict_result = {self.user_name: diction[self.user_name]}
            # diction = df_object.makeTopNUsers(
            #     similar=df_object.makeSimilarityBetweenUser())
            # diction[self.user_name] = self.makeListIdWithSongId(
            #     diction[self.user_name])
            return dict_result
        else:
            # 直接将所有的信息返回
            return diction

    def scanSongId(self, song_id, matrix_id):
        # 存储对应位置的数据
        list_tmp_row = []
        for id in matrix_id:
            # print(song_id.index(id))
            list_tmp_row.append(song_id.index(id))
            matrix_id[matrix_id.index(id)] = 1
        return list_tmp_row

    # 返回的结果是一个diction，所以需要重组，生成保存所需要的list
    # 同时需要有 id,name,RecomSong
    # 通过id进行数据存在判断，

    def changeDataFormat(self, diction: dict, list_keys: list):
        docs = []
        for key in list_keys:
            diction_tmp = {
                "id": self.users_id[self.users_name.index(key)],
                "name": key,
                "RecomSong": diction[key]
            }
            docs.append(diction_tmp)
        return docs

    # 保存操作
    def saveUserSongRecomAnswer(self, diction: dict):
        docs = self.changeDataFormat(diction=diction, list_keys=list(diction))
        self.wdb.writeDocument(
            docs=docs, collection_name="recom")
        return docs  # 用户输出方法体中变量

    # def makeMatrixSongUser(self, row, col, id):
    #     row_y = np.array(row)
    #     col_x = np.array(col)
    #     data = np.array(id)
    #     # 第 y 行 第 x 列
    #     return coo_matrix((data, (row_y, col_x)))
