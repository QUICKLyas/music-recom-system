#!/usr/bin/python3
# 本程序是为了进步对用户之间的歌曲进行一个相似度计算的测试程序集
# 预定是在user_song_recom_main.py中运行
import dao.MongoTagUser as mtu

mongotu = mtu.TagofUserCountRate()
mongotu.makeTagRateforUser()
