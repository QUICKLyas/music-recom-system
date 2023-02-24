import pandas as pd
import numpy as np
from sklearn.metrics import jaccard_score
from sklearn.metrics.pairwise import pairwise_distances


class TUPandas (object):
    def __init__(self, datas, items, users) -> None:
        self.data = datas
        self.items = items
        self.users = users
        self.df = pd.DataFrame(
            self.data, columns=self.users, index=self.items)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        pass

    # 根据用户的tag来计算similarity
    # 获得杰卡德系数
    def getJaccardScore(self, df, user_name):
        return jaccard_score(df[user_name])

    # make 用户之间的相似度
    def makeSimilarityBetweenUser(self):
        user_similar_tag = 1 - \
            pairwise_distances(self.df.values, metric="jaccard")
        user_similar = pd.DataFrame(
            user_similar_tag, columns=self.users, index=self.users)
        return user_similar

    # make tag 之间的两两相似度
    def makeSimilarityBetweenItem(self):
        item_similar_user = 1 - \
            pairwise_distances(self.df.T.values, metric="jaccard")
        item_similar = pd.DataFrame(
            item_similar_user, columns=self.items, index=self.items)
        return item_similar

    # 生成topN_user 找到相似的用户
    def makeTopNUsers(self, similar: pd.DataFrame, sign: int):
        topN_users = {}
        for i in similar.index:
            df_topN = similar.loc[i].drop([i])
            df_topN_sorted = df_topN.sort_values(ascending=False)
            # 目标用户是放在最开始的位置
            # print(df_topN_sorted)
            topN = []
            match sign:
                case 0:  # 0 时默认获取前N=5个数据
                    topN = list(df_topN_sorted.index[:5])
                    topN_users[i] = topN
                case 1:  # 1 获取几个相似度大于阈值0.95的用户
                    topN = self.getUserWithPearson(
                        df_topN_sorted)
                    topN_users[i] = topN
                    break
        return topN_users

    # 获取df中大于阈值（默认0.95）的数据
    def getUserWithPearson(self, df_top, threshold=0.95) -> list:
        topPearson_95 = list(df_top[(df_top[:] > threshold)].index)
        return topPearson_95

    # 计算某个tag在所有用户收藏的占比
    # 通过这些用户获取相似的歌曲，并排除某个用户已经有的歌曲

    def makeRecomUserByTag(self, topN: dict, song_num: int) -> dict:
        results = {}
        for user, similar_users in topN.items():
            result = set()
            for similar_user in similar_users:
                result = result.union(
                    set(self.df.loc[:, similar_user].replace(0, np.nan).dropna().index))
            result -= set(self.df.loc[:, user].replace(0,
                          np.nan).dropna().index)
            results[user] = list(result)[:song_num]
        return results

    # 使用Pearson相关系数
    def makeSimilarityWithPearson(self) -> pd.DataFrame:
        user_similar = self.df.corr()
        # print(user_similar.round(2))
        # print(user_similar)
        return user_similar.round(2)

    # 计算tag占比
    def computeRateofTag(self):
        data = self.df
        # print(self.df[self.df.columns[0]].sum())
        data['rate'] = (self.df[self.df.columns[1]] /
                        self.df[self.df.columns[1]].sum())
        self.df = self.formatRateforTag(data=data)
        return

    # 形成对应的list
    def formatRateforTag(self, data):
        data = data.sort_values('rate', ascending=False, kind='mergesort')
        data['rate'] = data['rate'].apply(lambda x: format(x, '.2%'))
        return data
