import mongo.ReadDataBase as rdb
import mongo.WriteDataBase as wdb
import numpy as np
import time as t
import random
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
        self.users_id = []
        self.songs_name = []

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
        self.a_projections = {
            "_id": 0,
            "id": "$id",
            "name": "$name",
            "songs": "$songs",
        }
        pass

    def setUserId(self, user_id):
        self.user_id = user_id

    # app调用这个方法来启动数据计算
    # limit 为 ALL 的时候，采用 user-song的相似度来对用户群进行一个较大的一次性推荐
    # 当limit 不为 ALL 的时候，采用处理tag 后 获取的相关性最高的一批用户构建一个 user-song 形成一个推荐表，来推荐歌曲
    # 主要是获取用户对象是哪些用户
    def makeRecomSongAnswer(self, limit="ALL"):
        print("[" + t.asctime(t.localtime()) + "]" +
              "Start" + "make recommend song answer ( limit", limit, ")")
        if limit == "ALL":
            self.makeRecomAnswerLoop(limit=-1)
        else:  # 只获取目标用户的推荐结果，并从数据库中调用
            self.saveUserSongRecomAnswer(self.makeRecomAnswerSong())
        print("successfully done")

    # 所有用户一次性土建，确保性能，只获取前50
    # 获取数据库中的信息，包括 用户 name，
    # 用户下的tags songs {name 和 id}
    # 处理collection = like
    # page 失去的页数总计
    # limit 是取的每页大小
    def makeRecomAnswerLoop(self, limit=50):
        n = 0
        while True:
            # 基础获取方法，不随机，按顺序定量拿数据
            projections = {"_id": 0, "id": 1, "name": 1, "songs": 1}
            docs = self.rdb.findDocument(
                collection_name="like",
                projection=projections,
                limit=limit, page=n)
            # 判断是否为空数据
            if len(docs) <= 0:
                break
            # 判断获取的数据数量是否足够，不够采用随机获取方法获取数据
            if len(docs) <= 10:
                # 重新获取docs
                querys = [{'$sample': {"size": limit}}]
                project = {'$project': self.a_projections}
                querys.append(project)
                docs = self.rdb.aggregateDocument(
                    collection_name="like", querys=querys)
            # 翻页
            n += 1
            dict_user_song = self.makeSongFromMongoOneofLoop(docs=docs)
            self.saveUserSongRecomAnswer(dict_user_song)
        return

    # makeRecomAnswerLoop(self, limit=50)当中单独的一个循环体中数据处理的部分
    def makeSongFromMongoOneofLoop(self, docs):
        # 通过docs 生成一组
        # matrix_data = data
        # pandas_x = self.x
        # pandas_y = self.y
        data = self.makeXYMatric(docs=docs)
        # print(data)
        sudf = supd.SUPandas(datas=list(
            map(list, data.toarray())), items=self.y, users=self.x)
        # 歌曲推荐的结果
        # sign 值默认时表示获取所有的用户
        dict_user_song = self.makeRecomDcition(df_object=sudf)
        # print(dict_user_song)
        return dict_user_song

    # 只获取一个用户的推荐歌曲信息
    def makeRecomAnswerSong(self):
        # 获取recom中之前设置的数据
        projections = {"_id": 0, "id": 1, "name": 1, "RecomUsers": 1}
        doc = self.rdb.findDocument(
            collection_name="recom", query=self.query, projection=projections)
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
        # matrix_data = data
        # pandas_x = self.x
        # pandas_y = self.y
        data = self.makeXYMatric(docs=docs)
        sudf = supd.SUPandas(datas=list(
            map(list, data.toarray())), items=self.y, users=self.x)
        # 歌曲推荐的结果，应该再一次保存用户列
        # 计划再处理数据的同时保存相似用户结果
        dict_user_song = self.makeRecomDcition(df_object=sudf, sign=-1)
        return dict_user_song

    # 根据用户id 获取数据
    def getSongsWithUserIdFromMongo(self, array) -> list:
        query = {'id': {"$in": array}}
        projection = {'_id': 0, 'id': 1, 'name': 1,
                      'songs.id': 1, 'songs.name': 1}
        docs = self.rdb.findDocument(
            collection_name="like", query=query, projection=projection, limit=-1)
        # print(docs)
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
        return data

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

    # song_num=50 默认推荐50 首
    # -1 时 获取特定用户
    # 获取都有用户
    def makeRecomDcition(self, df_object: supd.SUPandas, song_num=50, sign=1):
        # 判断是只取出一个用户还是取出多个用户
        # sign == -1 的时候使用 取出一个用户的信息
        # 统一构成推荐列表
        # 另存此处的topN_user
        diction = df_object.makeTopNUsers(
            similar=df_object.makeSimilarityBetweenUser(),
            sign=1)
        # print()
        list_from_dict = self.makeListIdWithUserName(
            list_name=diction[self.user_name])
        diction_song = df_object.makeRecomUserBySong(
            topN=diction, song_num=5)
        # print(diction)
        if sign == -1:
            # 计算所有的推荐的结果，但是返回的只有一个人
            dict_result = {self.user_name: [
                list_from_dict, diction_song[self.user_name]]}
            return dict_result
        else:
            # 直接将所有的信息返回
            return diction

    def scanSongId(self, song_id, matrix_id):
        # 存储对应位置的数据
        list_tmp_row = []
        for id in matrix_id:
            list_tmp_row.append(song_id.index(id))
            matrix_id[matrix_id.index(id)] = 1
        return list_tmp_row

    # 返回的结果是一个diction，所以需要重组，生成保存所需要的list
    # 同时需要有 id,name,RecomSong,
    # 同时应该考虑更新最新的推荐用户数列，
    # 以便于后面的再次使用
    # 通过id进行数据存在判断，
    def changeDataFormat(self, diction: dict, list_keys: list):
        docs = []
        for key in list_keys:
            diction_tmp = {
                "id": self.users_id[self.users_name.index(key)],
                "name": key,
                "RecomUsers": diction[key][0],
                "RecomSong": diction[key][1]
            }
            # print(diction_tmp)
            docs.append(diction_tmp)
        return docs

    # 保存操作
    def saveUserSongRecomAnswer(self, diction: dict):
        docs = self.changeDataFormat(diction=diction, list_keys=list(diction))
        # print(docs)
        self.wdb.writeDocument(
            docs=docs, collection_name="recom")
        return docs  # 用户输出方法体中变量

    def makeListIdWithUserName(self, list_name: list) -> list:
        list_id = []
        for name in list_name:
            list_id.append(self.users_id[self.users_name.index(name)])
        return list_id


