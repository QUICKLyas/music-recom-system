#!/usr/bin/python3

import sys

import json
import ssl as s
from urllib import request
from fake_useragent import UserAgent as ua
import mongo.Mongo as connect
# 本程序只更新当前操作的数据的内容，不处理其他位置上的数据。
# 本程序只接受一个参数，该参数是需要操作的对象id
# 程序会根据这个id查找数据url，并将最新的url保存到数据库中
# 程序启动的条件是，java调用且url是不可用的数据的时候就会运行这个程序
# 参数只有一个id


def update_url(id: int) -> bool:
    # 程序不返回Boolean，成功为True，失败为False
    # 调用id
    # 建立网络访问url
    song_url = "http://localhost:3000/song/url?id="+id

    # 获取我们需要的信息
    req = request.Request(
        url=song_url,
        headers={'User-Agent': ua().chrome})
    ssl = s._create_unverified_context()
    res = request.urlopen(req, context=ssl)
    context = res.read().decode('utf-8')
    context = json.loads(context)
    # data 就是我们需要的信息，我们需要将数据更新到数据库中
    data = context['data'][0]
    # 构建mongo连接
    con = connect.Conn()
    condb = con.getDB()
    cols = condb['song']
    query = {"id": id}
    new_values = {"$set": {
        "songUrl": data['url'], "data": data}}
    result = cols.update_one(query, new_values)
    if(result.modified_count is 1):
        return True
    else:
        return False
    # self.con = mongoConnect.Conn()
    # self.condb = self.con.getDB()


if __name__ == '__main__':
    a = []
    for i in range(1, len(sys.argv)):
        a.append((int(sys.argv[i])))
    update_url(a[0])
