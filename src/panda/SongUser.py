import pandas as pd
import numpy as np
from sklearn.metrics import jaccard_score
from sklearn.metrics.pairwise import pairwise_distances


class SUPandas():
    def __init__(self, datas, items, users) -> None:
        self.data = datas
        self.items = items
        self.users = users
        self.df = pd.DataFrame(
            self.data, columns=self.users, index=self.items)
        pass

    # 获得杰卡德系数
    def getJaccardScore(self, df, user_name, other_name):
        return jaccard_score(df[user_name], df[user_name])

    # make 用户之间的两两相似度
    def makeSimilarityBetweenUser(self):
        user_similar_item = 1 - \
            pairwise_distances(self.df.T.values, metric="jaccard")
        user_similar = pd.DataFrame(
            user_similar_item, columns=self.users, index=self.users)
        return user_similar

    # make 歌曲之间的两两相似度
    def makeSimilarityBetweenItem(self):
        item_similar_user = 1 - \
            pairwise_distances(self.df.values, metric="jaccard")
        item_similar = pd.DataFrame(
            item_similar_user, columns=self.items, index=self.items)
        return item_similar

    # 生成topN_user 找到相似的用户
    # 0 默认获取前5个人
    # 1 根据相似度的平均值获取高于平均值的用户
    def makeTopNUsers(self, similar: pd.DataFrame, sign=0) -> dict:
        topN_users = {}
        for i in similar.index:
            df_topN = similar.loc[i].drop([i])
            df_topN_sorted = df_topN.sort_values(ascending=False)

            topN = []
            match sign:
                case 0:  # 获取最相似的5个用户
                    topN = list(df_topN_sorted.index[:5])
                    topN_users[i] = topN
                case 1:  # 1 获取几个
                    average = df_topN_sorted[:].mean()
                    topN_users[i] = self.getUserWithJaccard(
                        df_topN_sorted, threshold=average)
        return topN_users

    # 生成topN_song 找到相似的歌曲
    # 0 默认获取前50
    # 1 根据相似度的平均值获取高于平均值的用户
    def makeTopNSongs(self, similar: pd.DataFrame, song_cnt=50, sign=0) -> dict:
        topN_users = {}
        for i in similar.index:
            df_topN = similar.loc[i].drop([i])
            df_topN_sorted = df_topN.sort_values(ascending=False)
            # print(df_topN_sorted[100:])
            # break
            topN = list(df_topN_sorted.index[:song_cnt])
            topN_users[i] = topN
        return topN_users

    # 通过这些用户获取相似的歌曲，并排除某个用户的已经有的歌曲
    def makeRecomUserBySong(self, topN: dict, song_num: int):
        results = {}
        for user, simimlar_users in topN.items():
            result = set()
            for similar_user in simimlar_users:
                # print(similar_user)
                # rs_result.union(set(df.loc[sim_user].replace(0,np.nan).dropna().index))
                result = result.union(
                    set(self.df.loc[:, similar_user].replace(0, np.nan).dropna().index))
            result -= set(self.df.loc[:, user].replace(0,
                          np.nan).dropna().index)
            results[user] = list(result)[:song_num]
        return results

    # 调取大于阈值的数据
    def getUserWithJaccard(self, df_top, threshold=0.95) -> list:
        topJaccard_average = list(df_top[(df_top[:] > threshold)].index)
        return topJaccard_average
