#!/usr/bin/python3
import dao.MongoTagUser as mtu

import utils.FileUse as fu


# 设置默认的文件读取路径
user_id = fu.readJsonFile(path='data/user_target.json')


mongotu = mtu.TagofSongUserRecom(user_id=user_id['name'])
mongotu.makeRecomUsersSetAnswer(limit="ONE")
# mongtu = mtu.TagofSongUserRecom()
# mongtu.makeRecomUsersSetAnswer(limit="ALL")
