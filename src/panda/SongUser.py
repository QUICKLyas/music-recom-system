import pandas as pd
import numpy as np
from sklearn.metrics import jaccard_score
from sklearn.metrics.pairwise import pairwise_distances


class SUPandas():
    def __init__(self, datas, songs, users) -> None:
        self.data = datas
        self.items = songs
        self.users = users
        self.df = pd.DataFrame(
            self.data, columns=self.items, index=self.users)
        pass

    # 获得杰卡德系数
    def getTaccardScore(self, df, user_name, other_name):
        return jaccard_score(df[user_name], df[user_name])

    # make 用户之间的两两相似度
    def makeSimilarityBetweenUser(self):
        user_similar = 1 - \
            pairwise_distances(self.df.values, metric="jaccard")
        user_similar = pd.DataFrame(
            user_similar, columns=self.users, indx=self.users)
        return user_similar

    # make 歌曲之间的两两相似度
    def makeSimilarityBetweenItem(self):
        item_similar = 1 - \
            pairwise_distances(self.df.T.values, metric="jaccard")
        item_similar = pd.DataFrame(
            item_similar, columns=self.items, index=self.items)
        return item_similar

    # 生成topN_user 找到相似的用户
    def makeTopNUsers(self, similar: pd.DataFrame):
        topN_users = {}
        for i in similar.index:
            df_topN = similar.loc[i].drop([i])
            df_topN_sorted = df_topN.sort_values(ascending=False)
            # 获取最相似的5个用户
            top5 = list(df_topN_sorted.index[:5])
            topN_users[i] = top5
        return topN_users

    # 通过这些用户获取相似的歌曲，并排除某个用户的已经有的歌曲
    def makeRecomUserSong(self, topN: dict, song_num: int):
        results = {}
        for user, simimlar_users in topN.items():
            result = set()
            for similar_user in simimlar_users:
                # rs_result.union(set(df.loc[sim_user].replace(0,np.nan).dropna().index))
                result = result.union(
                    set(self.df.loc[:, similar_user].replace(0, np.nan).dropna().index))
            result -= set(self.df.loc[:, user].replace(0,
                          np.nan).dropna().index)

            results[user] = list(result)[:song_num]
        return results
