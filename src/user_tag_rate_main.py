#!/usr/bin/python3
# 本程序只是为每个用户生辰他们收藏歌曲tag 的概率集
import dao.MongoTagUser as mtu

mongotu = mtu.TagofUserCountRate()
mongotu.makeTagRateforUser()
