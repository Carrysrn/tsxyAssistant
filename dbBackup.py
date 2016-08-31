# -*- coding: utf-8 -*-
import sqlite3
import time
ISOTIMEFORMAT='%Y-%m-%d %X'


def init():
    import ini
    def iniGet(tag):
        return ini.Config('conf.ini').get('sql', tag)
    global _db
    _db = iniGet('db')

init()#初始化

import redis_db

def stuIdToRedisDB():
    conn = sqlite3.connect(_db)
    cursor = conn.execute("SELECT userCode, stuId FROM userCodes")
    i = 0
    for row in cursor:
        userCode = row[0]
        stuId = row[1]
        try:
            redis_db.setStuIdToWxId(stuId, userCode)
            print "stuId:%s, userCode:%s in" % (stuId, userCode)
        except ValueError:
            print 'stuId:%s already in' % stuId
        i += 1
    print 'SUCCESS!'
    print i

def bindInfoToRedisDB():
    conn = sqlite3.connect(_db)
    cursor = conn.execute("SELECT wxID, userCode FROM binds")
    i = 0
    for row in cursor:
        wxId = row[0]
        userCode = row[1]
        try:
            redis_db.setBind(wxId, userCode)
            print "wxId:%s, userCode:%s in" % (wxId, userCode)
        except ValueError:
            print 'wxId:%s already in' % wxId
        i += 1
    print 'SUCCESS!'
    print i


if __name__ == "__main__":
    # stuIdToRedisDB()
    bindInfoToRedisDB()
