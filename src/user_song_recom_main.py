#!/usr/bin/python3
import dao.MongoUsersSong as mus

mongomus = mus.UserSongRecom(user_id="0bc2cc42a7be11edb7f600155daffd24")
mongomus.makeRecomSongAnswer(limit="ONE")
