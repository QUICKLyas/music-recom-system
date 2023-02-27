#!/usr/bin/python3
import dao.MongoTagUser as mtu

mongotu = mtu.TagofSongUserRecom(user_id="1a78ac10b67911ed95dd00155dadb10b")
mongotu.makeRecomUsersSetAnswer(limit="ONE")
# mongtu = mtu.TagofSongUserRecom()
# mongtu.makeRecomUsersSetAnswer(limit="ALL")
