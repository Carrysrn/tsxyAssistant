# -*- coding: utf-8 -*-
"""
青果教务系统 模拟登录/成绩抓取
使用 python2.7
需要安装的库见下
"""
import re
import pytesseract
import requests
import bs4
import ini
import cPickle

try:
    import Image
except:
    from PIL import Image

def iniGet(tag):
    return ini.Config('conf.ini').get('tsxy', tag)


class tsxyErr(BaseException):
    pass


class LoginErr(tsxyErr):
    pass


class GetErr(tsxyErr):
    pass


class NothingErr(GetErr):
    pass


class core(object):
    def __init__(self, stu = iniGet('stu'), pwd = iniGet('pwd')):
        """
        初始化对象
        简单的判断学号及密码是否符合要求
        :param stu:学号 9位或10位
        :param pwd:密码 最多30位
        """
        self._session = requests.session()
        self._url_postpage = 'http://jiaowu.tsc.edu.cn/tscjw/cas/logon.action'

        self._url_mainpage = 'http://jiaowu.tsc.edu.cn/tscjw/MainFrm.html'

        self._url_score = 'http://jiaowu.tsc.edu.cn/tscjw/student/xscj.stuckcj_data.jsp'

        if not (len(stu) == 9 or len(stu) == 10):
            raise ValueError('学号应为9位或10位！')
        self._stu = stu
        if len(pwd) == 0 or len(pwd) > 30:
            raise ValueError('密码值应为1~30位')
        self._pwd = pwd

        # 登陆/提交表单/获取页面 所需 headers
        # 暴力抓取的
        self.headers = {
            'Host': 'jiaowu.tsc.edu.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
            'Referer': 'http://jiaowu.tsc.edu.cn/tscjw/cas/login.action',
            'Connection': 'keep-alive',
        }
        self.cookiesLogin()


    def login(self):
        """
        模拟登陆 保留cookies及session以保存登陆状态
        :return:无返回值
        """
        def getrand():
            """
            获取验证码值 / 同时获取验证码页面的 cookies 到 self._cookies
            :return: 识别出的验证码
            """
            def randOK(text):
                """
                确认图像识别所得验证码为四位数字
                如果为四位数字 则说明验证码很大几率是正确的
                :param text: 识别的验证码
                :return: 是否为四位数字
                """
                if len(text) != 4:
                    return False
                try:
                    num = int(text)
                except:
                    return False
                if num > 1000 and num < 9999:
                    print text + 'Got'
                    return True
                return False

            import datetime
            GMT_FORMAT = '%a %b %d %Y %H:%M:%S GMT+0800 (CST)'
            # 这是校园网验证码页面url需要的日期格式 感谢 http://ju.outofmemory.cn/entry/1078
            text = ''
            while (not randOK(text)):
                imgurl = "http://jiaowu.tsc.edu.cn/tscjw/cas/genValidateCode?dateTime=" + \
                     str(datetime.datetime.now().strftime(GMT_FORMAT))
                img = self._session.get(imgurl, headers=self.headers)

                self._cookies = img.cookies # 以后的模拟登录需要这个cookies
                # 无须使用本地写权限/不会留下多余的验证码文件
                # thank to http://stackoverflow.com/questions/31064981/python3-error-initial-value-must-be-str-or-none
                from io import BytesIO
                im = Image.open(BytesIO(img.content))
                # 识别图像
                text = pytesseract.image_to_string(im)
            return text

        randnumber = getrand()

        def md5passwd(password, randnumber):
            """
            获取经password/验证码混合加密所得的passwd
            该”加密算法“来自官网登录页的JS脚本
            ###感谢师兄 旺哥将其翻译成了py版本###
                我以为js加法是16进制直接相加- -
                害得我在py里把两个16进制的转成10进制相加后再转成16进制- -
                马丹原来加号就是连接字符串啊- -
            :param password: 用户密码
            :param randnumber: 验证码
            :return: 登陆所需的已加密密码
            """
            def md5Encode(str):
                import hashlib
                m = hashlib.md5(str.encode(encoding='utf-8'))
                return m.hexdigest()
            passwd = md5Encode(md5Encode(password) + md5Encode(randnumber))
            return passwd

        passwd = md5passwd(self._pwd, randnumber)
        # 登陆提交的信息
        data = {
            'username': self._stu,
            'password': passwd,
            'randnumber': randnumber,
            'isPasswordPolicy': 1
        }
        self._session.post(url = self._url_postpage, data = data, headers = self.headers)
        # 获取主页HTML 判断是否成功登陆
        r2 = self._session.get(url = self._url_mainpage, headers = self.headers)
        # 正则表达式 判断抓取的页面是否有登陆成功时会出现的值.对 就是这么丑 :)
        r = re.compile('<p>This.+frames')
        if not r.search(r2.text):
            raise LoginErr
        else:
            print '模拟登陆成功!'

    def safeLogin(self):
        try:
            self.login()
        except LoginErr:
            try:
                self.login()
            except LoginErr:
                try:
                    self.login()
                except LoginErr:
                    return None
        return True


    def cookiesLogin(self):
        """
        安全登陆:不断加载文件cookies/模拟登陆,直到登陆成功为止
        :return:
        """

        def save_cookies(cookiesFile, cookies):
            try:
                with open(cookiesFile, 'w') as f:
                    cPickle.dump(requests.utils.dict_from_cookiejar(cookies), f)
                    print 'Saved'
                    f.close()
            except:
                print 'Save cookies failed'

        def load_cookies(cookiesFile):
            try:
                with open(cookiesFile, 'r') as f:
                    cookies = requests.utils.cookiejar_from_dict(cPickle.load(f))
                    f.close()
            except:
                cookies = ''
            return cookies

        cookiesFile = 'cookies'

        while True:
            cookies = load_cookies(cookiesFile)
            if cookies != '':
                self._session.cookies.update(cookies)
                userCode = self.isLogin()
                if userCode != None:
                    return
                else:
                    try:
                        print '1'
                        self.login()
                        save_cookies(cookiesFile, self._session.cookies)
                    except LoginErr:
                        print '登陆出错1'
            else:
                try:
                    self.login()
                    save_cookies(cookiesFile, self._session.cookies)
                    return
                except LoginErr:
                    print '登陆出错2'

    def getUserCode(self):
        """
        登陆状态下可以获取登录账户的UserCode
        获取不到说明没有登陆
        :return: 返回获取到的UserCode
        """
        url = 'http://jiaowu.tsc.edu.cn/tscjw/jw/common/showYearTerm.action'
        t = self._session.get(url=url, headers=self.headers)
        r = re.compile('"userCode":"(.+?)"')
        try:
            userCode = r.search(t.text).groups()[0]
        except:
            return None
        if userCode == 'kingo.guest':
            return None
        return userCode

    isLogin = getUserCode


