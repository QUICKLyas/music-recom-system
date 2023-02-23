import mongo.ReadDataBase as rdb
import mongo.WriteDataBase as wdb
import panda.TagUser as tupd
import time as t
import numpy as np

from scipy.sparse import coo_matrix, csr_matrix
from collections import Counter


# 设计 对用户听歌的习惯进行一个计算，统计出用户的听歌偏好偏好
class TagofSongUserRecom():
    # 目的： 判断用户听歌倾向
    # 条件： 用户的tags，
    # 结果： 1. 用户的tags 的统计
    # 再创建这个class 的同时可以写找的对象的id 或者不写，默认找到的是最开是的对象
    def __init__(self, user_id=None) -> None:
        # 如果user_id 不为空那么只对这个用户进行tags分析
        # 存储个体用户信息
        self.user_id = user_id
        self.user_name = None
        # 用于更新的时候使用的查找条件
        self.id = None
        self.page = 0
        self.doc_length = -1
        self.x = []  # x 轴坐标
        self.y = []  # y 轴坐标
        self.matric_rate_data = None
        self.songs = []
        self.tags = []
        self.users_name = []
        self.users_id = []
        # mongo
        self.rdb = rdb.ReadColle()
        self.wdb = wdb.WriteColle()
        # panda
        # 设置fing的query 是 只找寻特定用户还是所有用户
        if self.user_id == None:
            self.query = {}
        else:
            self.query = {
                'id': self.user_id
            }
        # 设置projection ,不需要_id(ObjectId)，判断tag 不需要 song 的 id
        self.projections = {
            "_id": 0,
            "name": 1,
            "id": 1,
            "tags": 1,
            # "songs.id": 1,
            # "songs.name": 1
        }
        self.a_projections = {
            "_id": 0,
            "name": "$name",
            "id": "$id",
            "tags": "$tags"
            # "songs": "$songs"
        }
        pass

    # 生成我们需要内容：关于tag相似度获取的用户集
    # 外部使用当前的方法来调用整个过程包括保存到数据库中
    def makeRecomUsersSet(self, limit="ALL"):
        print("[" + t.asctime(t.localtime()) + "]" +
              "Start " + "make similarity users answer")
        self.saveDataSetRecomAnswer(
            self.makeRecomAnswerForUser(), id=self.user_id)

    # 首先应该获取用户的信息然后生成xy轴和矩阵
    def makeRecomAnswerForUser(self, limit=50) -> dict:
        # 获取单个用户信息
        doc = self.rdb.findDocument(
            collection_name="like", query=self.query, projection=self.projections)
        # 储存请求用户的名字
        self.user_name = doc[0]['name']
        # 随机获取一定数量的用户来计算tag 相似度
        # 统一获取其他用户的信息
        querys = [{'$sample': {"size": limit-1}}]
        project = {'$project': self.a_projections}
        querys.append(project)
        docs = self.rdb.aggregateDocument(
            collection_name="like", querys=querys)
        # print(doc)
        # print(len(docs))
        # 判断 docs中是否存在 doc 并合并
        docs = self.isDocinDocs(doc=doc, docs=docs)
        # 通过docs 生成一组 matric_rate_data数据
        # 查找数据songs 便于 统计tags 出现的次数
        # 提取docs 中用户的id
        list_name = self.getUserIdFromDocs(docs=docs, key='name')
        list_id = self.getUserIdFromDocs(docs=docs, key='id')
        docs_song = self.getSongsforTagfromMongo(list_id)
        # count_tag
        dict_tags = self.makeMatricTagCountData(docs=docs_song)
        # 根据以上docs 来生成 xy轴，矩阵
        data = self.makeXYMatric(docs=docs)
        # 内容
        # matrix_data = data
        # pandas_x = self.x
        # pandas_y = self.y
        # 生成pandas 表格
        tudf = tupd.TUPandas(datas=data, items=self.y, users=self.x)
        # 开始将tudf 中的数据根据上面的dict_tags中的数据进行替换
        tudf = self.changeDataCountTagTUDF(list_name, dict_tags, tudf)
        # print(tudf.df)
        return self.makeRecomDcition(df_object=tudf)

    # 生成最后的tag表 开始的函数方法，
    # 如果我们是app调用程序
    # 从此处启动相关程序
    # 统计一个用户自己tag的占比
    def makeTagRateAnswer(self):
        print("[" + t.asctime(t.localtime()) + "]" +
              "Start" + "make tag's rate answer")
        # while True:
        #     # 如果 doc 的长度为 0 设置推出循环
        #     if self.doc_length == 0:
        #         break
        #     # 如果 doc 的长度为 非 0 运行下面的程序 步骤
        #     diction = self.makeTagUserRateDataPandas()
        #     # save 操作
        #     self.saveDataSetRecomAnswer(diction)
        #     self.page += 1
        print("successfully done")
        return

    # 内部通过这里调用方法
    def makeTagUserRateDataPandas(self, user_id=None, user_tags=None) -> list:
        # 当前方法是开始方法
        if user_id == None:
            self.getTagFromMongo(self.user_id)
        else:
            self.getTagFromMongo(user_id)
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
        # 生成pandas
        taguser = tupd.TUPandas(datas=data, tags=tag_col,
                                users=["name", "count"])
        # print(taguser.df)
        # 形成关于用户的收藏的歌曲中的占比
        taguser.computeRateofTag()  # 具体计算方法在pandas中进行
        list_diction = taguser.df.to_dict(orient='records')
        # print("list_diction:", list_diction)
        return list_diction

    # 保存操作
    def saveDataSetRecomAnswer(self, diction: dict, id):
        docs = self.changeDataFormat(diction=diction, list_keys=list(diction))
        # print(docs)
        self.wdb.writeDocument(
            docs=docs, collection_name="recom")
        return docs

    # 判断 docs中是否存在 doc 返回doc 和 docs 合并后的list
    def isDocinDocs(self, doc, docs) -> list:
        for item in docs:
            # print(item['id'])
            if item['id'] == self.user_id:
                docs.remove(item)
                break
            else:
                continue
        doc.extend(docs)
        return doc

    # 提取docs 中用户的id
    def getUserIdFromDocs(self, docs, key) -> list:
        list_tmp = []
        for item in docs:
            list_tmp.append(item[key])
        return list_tmp

    # 获取用户和他们收藏的歌曲
    def getSongsforTagfromMongo(self, array) -> list:
        query = {'id': {"$in": array}}
        projection = {'_id': 0, 'name': 1, 'songs.id': 1, 'songs.union': 1}
        docs = self.rdb.findDocument(
            collection_name="like", query=query, projection=projection, limit=-1)
        return docs

    # 通过者个docs 生成一组 matric_rate_data数据
    def makeMatricTagCountData(self, docs):
        diction = {}
        for item in docs:
            # print(Counter(item['tags']))
            # print(item)
            list_tmp = []
            for song in item['songs']:
                # 该歌曲的tags
                list_tmp.extend(song['union'][0]['tags'])
                # print(Counter(list_tmp))
                # break
            arr = Counter(list_tmp)
            diction[item['name']] = arr
        return diction

    # 根据以上docs 来生成 xy轴，矩阵
    def makeXYMatric(self, docs) -> list[list]:
        # 存储(用户-标签)元素的坐标
        matric_data = []  # 矩阵中值
        matric_y = []  # 矩阵 y 值
        matric_x = []  # 矩阵 x 值
        for item in docs:
            self.x.append(item['name'])
            self.users_id.append(item['id'])
            # 第index_item列,表示当前操作的item在docs中的位置
            index_item = docs.index(item)
            # print(index_item)
            # print(self.users_name, self.users_id)
            # 循环每个item内的tags形成行标
            list_tmp = []  # 所有用户拥有的tags（没有去重的情况下）
            col_tmp = []  # 暂存当前用户所在位置，用于之后形成的matric 时作为x值
            for tag in item['tags']:
                list_tmp.append(tag)
                col_tmp.append(int(index_item))
            # 纵轴坐标 y
            self.y.extend(list_tmp)  # （没有去重）
            self.y = list(set(self.y))  # 每次添加新的list_tmp后都进行一次去重，到最后就是y轴坐标
            matric_data += list_tmp  # 将存储的标签转换出每个tag 的 y 值
            matric_x += col_tmp
        # 扫描以上的matric_y 和 self.y(去重后),最后生成y值
        matric_y = self.scanItemAsMatricY(matric_y=matric_data)
        # 生成相应的矩阵数据集
        data = self.makeMatric(x=matric_x, y=matric_y,
                               matric_data=matric_data)
        data = list(map(list, data.toarray()))
        return data

    # 利用pandas和pearson形成相关性最高的几个用数据，默认推荐5个人，如果有推荐阈值
    def makeRecomDcition(self, df_object: tupd.TUPandas):
        # 变量
        diction = df_object.makeTopNUsers(similar=df_object.makeSimilarityWithPearson(),
                                          sign=1)
        # 利用当前用户的信息确定他们的id值形成对应的list_id
        diction[self.user_name] = self.makeListIdWithUserName(
            diction[self.user_name])
        return diction

    # 利用当前用户的信息确定他们的id值形成对应的list_id
    def makeListIdWithUserName(self, list_name: list) -> list:
        list_id = []
        for name in list_name:
            list_id.append(self.users_id[self.x.index(name)])
        return list_id

    # 替换pandas中的数值为次数
    def changeDataCountTagTUDF(self, list_x: list, docs: dict, df_object: tupd.TUPandas) -> tupd.TUPandas:
        for item in list_x:
            # 生成y轴坐标
            list_tmp_tag = list(docs[item].keys())
            # print(docs[item])
            for tag in list_tmp_tag:
                # TUPandas内的pandas先行后列
                df_object.df.loc[tag, item] = docs[item][tag]
        df_result = df_object
        return df_result

    def scanItemAsMatricY(self, matric_y, matric_rate_data=None):
        # 存储matric_y 中每个元素对应的y坐标值
        list_tmp_y = []
        for item in matric_y:
            list_tmp_y.append(self.y.index(item))
            # 配置其中每个数据
            matric_y[matric_y.index(item)] = 1
        if matric_rate_data == None:
            pass
        else:
            pass
        return list_tmp_y

    def makeMatric(self, x, y, matric_data):
        col_x = np.array(x)
        row_y = np.array(y)
        data = np.array(matric_data)
        return coo_matrix((data, (row_y, col_x)))

    # 设定保存的格式，在本类中，每次调用都是单个用户的调用，
    def changeDataFormat(self, diction: dict, list_keys: list) -> list:
        docs = []
        for key in list_keys:
            diction_tmp = {
                "id": self.user_id,
                "name": key,
                "RecUsers": diction[key]
            }
            docs.append(diction_tmp)
        return docs
