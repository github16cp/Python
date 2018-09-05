# 实战
-------
## Day1 - 搭建开发环境
-------
### 搭建开发环境
首先，确认系统安装的Python版本是3.6.x：
```Python
$ python3 --version
Python 3.6.1
```
然后，用`pip`安装开发Web App需要的第三方库：

异步框架`aiohttp`：
```Python
$pip3 install aiohttp
```
前端模板引擎jinja2：
```Python
$ pip3 install jinja2
```
MySQL 5.x数据库，从[官方网站](https://dev.mysql.com/downloads/mysql/5.6.html)下载并安装，安装完毕后，请务必牢记root口令。为避免遗忘口令，建议直接把root口令设置为password；

MySQL的Python异步驱动程序aiomysql：
```Python
$ pip3 install aiomysql
```
### 项目结构
选择一个工作目录，然后，我们建立如下的目录结构：
```Python
awesome-python3-webapp/  <-- 根目录
|
+- backup/               <-- 备份目录
|
+- conf/                 <-- 配置文件
|
+- dist/                 <-- 打包目录
|
+- www/                  <-- Web目录，存放.py文件
|  |
|  +- static/            <-- 存放静态文件
|  |
|  +- templates/         <-- 存放模板文件
|
+- ios/                  <-- 存放iOS App工程
|
+- LICENSE               <-- 代码LICENSE
```
创建好项目的目录结构后，建议同时建立git仓库并同步至GitHub，保证代码修改的安全。

要了解git和GitHub的用法，请移步[Git教程](https://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000)。
### 开发工具

自备，推荐用Sublime Text，请参考[使用文本编辑器](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/0014316399410395f704750ee9440228135925a6ca1dad8000)。
### 附
用Anaconda搭建运行环境：
```Python
conda create --name webpy3 python=3.6
conda activate webpy3
conda install xxx
conda deactivate
pip install aiomysql
```
## Day2 - 编写Web App骨架
-------
由于我们的Web App建立在asyncio的基础上，因此用aiohttp写一个基本的`app.py`：
```Python
import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

def index(request):
    return web.Response(body=b'<h1>Awesome</h1>')

@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
```
运行`python app.py`，Web App将在`9000`端口监听HTTP请求，并且对首页`/`进行响应：
```Python
$ python3 app.py
INFO:root:server started at http://127.0.0.1:9000...
```
这里我们简单地返回一个`Awesome`字符串，在浏览器中可以看到效果：

(此处出现问题，并不能在浏览器中出现效果，在地址连输入地址后发现是下载东西，该问题怎么解决？)

`在Response中加上content_type='text/html'就好了， return web.Response(body=b'<h1>Awesome</h1>', content_type='text/html')`

这说明我们的Web App骨架已经搭好了，可以进一步往里面添加更多的东西。
## Day 3 - 编写ORM
------
在一个Web App中，所有数据，包括用户信息、发布的日志、评论等，都存储在数据库中。在awesome-python3-webapp中，我们选择MySQL作为数据库。

Web App里面有很多地方都要访问数据库。访问数据库需要创建数据库连接、游标对象，然后执行SQL语句，最后处理异常，清理资源。这些访问数据库的代码如果分散到各个函数中，势必无法维护，也不利于代码复用。

所以，我们要首先把常用的SELECT、INSERT、UPDATE和DELETE操作用函数封装起来。

由于Web框架使用了基于asyncio的aiohttp，这是基于协程的异步模型。在协程中，不能调用普通的同步IO操作，因为所有用户都是由一个线程服务的，协程的执行速度必须非常快，才能处理大量用户的请求。而耗时的IO操作不能在协程中以同步的方式调用，否则，等待一个IO操作时，系统无法响应任何其他用户。

这就是异步编程的一个原则：一旦决定使用异步，则系统每一层都必须是异步，“开弓没有回头箭”。

幸运的是`aiomysql`为MySQL数据库提供了异步IO的驱动。
### 创建连接池
------
我们需要创建一个全局的连接池，每个HTTP请求都可以从连接池中直接获取数据库连接。使用连接池的好处是不必频繁地打开和关闭数据库连接，而是能复用就尽量复用。

连接池由全局变量`__pool`存储，缺省情况下将编码设置为`utf8`，自动提交事务：
```Python
@asyncio.coroutine
def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = yield from aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )
```
### Select
要执行SELECT语句，我们用`select`函数执行，需要传入SQL语句和SQL参数：
```Python
@asyncio.coroutine
def select(sql, args, size=None):
    log(sql, args)
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor(aiomysql.DictCursor)
        yield from cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows returned: %s' % len(rs))
        return rs
```
SQL语句的占位符是`?`，而MySQL的占位符是`%s`，`select()`函数在内部自动替换。注意要始终坚持使用带参数的SQL，而不是自己拼接SQL字符串，这样可以防止SQL注入攻击。

注意到`yield from`将调用一个子协程（也就是在一个协程中调用另一个协程）并直接获得子协程的返回结果。

如果传入`size`参数，就通过`fetchmany()`获取最多指定数量的记录，否则，通过`fetchall()`获取所有记录。
### Insert, Update, Delete
要执行INSERT、UPDATE、DELETE语句，可以定义一个通用的`execute()`函数，因为这3种SQL的执行都需要相同的参数，以及返回一个整数表示影响的行数：
```Python
@asyncio.coroutine
def execute(sql, args):
    log(sql)
    with (yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise
        return affected
```
`execute()`函数和`select()`函数所不同的是，cursor对象不返回结果集，而是通过`rowcount`返回结果数。

### ORM
有了基本的`select()`和`execute()`函数，我们就可以开始编写一个简单的ORM了。

设计ORM需要从上层调用者角度来设计。

我们先考虑如何定义一个`User`对象，然后把数据库表`users`和它关联起来。
```Python
from orm import Model, StringField, IntegerField

class User(Model):
    __table__ = 'users'

    id = IntegerField(primary_key=True)
    name = StringField()
```
注意到定义在`User`类中的`__table__`、`id`和`name`是类的属性，不是实例的属性。所以，在类级别上定义的属性用来描述`User`对象和表的映射关系，而实例属性必须通过`__init__()`方法去初始化，所以两者互不干扰：
```Python
# 创建实例:
user = User(id=123, name='Michael')
# 存入数据库:
user.insert()
# 查询所有User对象:
users = User.findAll()
```
### 定义Model
首先要定义的是所有ORM映射的基类`Model`：
```Python
class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value
```
`Model`从`dict`继承，所以具备所有`dict`的功能，同时又实现了特殊方法`__getattr__()`和`__setattr__()`，因此又可以像引用普通字段那样写：
```Python
>>> user['id']
123
>>> user.id
123
```
以及`Field`和各种`Field`子类：
```Python
class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)
```
映射`varchar`的`StringField`：
```Python
class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)
```
注意到`Model`只是一个基类，如何将具体的子类如`User`的映射信息读取出来呢？答案就是通过metaclass：`ModelMetaclass`：

```Python
class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        # 排除Model类本身:
        if name=='Model':
            return type.__new__(cls, name, bases, attrs)
        # 获取table名称:
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        # 获取所有的Field和主键名:
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    # 找到主键:
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey # 主键属性名
        attrs['__fields__'] = fields # 除主键外的属性名
        # 构造默认的SELECT, INSERT, UPDATE和DELETE语句:
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)
```
这样，任何继承自Model的类（比如User），会自动通过ModelMetaclass扫描映射关系，并存储到自身的类属性如`__table__`、`__mappings__`中。

然后，我们往Model类添加class方法，就可以让所有子类调用class方法：
```Python
class Model(dict):

    ...

    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        ' find object by primary key. '
        rs = yield from select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])
```
User类现在就可以通过类方法实现主键查找：
```Python
user = yield from User.find('123')
```
往Model类添加实例方法，就可以让所有子类调用实例方法：
```Python
class Model(dict):

    ...

    @asyncio.coroutine
    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = yield from execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)
```
这样，就可以把一个User实例存入数据库：
```Python
user = User(id=123, name='Michael')
yield from user.save()
```
最后一步是完善ORM，对于查找，我们可以实现以下方法：
* findAll() - 根据WHERE条件查找；
* findNumber() - 根据WHERE条件查找，但返回的是整数，适用于`select count(*)`类型的SQL。

以及`update()`和`remove()`方法。

所有这些方法都必须用`@asyncio.coroutine`装饰，变成一个协程。

调用时需要特别注意：
```Python
user.save()
```
没有任何效果，因为调用`save()`仅仅是创建了一个协程，并没有执行它。一定要用：
```Python
yield from user.save()
```
才真正执行了INSERT操作。

最后看看我们实现的ORM模块一共多少行代码？累计不到300多行。用Python写一个ORM是不是很容易呢？

源代码 [orm.py](https://github.com/github16cp/Python/blob/master/awesome_py3_webapp/www/orm.py)

测试`orm.py`:
```Python
from orm import Model, StringField, IntegerField

class User(Model):
    __table__ = 'users'

    id = IntegerField(primary_key=True)
    name = StringField()

# 创建实例:
user = User(id=123, name='Michael')
# 存入数据库:
user.save()
# 查询所有User对象:
users = User.findAll()
print(user['id'])
print(user.id)
```

测试`models.py`
```Python
import orm,asyncio
from models import User,Blog,Comment

async def test():
    await orm.create_pool(loop=loop,user='www-data',password='www-data',db='awesome')
    u = User(name='test3',email='test4@test.com',passwd='test',image='about:blank')
    #u = User(name='Test',email='test@example.com',passwd='1234567890',image='about:blank')
    await u.save()

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()
```
`注意`：在测试之前首先启动mysql，执行schema.sql脚本，步骤结构如下：
```Python
盘符>mysql -u root -p
Enter password:
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 10
Server version: 5.6.41 MySQL Community Server (GPL)

Copyright (c) 2000, 2018, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| test               |
+--------------------+
4 rows in set (0.03 sec)

mysql> source ./.(路径)/schema.sql
Query OK, 0 rows affected, 1 warning (0.04 sec)

Query OK, 1 row affected (0.04 sec)

Database changed
Query OK, 0 rows affected (0.09 sec)

Query OK, 0 rows affected (0.55 sec)

Query OK, 0 rows affected (0.31 sec)

Query OK, 0 rows affected (0.19 sec)

mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| awesome            |
| mysql              |
| performance_schema |
| test               |
+--------------------+
5 rows in set (0.00 sec)
mysql> show tables;
+-------------------+
| Tables_in_awesome |
+-------------------+
| blogs             |
| comments          |
| users             |
+-------------------+
3 rows in set (0.03 sec)
mysql> describe users;
+------------+--------------+------+-----+---------+-------+
| Field      | Type         | Null | Key | Default | Extra |
+------------+--------------+------+-----+---------+-------+
| id         | varchar(50)  | NO   | PRI | NULL    |       |
| email      | varchar(50)  | NO   | UNI | NULL    |       |
| passwd     | varchar(50)  | NO   |     | NULL    |       |
| admin      | tinyint(1)   | NO   |     | NULL    |       |
| name       | varchar(50)  | NO   |     | NULL    |       |
| image      | varchar(500) | NO   |     | NULL    |       |
| created_at | double       | NO   | MUL | NULL    |       |
+------------+--------------+------+-----+---------+-------+
7 rows in set (0.03 sec)

mysql> select * from users;
+----------------------------------------------------+------------------+------------+-------+------+-------------+------------------+
| id                                                 | email            | passwd     | admin | name | image       | created_at       |
+----------------------------------------------------+------------------+------------+-------+------+-------------+------------------+
| 001536115962695ccafc12b6c68445e958667f5cab6065c000 | test@example.com | 1234567890 |     0 | Test | about:blank | 1536115962.69569 |
+----------------------------------------------------+------------------+------------+-------+------+-------------+------------------+
1 row in set (0.02 sec)

mysql> select * from users;
+----------------------------------------------------+------------------+------------+-------+-------+-------------+------------------+
| id                                                 | email            | passwd     | admin | name  | image       | created_at       |
+----------------------------------------------------+------------------+------------+-------+-------+-------------+------------------+
| 001536115962695ccafc12b6c68445e958667f5cab6065c000 | test@example.com | 1234567890 |     0 | Test  | about:blank | 1536115962.69569 |
| 001536116740855bb86d5880afa49658311e32410b27666000 | test4@test.com   | test       |     0 | test3 | about:blank | 1536116740.85486 |
+----------------------------------------------------+------------------+------------+-------+-------+-------------+------------------+
2 rows in set (0.00 sec)
```
