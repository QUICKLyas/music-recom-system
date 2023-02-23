#!/usr/bin/python3
import controller.UserTagC as userTagC
import dao.MongoUsersSong as mus
import dao.MongoTagUser as tu

import dao.MongoTagUser as mtu

# 默认测试用户获取推荐的用户集
# mongotu = mtu.TagofSongUserRecom(user_id="0bc2cc42a7be11edb7f600155daffd24")
# mongotu.makeRecomUsersSet()
# 运行完毕之后，我们需要知道这个用户被推荐的歌曲
mongomus = mus.UserSongRecom(user_id="0bc2cc42a7be11edb7f600155daffd24")
mongomus.makeRecomAnswerSong()
# mongotu = mtu.TagofSongUserRecom()
# mongotu.makeTagRateAnswer()

# users = ["A", "B", "C", "D"]

# tags = ["..", "...", "...."]

# userTagsController = userTagC.UserTagsController(users, tags)

# us = userTagsController.getUsers()
# tag = userTagsController.getTags()
# print(us, tag)
# return us
# m = mus.UserSongRecom()
# m.makeRecomSongAnswer()
# 需要获取用户名
# diction = m.makeRecomAnswer()
# print(diction)
# m.saveUserSongRecomAnswer(diction=diction)
# t = tu.TagofSongUserRecom()
# t.makeTagRateAnswer()
# 判断 用户 之间的相似度，通过听歌的tag 来判断
