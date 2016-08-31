# -*- coding: utf-8 -*-

import redis

# r = redis.StrictRedis(host='localhost', port=6379, db=0)

"""
key value 关系对应
wxId|       : userCode
mail|wxID   : stuEmail
stuId|      : userCode
"""

host = 'localhost'
port = 6379

adminUserCode = '201400000407'

def get(key):
    """
    获取值
    可用于 getUserCode(stuId) k:'stuId+'学号 v:userCode
    getUserCodeFromWxId(wxId) k:'wxId+'微信Id v:userCode
    k 'mail+'微信Id v:用户邮箱
    :param key
    :return: value
    """
    if len(key) >= 300:
        raise KeyError('key is too long')
    conn = redis.StrictRedis(host=host, port=port)
    value = conn.get(key)
    return value


def raw_set(key, value):
    """
    设置值
    :param key: k
    :param value: v
    :return: N/A
    """
    if len(key) >= 300:
        raise KeyError('太长了')
    conn = redis.StrictRedis(host=host, port=port)
    conn.set(key, value)

def check_set(key, value):
    """
    设置前检查
    :param key: k
    :param value: v
    :return: N/A
    """
    oldvalue = get(key)
    if oldvalue is None:
        raw_set(key, value)
    else:
        raise ValueError(oldvalue)


def bind(wxId, userCode):
    # userCode = get('stuId+' +  stuId)
    if userCode is None:
        return '找不到学号对应用户码，请反馈'
    try:
        check_set('wxId|' + wxId, userCode)
        return '绑定成功!\n可以发送‘查分’查询您的分数了呦\n为了您的账号安全，请您及时修改教务系统密码'
    except ValueError:
        return '该微信已经绑定了学号\n请‘解绑’解除绑定状态，或‘查分’查询您的分数'


def isbinded(wxId):
    value = get('wxId|' + wxId)
    if value is not None:
        return True
    return False


def isadmin(wxId):
    if get('wxId|' + wxId) == adminUserCode:
        return True
    return False


def bindmail(wxId, stuEmail):
    userCode = get('wxId|' + wxId)
    if userCode == None:
        return 'Error 请先绑定学号！'
    try:# 根据信息添加记录
        check_set('mail|' + wxId, stuEmail)
        return 'OK 绑定成功！'
    except ValueError:# 重复 更新
        raw_set('mail|' + wxId, stuEmail)
        return "OK 绑定邮箱更新为"+stuEmail

def getUserCodeByStuId(stuId):
    userCode = get('stuId|' + stuId)
    return userCode

def getUserCodeByWxId(wxId):
    userCode = get('wxId|' + wxId)
    return userCode

def setStuIdToWxId(stuId, userCode):
    check_set('stuId|' + stuId, userCode)

def setBind(wxId, userCode):
    check_set('wxId|' + wxId, userCode)

