#!/usr/bin/python3
# 本程序是为了进步对用户之间的歌曲进行一个相似度计算的测试程序集
# 预定是在user_song_recom_main.py中运行
import dao.MongoUsersSong as mus
import utils.FileUse as fu


# {
#     "user_id": "1a78ac10b67911ed95dd00155dadb10b"
# }
user_id = fu.readJsonFile(path='src/data/user_target.json')
# 获取相似用户数列集
# 根据这相似用户集需要重新更新到数据库中
# 从这里开始重新获取数据
# 通过用户进行歌曲的歌曲相似度推荐 获取的其中的相似歌曲
mongomus = mus.UserSongRecomAfterSongSimilarity(
    user_id=user_id['user_id'])
# 1a78ac10b67911ed95dd00155dadb10b
mongomus.makeRecomBySongSimilarityAnswer(limit="ONE")
# 重新获取用户的信息，从而生成一定数量的相似歌曲
# mongomus_songs = mus.UserSongRecomAfterSongSimilarity(
#     user_id=user_id['user_id'])
# # 1a78ac10b67911ed95dd00155dadb10b
# mongomus_songs.makeRecomBySongSimilarityAnswer(limit="ALL")
