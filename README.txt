本项目基于 tsxyScore 延伸而来，目的是打造一个提供唐山学院各类服务的多功能后台


接下来:
[ ] 查分组件 core.py
- [x] 查询免等待:cookies保存/载入
- [ ] 抽象化:查分部分 与 模拟登录部分 区分开.便于以后添加新功能

[ ]  数据库 (sql).py
- [ ] 数据库接口化，对程序其他部分隐藏数据库操作细节
- [ ] 加入数据库异常处理, 并在出错时告知用户

部署:
在项目根目录新建conf.ini文件
```
[qmail]
host = smtp.qq.com
port = 465
user = (QQ号)@qq.com
passwd = (QQ邮箱授权码)

[tsxy]
stu = (学号)
pwd = (密码)
```
请替换括号及括号中的内容，不需要引号。

执行以下命令
```
 $ sudo pip install -r requirements.txt
 $ uwsgi --http :9999 -w index
```

功能介绍:
1. 模拟登陆

