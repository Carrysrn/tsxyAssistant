# -*- coding: utf-8 -*-
#import saekvdb as sql # SAE免费的就用这个
import radis_db as sql
from core import Score, core
from mail import mailToStu

from urllib2 import unquote

import web

class score:
    def GET(self):
        return 'POST it please.'
    def POST(self):
        data = postDatatoDict(web.data())# 获取POST中的 do键值对
        try:
            cmdList = data['cmd'].split('+')
            wxId = data['wxId']
            do = cmdList[0]
        except:
            return '参数错误！注意命令里不要有空格，并且确保使用的是英文的加号'

        tt = ['查分', '查询', '分数', '成绩']
        if do == '邮箱':
            try:
                email = cmdList[1]
                print email
                return _mail(wxId, email, type='new')
            except:
                return '输入有误!\n邮箱命令用法为："邮箱+你要绑定的邮箱"'
        elif do == '管理员':
            import mail
            try:
                msg = ''
                for line in cmdList[2:]:
                    msg = msg + line + ' '
                if isQmail(cmdList[1]):
                    mail.toAdmin('管理员，有人找', msg + '\n联系方式：' + cmdList[1])
                else:
                    return '请留下您的QQ邮箱，以便我们及时联系您～'
            except:
                return '给管理员发消息的命令是“管理员+你的QQ邮箱+你想说的话”\n加号应该是英文的加号，不要有空格'
            return '您的消息已转达管理员！'
        elif do[0:6] in tt:  # 查询功能
            try:
                if do[6] == '1':  # 没有这个就except了..
                    return _query(wxId, 'all')
            except:
                pass
            return _query(wxId, 'new')
        elif do == '测试':
            return unquote(web.data())
        elif do == '绑定':  # 绑定功能
            try:
                stuId = cmdList[1]
                passwd = cmdList[2]
                return _bind(wxId, stuId, passwd)
            except IndexError:
                return '输入有误!\n绑定命令用法为：“绑定+学号+密码”'
        elif do == 'root':
            try:
                stuId = cmdList[1]
                type = cmdList[2]
                return _root(stuId, type)
            except IndexError:
                return '输入有误'
        return """好尴尬...没识别你的指令...
现在的指令有:
“绑定+学号+教务系统密码“ 绑定后 即可使用 “查分“ 指令
“邮箱+你的QQ邮箱“ 即可绑定邮箱，未来会更新邮件发送服务呦
“管理员+你的QQ邮箱+你想说的话“ 可以向管理员提意见 / 吐槽呦
请注意：
加号必须为英文加号
除了联系管理员中‘你想说的话’部分，其它所有的命令都不要包含空格
资金捉急，目前仅仅支持QQ邮箱，敬请谅解
"""

def _root(stuId, type = 'new'):
    userCode = sql.get('stuId:' + stuId)
    if userCode is not None:
        return Score().webget(userCode, type)
    else:
        return '没找到'

def _bind(wxId, stuId, passwd):
    if sql.isbinded(wxId):
        return '你好像已经绑定了～请直接发送‘查询’查询成绩～'
    user = core(stuId, passwd)
    if user.safeLogin():
        userCode = user.getUserCode()
        return sql.bind(wxId, userCode)
    else:
        return '账号密码有误,请确认。'


def _query(wxId, type='new'):
    # 执行查询
    userCode = sql.get('wxId+'+wxId)  # 数据库中查询学号对应的UserCode
    if userCode is not None:
        return Score().webget(userCode, type)
    else:
        return '请发送“绑定+学号+教务系统密码”进行绑定\n绑定仅仅为了确认您的身份，以防您的隐私泄露\n服务器不会保存您的密码\n为确保账号安全，绑定后请尽快修改您的密码'


def isQmail(email):
    import re
    r = re.compile(r'^.+?@qq\.com$')
    g = re.match(r, email)
    if g == None:
        return False
    return True
def _mail(wxId, email, type='new'):
    if isQmail(email):
        msg = sql.bindmail(wxId, email)
        if msg[0:2] == 'OK':
            mailmsg = mailToStu(email, sql.get('wxId+'+wxId))
            if mailmsg[0:2] == 'ER':
                return mailmsg
            return msg + '\n稍后您将接收到一封包含您最新成绩的邮件'
        else:
            return msg
    else:
        return '非常抱歉，目前仅支持QQ邮箱'


def postDatatoDict(data):
    dict = {}
    data = data.split('&')
    for line in data:
        s = line.split('=')
        dict[unquote(s[0])] = unquote(s[1])
    return dict
