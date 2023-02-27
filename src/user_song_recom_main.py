#!/usr/bin/python3
import dao.MongoUsersSong as mus

mongomus = mus.UserSongRecom(user_id="1a78ac10b67911ed95dd00155dadb10b")
mongomus.makeRecomSongAnswer(limit="ONE")