class Score(core):
    def getScore(self, userCode, scoreType):
        """
        提交表单获取分数页面HTML代码
        :param userCode: 用户代码，一一对应
        :param scoreType: 类型 最新 new/ 所有 all
        :return:
        """
        data_all = {
            'sjxz': 'sjxz1',
            'ysyx': 'yscj',
            'userCode': userCode,
            'xn1': '2016',
            'ysyxS': 'on',
            'sjxzS': 'on',
            'menucode_current': ''
        }
        # 每个学期的不一样 懒得改
        data_new = {
            'sjxz': 'sjxz3',
            'ysyx': 'yscj',
            'userCode': userCode,
            'xn': '2015',
            'xn1': '2016',
            'xq': '1',
            'ysyxS': 'on',
            'sjxzS': 'on',
            'menucode_current': ''
        }
        if scoreType == 'all':
            data = data_all
        else:
            data = data_new
        r = self._session.post(url=self._url_score, data=data,
                               headers=self.headers)
        # print r.text
        if not re.compile(
                r'<div pagetitle="pagetitle" style="width:256mm;font-size:20px;font-weight:bold;" align="center">').search(
                r.text):
            raise GetErr
        return r.text


    def webget(self, userCode, scoreType='new'):
        """
        获取整理过的分数数据
        :param userCode:
        :param scoreType:
        :return:
        """

        def getStuInfo(soup):
            department = soup.find_all('div')[3].string.encode('utf-8').split('：')[1]
            grade = soup.find_all('div')[4].string.encode('utf-8').split('：')[1]
            stuId = soup.find_all('div')[5].string.encode('utf-8').split('：')[1]
            stuName = soup.find_all('div')[6].string.encode('utf-8').split('：')[1]
            return grade + ' ' + stuName

        html = self.getScore(userCode, scoreType)
        """ 多行注释 :)
        f = open('1.html', 'wb')
        f.write(html.encode('utf-8'))
        f.close()
        """
        soup = bs4.BeautifulSoup(html, 'html.parser')
        stuInfo = getStuInfo(soup)
        scores = re.compile(r'<tr>.+?>(\d+)<.+?](.+?)</td>.+?right;">\d+.+?</td>.+?right;">(.+?)</td>.+?center.+?</tr>',
                            re.S)
        allScore = ""
        for line in scores.findall(html):
            for word in line:
                allScore = allScore + word + ' '
            allScore = allScore + '\n'
        return stuInfo + '\n' + allScore.encode('utf-8')


if __name__ == "__main__":
    # print li.safeGetScore('201400000006')
    # http://jiaowu.tsc.edu.cn/tscjw/jw/common/showYearTerm.action
    li = Score()
    li.cookiesLogin()
    userCode = li.isLogin()
    print userCode
    print li.webget(userCode)