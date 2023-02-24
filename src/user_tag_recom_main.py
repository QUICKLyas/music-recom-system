#!/usr/bin/python3
import dao.MongoTagUser as mtu

mongotu = mtu.TagofSongUserRecom(user_id="0bc2cc42a7be11edb7f600155daffd24")
mongotu.makeRecomUsersSetAnswer(limit="ONE")
