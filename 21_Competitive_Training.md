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
关于此节的一些参考 - [廖雪峰讨论](https://www.liaoxuefeng.com/discuss/001409195742008d822b26cf3de46aea14f2b7378a1ba91000/0014343464019826e946ddb3cc9498c969d47deca592311000?)
## Day4 - 编写Model
-------
有了ORM，我们就可以把Web App需要的3个表用`Model`表示出来：
```Python
import time, uuid

from orm import Model, StringField, BooleanField, FloatField, TextField

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)

class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)

class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)
```
在编写ORM时，给一个Field增加一个`default`参数可以让ORM自己填入缺省值，非常方便。并且，缺省值可以作为函数对象传入，在调用`save()`时自动计算。

例如，主键`id`的缺省值是函数`next_id`，创建时间`created_at`的缺省值是函数`time.time`，可以自动设置当前日期和时间。

日期和时间用`float`类型存储在数据库中，而不是`datetime`类型，这么做的好处是不必关心数据库的时区以及时区转换问题，排序非常简单，显示的时候，只需要做一个`float`到`str`的转换，也非常容易。

### 初始化数据库表
如果表的数量很少，可以手写创建表的SQL脚本：
```Python
-- schema.sql

drop database if exists awesome;

create database awesome;

use awesome;

grant select, insert, update, delete on awesome.* to 'www-data'@'localhost' identified by 'www-data';

create table users (
    `id` varchar(50) not null,
    `email` varchar(50) not null,
    `passwd` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `image` varchar(500) not null,
    `created_at` real not null,
    unique key `idx_email` (`email`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table blogs (
    `id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `name` varchar(50) not null,
    `summary` varchar(200) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table comments (
    `id` varchar(50) not null,
    `blog_id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;
```
如果表的数量很多，可以从`Model`对象直接通过脚本自动生成SQL脚本，使用更简单。

把SQL脚本放到MySQL命令行里执行：
```Python
$ mysql -u root -p < schema.sql
```
我们就完成了数据库表的初始化。
### 编写数据访问代码
接下来，就可以真正开始编写代码操作对象了。比如，对于`User`对象，我们就可以做如下操作：
```Python
import orm
from models import User, Blog, Comment

def test():
    yield from orm.create_pool(user='www-data', password='www-data', database='awesome')

    u = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')

    yield from u.save()

for x in test():
    pass
```
可以在MySQL客户端命令行查询，看看数据是不是正常存储到MySQL里面了。

本节源代码 [models.py](https://github.com/github16cp/Python/blob/master/awesome_py3_webapp/www/models.py)
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
## Day 5 - 编写Web框架
------
在正式开始Web开发前，我们需要编写一个Web框架。

`aiohttp`已经是一个Web框架了，为什么我们还需要自己封装一个？

原因是从使用者的角度来说，`aiohttp`相对比较底层，编写一个URL的处理函数需要这么几步：

第一步，编写一个用`@asyncio.coroutine`装饰的函数：
```Python
@asyncio.coroutine
def handle_url_xxx(request):
    pass
```
第二步，传入的参数需要自己从`request`中获取：
```Python
url_param = request.match_info['key']
query_params = parse_qs(request.query_string)
```
最后，需要自己构造`Response`对象：
```Python
text = render('template', data)
return web.Response(text.encode('utf-8'))
```
这些重复的工作可以由框架完成。例如，处理带参数的URL`/blog/{id}`可以这么写：
```Python
@get('/blog/{id}')
def get_blog(id):
    pass
```
处理query_string参数可以通过关键字参数**kw或者命名关键字参数接收：
```Python
@get('/api/comments')
def api_comments(*, page='1'):
    pass
```
对于函数的返回值，不一定是`web.Response`对象，可以是`str`、`bytes`或`dict`。

如果希望渲染模板，我们可以这么返回一个`dict`：
```Python
return {
    '__template__': 'index.html',
    'data': '...'
}
```
因此，Web框架的设计是完全从使用者出发，目的是让使用者编写尽可能少的代码。

编写简单的函数而非引入`request`和`web.Response`还有一个额外的好处，就是可以单独测试，否则，需要模拟一个`request`才能测试。

### @get和@post
要把一个函数映射为一个URL处理函数，我们先定义`@get()`：
```Python
def get(path):
    '''
    Define decorator @get('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator
```
这样，一个函数通过`@get()`的装饰就附带了URL信息。

`@post`与`@get`定义类似。
###　定义RequestHandler
URL处理函数不一定是一个`coroutine`，因此我们用`RequestHandler()`来封装一个URL处理函数。

`RequestHandler`是一个类，由于定义了`__call__()`方法，因此可以将其实例视为函数。

`RequestHandler`目的就是从URL函数中分析其需要接收的参数，从`request`中获取必要的参数，调用URL函数，然后把结果转换为`web.Response`对象，这样，就完全符合`aiohttp`框架的要求：
```Python
class RequestHandler(object):

    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        ...

    @asyncio.coroutine
    def __call__(self, request):
        kw = ... 获取参数
        r = yield from self._func(**kw)
        return r
```
再编写一个`add_route`函数，用来注册一个URL处理函数：
```Python
def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))
```
最后一步，把很多次`add_route()`注册的调用：
```Python
add_route(app, handles.index)
add_route(app, handles.blog)
add_route(app, handles.create_comment)
...
```
变成自动扫描：
```Python
# 自动把handler模块的所有符合条件的函数注册了:
add_routes(app, 'handlers')
```
add_routes()定义如下：
```Python
def add_routes(app, module_name):
    n = module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n+1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                add_route(app, fn)
```
最后，在`app.py`中加入`middleware`、`jinja2`模板和自注册的支持：
```Python
app = web.Application(loop=loop, middlewares=[
    logger_factory, response_factory
])
init_jinja2(app, filters=dict(datetime=datetime_filter))
add_routes(app, 'handlers')
add_static(app)
```
### middleware
`middleware`是一种拦截器，一个URL在被某个函数处理前，可以经过一系列的`middleware`的处理。

一个`middleware`可以改变URL的输入、输出，甚至可以决定不继续处理而直接返回。middleware的用处就在于把通用的功能从每个URL处理函数中拿出来，集中放到一个地方。例如，一个记录URL日志的`logger`可以简单定义如下：
```Python
@asyncio.coroutine
def logger_factory(app, handler):
    @asyncio.coroutine
    def logger(request):
        # 记录日志:
        logging.info('Request: %s %s' % (request.method, request.path))
        # 继续处理请求:
        return (yield from handler(request))
    return logger
```
而`response`这个`middleware`把返回值转换为`web.Response`对象再返回，以保证满足`aiohttp`的要求：
```Python
@asyncio.coroutine
def response_factory(app, handler):
    @asyncio.coroutine
    def response(request):
        # 结果:
        r = yield from handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            ...
```
有了这些基础设施，我们就可以专注地往`handlers`模块不断添加URL处理函数了，可以极大地提高开发效率。

## Day 6 - 编写配置文件
-------
有了Web框架和ORM框架，我们就可以开始装配App了。

通常，一个Web App在运行时都需要读取配置文件，比如数据库的用户名、口令等，在不同的环境中运行时，Web App可以通过读取不同的配置文件来获得正确的配置。

由于Python本身语法简单，完全可以直接用Python源代码来实现配置，而不需要再解析一个单独的`.properties`或者`.yaml`等配置文件。

默认的配置文件应该完全符合本地开发环境，这样，无需任何设置，就可以立刻启动服务器。

我们把默认的配置文件命名为`config_default.py`：
```Python
# config_default.py

configs = {
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'www-data',
        'password': 'www-data',
        'database': 'awesome'
    },
    'session': {
        'secret': 'AwEsOmE'
    }
}
```
上述配置文件简单明了。但是，如果要部署到服务器时，通常需要修改数据库的host等信息，直接修改`config_default.py`不是一个好办法，更好的方法是编写一个`config_override.py`，用来覆盖某些默认设置：
```Python
# config_override.py

configs = {
    'db': {
        'host': '192.168.0.100'
    }
}
```
把`config_default.py`作为开发环境的标准配置，把`config_override.py`作为生产环境的标准配置，我们就可以既方便地在本地开发，又可以随时把应用部署到服务器上。

应用程序读取配置文件需要优先从`config_override.py`读取。为了简化读取配置文件，可以把所有配置读取到统一的`config.py`中：
```Python
# config.py
configs = config_default.configs

try:
    import config_override
    configs = merge(configs, config_override.configs)
except ImportError:
    pass
```
App的配置完成。

## Day 7 - 编写MVC
现在，ORM框架、Web框架和配置都已就绪，我们可以开始编写一个最简单的MVC，把它们全部启动起来。

通过Web框架的`@get`和ORM框架的Model支持，可以很容易地编写一个处理首页URL的函数：
```Python
@get('/')
def index(request):
    users = yield from User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }
```
`'__template__'`指定的模板文件是`test.html`，其他参数是传递给模板的数据，所以我们在模板的根目录`templates`下创建`test.html`：
```Python
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Test users - Awesome Python Webapp</title>
</head>
<body>
    <h1>All users</h1>
    {% for u in users %}
    <p>{{ u.name }} / {{ u.email }}</p>
    {% endfor %}
</body>
</html>
```
接下来，如果一切顺利，可以用命令行启动Web服务器：
```Python
$ python3 app.py
```
然后，在浏览器中访问`http://localhost:9000/`。

如果数据库的`users`表什么内容也没有，你就无法在浏览器中看到循环输出的内容。可以自己在MySQL的命令行里给`users`表添加几条记录，然后再访问：

`注意`：这儿出现了错误OSError: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 9000):解决方案，关闭编辑器，重新编译调试，原因：端口被占用。
```Python

```