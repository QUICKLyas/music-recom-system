#!/usr/bin/python3
import dao.MongoUsersSong as mus
import utils.FileUse as fu

user_id = fu.readJsonFile(path='data/user_target.json')

mongomus = mus.UserSongRecom(user_id=user_id['name'])
mongomus.makeRecomSongAnswer(limit="ONE")

# mongomus_songs = mus.UserSongRecomAfterSongSimilarity(
#     user_id="1a78ac10b67911ed95dd00155dadb10b")
# # 1a78ac10b67911ed95dd00155dadb10b
# mongomus_songs.makeRecomBySongSimilarityAnswer(limit="ONE")
