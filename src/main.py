#!/usr/bin/python3
import controller.UserTagC as userTagC
import dao.MongoUserSong as mus
import dao.MongoTagUser as tu
# users = ["A", "B", "C", "D"]

# tags = ["..", "...", "...."]

# userTagsController = userTagC.UserTagsController(users, tags)

# us = userTagsController.getUsers()
# tag = userTagsController.getTags()
# print(us, tag)
# return us
m = mus.UserSongRecom()
m.makeRecomSongAnswer()
# 需要获取用户名
# diction = m.makeRecomAnswer()
# print(diction)
# m.saveUserSongRecomAnswer(diction=diction)
t = tu.TagofSongUserRecom()
t.makeTagRateAnswer()
