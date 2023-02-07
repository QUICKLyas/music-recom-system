#!/usr/bin/python3
import controller.UserTagC as userTagC

users = ["A", "B", "C", "D"]

tags = ["..", "...", "...."]

userTagsController = userTagC.UserTagsController(users, tags)

us = userTagsController.getUsers()
tag = userTagsController.getTags()
print(us, tag)
# return us
