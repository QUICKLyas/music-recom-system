#!/usr/bin/python3
import dao.MongoUsersSong as mus

mongomus = mus.UserSongRecom(user_id="1a78b764b67911ed95dd00155dadb10b")
mongomus.makeRecomSongAnswer(limit="ONE")

# mongomus_songs = mus.UserSongRecomAfterSongSimilarity(
#     user_id="1a78ac10b67911ed95dd00155dadb10b")
# # 1a78ac10b67911ed95dd00155dadb10b
# mongomus_songs.makeRecomBySongSimilarityAnswer(limit="ONE")