# 此类重新获取一边用户集，再一次对数据进行一次歌曲的相似度计算，从而获取歌曲的topN计算
# 本方法只限定在目标用户，不会 所有用户
# 此处算法，考虑用过推荐歌曲的相似歌曲，设定一次找寻最相似歌曲数量为5首，
# 算法基于用户和tag
# 首先基于tag 将歌曲进行一个获取，尽量获取tag重合度较高的歌曲，
# 然后根据mongo 的获取方法，获取拥有这几首歌的用户，进行相似度计算，最后推荐这些歌曲
# 受限于手边的数据集不能够组成比较完备 的数据集，所暂时不进行考虑，
# 但依然实现歌曲-歌曲相似度计算的程序，用来推荐相似歌曲，但是未考虑使用什么表格进行存储，所以暂时将数据存储到song-detial中，并以SimilaritySong 的array样式 的id进行存储
class UserSongRecomAfterSongSimilarity(object):
    def __init__(self, user_id=None) -> None:
        self.user_id = user_id
        if self.user_id == None:
            self.query = {}
        else:
            self.query = {
                'id': self.user_id
            }
        self.usr = UserSongRecom()
        self.usr.setUserId(user_id=user_id)
        # print(self.usr.user_id)
        self.rdb = rdb.ReadColle()
        self.wdb = wdb.WriteColle()
        pass

    # 启动程序
    def makeRecomBySongSimilarityAnswer(self, limit="ALL"):
        print("[" + t.asctime(t.localtime()) + "]" +
              "Start" + "make recommend song answer ( limit", limit, "song-song )")
        # self.saveUserSongRecomAnswer(self.makeRecomAnswerSong())
        if limit == "ALL":
            self.saveUserSongRecomAnswer(
                self.makeRecomAnswerSong(
                    sign=0), update_name="SimilaritySongs", collection="song")
        else:
            self.saveUserSongRecomAnswer(
                self.makeRecomAnswerSong(sign=1), update_name="RecomSong", collection="recom")

        print("successfully done")

    # 只获取一个用户的歌曲信息，从而生成其中所有歌曲的相似歌曲的结果
    def makeRecomAnswerSong(self, sign=0):
        # 获取recom中之前设置的数据
        projections = {"_id": 0, "id": 1, "name": 1, "RecomUsers": 1}
        doc = self.rdb.findDocument(
            collection_name="recom", query=self.query, projection=projections, limit=1)
        # 储存请求用户的名字
        self.usr.user_name = doc[0]['name']
        # 跟据数据库给的RecUsers来处理数据
        list_users_id = []
        list_users_id.append(self.user_id)
        # print(self.user_id, list_users_id)
        # users_id 合集，之后会通过这个来形成x轴坐标
        list_users_id.extend(doc[0]['RecomUsers'])
        # 构成xy轴的内容源头
        docs = self.usr.getSongsWithUserIdFromMongo(array=list_users_id)
        # matrix_data = data
        # pandas_x = self.x
        # pandas_y = self.y
        data = self.usr.makeXYMatric(docs=docs)
        sudf = supd.SUPandas(datas=list(
            map(list, data.toarray())), items=self.usr.y, users=self.usr.x)
        # 歌曲推荐的结果，应该再一次保存用户列
        # 计划再处理数据的同时保存相似用户结果
        # 当sign = 0  的时候 是表示求相似歌曲， sign 为 1 时 是生成用户的推荐结果
        dict_song = {}
        # 设置两种返回结果
        match sign:
            case 0:
                # 寻找相似歌曲
                dict_song = self.makeSimilaritySongDictionForSong(
                    df_object=sudf)
            case 1:
                # 寻找用户的推荐歌曲
                projections = {"_id": 0, "songs": 1}
                dict_song = self.makeRecomSongDictionForUser(
                    df_object=sudf, user_songs=self.rdb.findDocument(
                        collection_name="like", query=self.query, projection=projections)[0]['songs'])
        return dict_song

    def makeSimilaritySongDictionForSong(self, df_object: supd.SUPandas) -> dict:
        # 判断是只取出一个用户直接获取所有歌曲中最相似的歌曲
        # 统一构成推荐列表
        # 另存此处的topN_songs ，key是song标签，将这些数据存储到数据库中
        # [self.user_id]
        diction = df_object.makeTopNSongs(
            # 对用户收藏的歌曲，每首获取最相似的前5首
            # 将这个数据进行几个合并，
            # 然后将数据进行随机提取，
            # 提取其中的 前5个
            similar=df_object.makeSimilarityBetweenItem(),
            song_cnt=5)
        return diction

    def makeRecomSongDictionForUser(self, df_object: supd.SUPandas, user_songs: list) -> dict:
        # 歌曲相似后得到的数据
        diction = df_object.makeTopNSongs(
            # 对用户收藏的歌曲，每首获取最相似的前5首
            # 将这个数据进行几个合并，
            # 然后将数据进行随机提取，
            # 提取其中的 前5个
            similar=df_object.makeSimilarityBetweenItem(),
            song_cnt=5)
        list_songs = self.makeSongIdList(user_songs)
        # 通过list_songs 和 diction 获取需要的歌曲
        list_songs_result = self.makeSongsFromSimilarDict(
            diction=diction, songs=list_songs)
        # 构造数据字典，方便之后用于保存，需要有id和name和数据
        return {self.user_id: list_songs_result}

    def makeSongsFromSimilarDict(self, diction: dict, songs: list, song_num=30):
        list_ids = list(diction)
        list_tmp = []
        for item in list_ids:
            if item in songs:
                list_tmp.extend(diction[item])
        list_tmp = list(set(list_tmp))
        # 删除songs 中出现的id
        for item in songs:
            if item in list_tmp:
                list_tmp.pop(list_tmp.index(item))
            else:
                continue
        list_result = random.sample(list_tmp, song_num)
        return list_result

    def makeSongIdList(self, array: list):
        list_tmp = []
        for item in array:
            list_tmp.append(item['id'])
        return list_tmp

    def checkList(self, src_list: list, dest_list: list):
        for item in src_list:
            if item not in dest_list:
                print(True)

    def saveUserSongRecomAnswer(self, diction: dict, update_name, collection=""):
        docs = self.changeDataFormat(
            diction=diction, list_keys=list(diction), update_name=update_name)
        self.wdb.writeDocument(
            docs=docs, collection_name=collection)
        return docs  # 用户输出方法体中变量

    # 返回的结果是一个diction，所以需要重组，生成保存所需要的list
    # 同时需要有 id,name,RecomSong,
    # 同时应该考虑更新最新的推荐用户数列，
    # 以便于后面的再次使用
    # 通过id进行数据存在判断，
    def changeDataFormat(self, diction: dict, list_keys: list, update_name=""):
        docs = []
        for key in list_keys:
            diction_tmp = {
                "id": key,
                "name": self.usr.user_name,
                update_name: diction[key]
            }
            docs.append(diction_tmp)
        return docs
