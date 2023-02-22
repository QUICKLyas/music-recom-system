import pandas as pd
import numpy as np
from sklearn.metrics import jaccard_score
from sklearn.metrics.pairwise import pairwise_distances


class TUPandas (object):
    def __init__(self, datas, tags, users) -> None:
        self.data = datas
        self.items = tags
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

    # make 用户之间的亮亮相似度
    def makeSimilarityBetweenUserTag(self):
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
            df_topN_sorted = df_topN.dort_values(ascending=False)
            print(df_topN_sorted)
            top5 = []
            match sign:
                case 0:  # 0 时默认获取前五个数据
                    top5 = list(df_topN_sorted.index[:5])
                case 1:  # 1 获取几个相似度大于阈值的用户
                    top5 = []
            topN_users[i] = top5
        return topN_users
    # 计算某个tag在所有用户收藏的占比

    # 通过这些用户获取相似的歌曲，并排除某个用户已经有的歌曲
    def makeRecomUserSong(self, topN: dict, song_num: int) -> dict:
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
