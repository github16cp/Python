# Python基础
## 数据类型和变量
---
## 字符串和编码
---
## 使用list和tuple
------
### list
---
Python内置的一种数据类型是列表：list。list是一种有序的集合，可以随时添加和删除其中的元素。

比如，列出班里所有同学的名字，就可以用一个list表示：
```Python
>>> classmates = ['Michael', 'Bob', 'Tracy']
>>> classmates
['Michael', 'Bob', 'Tracy']
```
变量 **classmates** 就是一个list。用 **len()** 函数可以获得list元素的个数
```Python
>>> len(classmates)
3
```
用索引来访问list中每一个位置的元素，记得索引是从0开始的：
```Python
>>> classmates[0]
'Michael'
>>> classmates[1]
'Bob'
>>> classmates[2]
'Tracy'
>>> classmates[3]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
IndexError: list index out of range
```
当索引超出了范围时，Python会报一个 **IndexError** 错误，所以，要确保索引不要越界，记得最后一个元素的索引是 **len(classmates) - 1** 。

如果要取最后一个元素，除了计算索引位置外，还可以用 **-1**做索引，直接获取最后一个元素：
```Python
>>> classmates[-1]
'Tracy'
```
以此类推，可以获取倒数第2个、倒数第3个：
```Python
>>> classmates[-2]
'Bob'
>>> classmates[-3]
'Michael'
>>> classmates[-4]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
IndexError: list index out of range
```
当然，倒数第4个就越界了。"markdown-preview-enhanced.codeBlockTheme": "default.css",

list是一个可变的有序表，所以，可以往list中追加元素到末尾：
```Python
>>> classmates.append('Adam')
>>> classmates
['Michael', 'Bob', 'Tracy', 'Adam']
```
也可以把元素插入到指定的位置，比如索引号为 **1** 的位置：
```Python
>>> classmates.insert(1, 'Jack')
>>> classmates
['Michael', 'Jack', 'Bob', 'Tracy', 'Adam']
```
要删除list末尾的元素，用 **pop()** 方法：
```Python
>>> classmates.pop()
'Adam'
>>> classmates
['Michael', 'Jack', 'Bob', 'Tracy']
```
要删除指定位置的元素，用 **pop(i)** 方法，其中 **i** 是索引位置：
```Python
>>> classmates.pop(1)
'Jack'
>>> classmates
['Michael', 'Bob', 'Tracy']
```
要把某个元素替换成别的元素，可以直接赋值给对应的索引位置：
```Python
>>> classmates[1] = 'Sarah'
>>> classmates
['Michael', 'Sarah', 'Tracy']
```
list里面的元素的数据类型也可以不同，比如：
```Python
>>> L = ['Apple', 123, True]
```
list元素也可以是另一个list，比如：
```Python
>>> s = ['python', 'java', ['asp', 'php'], 'scheme']
>>> len(s)
4
```
要注意s只有4个元素，其中 **s[2]** 又是一个list，如果拆开写就更容易理解了：
```Python
>>> p = ['asp', 'php']
>>> s = ['python', 'java', p, 'scheme']
```
要拿到 **'php'** 可以写 **p[1]** 或者 **s[2][1]** ，因此 **s** 可以看成是一个二维数组，类似的还有三维、四维……数组，不过很少用到。

如果一个list中一个元素也没有，就是一个空的list，它的长度为0：
```Python
>>> L = []
>>> len(L)
0
```

### tuple
---
另一种有序列表叫元组：tuple。tuple和list非常类似，但是tuple一旦初始化就不能修改，比如同样是列出同学的名字：

```Python
>>> classmates = ('Michael', 'Bob', 'Tracy')
```

现在，classmates这个tuple不能变了，它也没有append()，insert()这样的方法。其他获取元素的方法和list是一样的，你可以正常地使用 **classmates[0]** ，**classmates[-1]** ，但不能赋值成另外的元素。

不可变的tuple有什么意义？因为tuple不可变，所以代码更安全。如果可能，能用tuple代替list就尽量用tuple。

tuple的陷阱：当你定义一个tuple时，在定义的时候，tuple的元素就必须被确定下来，比如：
```Python
>>> t = (1, 2)
>>> t
(1, 2)
```
如果要定义一个空的tuple，可以写成()：
```Python
>>> t = ()
>>> t
()
```
但是，要定义一个只有1个元素的tuple，如果你这么定义：
```Python
>>> t = (1)
>>> t
1
```
定义的不是tuple，是`1`这个数！这是因为括号`()`既可以表示tuple，又可以表示数学公式中的小括号，这就产生了歧义，因此，Python规定，这种情况下，按小括号进行计算，计算结果自然是`1`。

所以，只有1个元素的tuple定义时必须加一个逗号`,`，来消除歧义：
```Python
>>> t = (1,)
>>> t
(1,)
```
最后来看一个“可变的”tuple：
```Python
>>> t = ('a', 'b', ['A', 'B'])
>>> t[2][0] = 'X'
>>> t[2][1] = 'Y'
>>> t
('a', 'b', ['X', 'Y'])
```
这个tuple定义的时候有3个元素，分别是`'a'`，`'b'`和一个list。不是说tuple一旦定义后就不可变了吗？怎么后来又变了？

别急，我们先看看定义的时候tuple包含的3个元素：
https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/0014316724772904521142196b74a3f8abf93d8e97c6ee6000

当我们把list的元素`'A'`和`'B'`修改为`'X'`和`'Y'`后，tuple变为：

https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/0014316724772904521142196b74a3f8abf93d8e97c6ee6000

表面上看，tuple的元素确实变了，但其实变的不是tuple的元素，而是list的元素。tuple一开始指向的list并没有改成别的list，所以，tuple所谓的“不变”是说，tuple的每个元素，指向永远不变。即指向`'a'`，就不能改成指向`'b'`，指向一个list，就不能改成指向其他对象，但指向的这个list本身是可变的！

理解了“指向不变”后，要创建一个内容也不变的tuple怎么做？那就必须保证tuple的每一个元素本身也不能变。

## 条件判断
----
###  条件判断
---
计算机之所以能做很多自动化的任务，因为它可以自己做条件判断。

比如，输入用户年龄，根据年龄打印不同的内容，在Python程序中，用`if`语句实现：
```Python
age = 20
if age >= 18:
    print('your age is', age)
    print('adult')
```
根据Python的缩进规则，如果`if`语句判断是`True`，就把缩进的两行print语句执行了，否则，什么也不做。

也可以给`if`添加一个`else`语句，意思是，如果`if`判断是`False`，不要执行`if`的内容，去把`else`执行了：
```Python
age = 3
if age >= 18:
    print('your age is', age)
    print('adult')
else:
    print('your age is', age)
    print('teenager')
```
注意不要少写了冒号`:`。

当然上面的判断是很粗略的，完全可以用`elif`做更细致的判断：
```Python
age = 3
if age >= 18:
    print('adult')
elif age >= 6:
    print('teenager')
else:
    print('kid')
```
`elif`是`else if`的缩写，完全可以有多个`elif`，所以`if`语句的完整形式就是：
```Python
if <条件判断1>:
    <执行1>
elif <条件判断2>:
    <执行2>
elif <条件判断3>:
    <执行3>
else:
    <执行4>
```
`if`语句执行有个特点，它是从上往下判断，如果在某个判断上是`True`，把该判断对应的语句执行后，就忽略掉剩下的`elif`和`else`，所以，请测试并解释为什么下面的程序打印的是`teenager`：
```Python
age = 20
if age >= 6:
    print('teenager')
elif age >= 18:
    print('adult')
else:
    print('kid')
```
`if`判断条件还可以简写，比如写：
```Python
if x:
    print('True')
```
只要`x`是非零数值、非空字符串、非空list等，就判断为`True`，否则为`False`。

### 再议input
---
最后看一个有问题的条件判断。很多同学会用`input()`读取用户的输入，这样可以自己输入，程序运行得更有意思：
```Python
birth = input('birth: ')
if birth < 2000:
    print('00前')
else:
    print('00后')
```
输入`1982`，结果报错：
```Python
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unorderable types: str() > int()
```
这是因为`input()`返回的数据类型是`str`，`str`不能直接和整数比较，必须先把`str`转换成整数。Python提供了`int()`函数来完成这件事情：
```Python
s = input('birth: ')
birth = int(s)
if birth < 2000:
    print('00前')
else:
    print('00后')
```

再次运行，就可以得到正确地结果。但是，如果输入`abc`呢？又会得到一个错误信息：
```Python
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: invalid literal for int() with base 10: 'abc'
```
原来`int()`函数发现一个字符串并不是合法的数字时就会报错，程序就退出了。

如何检查并捕获程序运行期的错误呢？后面的错误和调试会讲到。

### 练习
------
小明身高1.75，体重80.5kg。请根据BMI公式（体重除以身高的平方）帮小明计算他的BMI指数，并根据BMI指数：

* 低于18.5：过轻
* 18.5-25：正常
* 25-28：过重
* 28-32：肥胖
* 高于32：严重肥胖

用if-elif判断并打印结果：
```Python
# -*- coding: utf-8 -*-

height = 1.75
weight = 80.5
bmi = weight/(height*height)
if bmi < 18.5:
    print("过轻")
elif bmi <= 25:
    print("正常")
elif bmi <= 28:
    print("过重")
elif bmi <= 32:
    print("肥胖")
else:
    print("严重肥胖")

```

## 循环
------
### 循环
---
要计算1+2+3，我们可以直接写表达式：
```Python
>>> 1 + 2 + 3
6
```
要计算1+2+3+...+10，勉强也能写出来。

但是，要计算1+2+3+...+10000，直接写表达式就不可能了。

为了让计算机能计算成千上万次的重复运算，我们就需要循环语句。

Python的循环有两种，一种是for...in循环，依次把list或tuple中的每个元素迭代出来，看例子：
```Python
names = ['Michael', 'Bob', 'Tracy']
for name in names:
    print(name)
```
执行这段代码，会依次打印`names`的每一个元素：
```Python
Michael
Bob
Tracy
```
所以`for x in ...`循环就是把每个元素代入变量`x`，然后执行缩进块的语句。

再比如我们想计算1-10的整数之和，可以用一个`sum`变量做累加：
```Python
sum = 0
for x in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    sum = sum + x
print(sum)
```
如果要计算1-100的整数之和，从1写到100有点困难，幸好Python提供一个`range()`函数，可以生成一个整数序列，再通过`list()`函数可以转换为list。比如`range(5)`生成的序列是从0开始小于5的整数：
```Python
>>> list(range(5))
[0, 1, 2, 3, 4]
```
`range(101)`就可以生成0-100的整数序列，计算如下：
```Python
# -*- coding: utf-8 -*-
sum = 0
for x in range(101):
    sum = sum + x
print(sum)
```
第二种循环是while循环，只要条件满足，就不断循环，条件不满足时退出循环。比如我们要计算100以内所有奇数之和，可以用while循环实现：
```Python
sum = 0
n = 99
while n > 0:
    sum = sum + n
    n = n - 2
print(sum)
```
在循环内部变量`n`不断自减，直到变为`-1`时，不再满足while条件，循环退出。

### 练习
---
请利用循环依次对list中的每个名字打印出`Hello, xxx!`：
```Python
# -*- coding: utf-8 -*-
L = ['Bart', 'Lisa', 'Adam']
for x in L:
  print('Hello,%s!' % x)
```
或者
```Python
# -*- coding: utf-8 -*-
L = ['Bart', 'Lisa', 'Adam']  
l=len(L)
n=0
while n<l:
    print('Hello,%s!' % L[n])
    n = n + 1
```

### break
-------

在循环中，`break`语句可以提前退出循环。例如，本来要循环打印1～100的数字：
```Python
n = 1
while n <= 100:
    print(n)
    n = n + 1
print('END')
```
上面的代码可以打印出1~100。

如果要提前结束循环，可以用`break`语句：
```Python
n = 1
while n <= 100:
    if n > 10: # 当n = 11时，条件满足，执行break语句
        break # break语句会结束当前循环
    print(n)
    n = n + 1
print('END')
```
执行上面的代码可以看到，打印出1~10后，紧接着打印`END`，程序结束。

可见`break`的作用是提前结束循环。

### continue
------

在循环过程中，也可以通过`continue`语句，跳过当前的这次循环，直接开始下一次循环。
```Python
n = 0
while n < 10:
    n = n + 1
    print(n)
```
上面的程序可以打印出1～10。但是，如果我们想只打印奇数，可以用`continue`语句跳过某些循环：
```Python
n = 0
while n < 10:
    n = n + 1
    if n % 2 == 0: # 如果n是偶数，执行continue语句
        continue # continue语句会直接继续下一轮循环，后续的print()语句不会执行
    print(n)
```
执行上面的代码可以看到，打印的不再是1～10，而是1，3，5，7，9。

可见`continue`的作用是提前结束本轮循环，并直接开始下一轮循环。

### 小结
------
循环是让计算机做重复任务的有效的方法。

`break`语句可以在循环过程中直接退出循环，而`continue`语句可以提前结束本轮循环，并直接开始下一轮循环。这两个语句通常都`必须`配合`if`语句使用。

`要特别注意`，不要滥用`break`和`continue`语句。`break`和`continue`会造成代码执行逻辑分叉过多，容易出错。大多数循环并不需要用到`break`和`continue`语句，上面的两个例子，都可以通过`改写循环条件`或者`修改循环逻辑`，去掉`break`和`continue`语句。

有些时候，如果代码写得有问题，会让程序陷入“死循环”，也就是永远循环下去。这时可以用`Ctrl+C`退出程序，或者强制结束Python进程。

请试写一个死循环程序。

## 使用dict和set
---
### dict
---

Python内置了字典：dict的支持，dict全称dictionary，在其他语言中也称为map，使用键-值（key-value）存储，具有极快的查找速度。

举个例子，假设要根据同学的名字查找对应的成绩，如果用list实现，需要两个list：
```Python
names = ['Michael', 'Bob', 'Tracy']
scores = [95, 75, 85]
```
给定一个名字，要查找对应的成绩，就先要在names中找到对应的位置，再从scores取出对应的成绩，list越长，耗时越长。

如果用dict实现，只需要一个“名字”-“成绩”的对照表，直接根据名字查找成绩，无论这个表有多大，查找速度都不会变慢。用Python写一个dict如下：
```Python
>>> d = {'Michael': 95, 'Bob': 75, 'Tracy': 85}
>>> d['Michael']
95
```
为什么dict查找速度这么快？因为dict的实现原理和查字典是一样的。假设字典包含了1万个汉字，我们要查某一个字，一个办法是把字典从第一页往后翻，直到找到我们想要的字为止，这种方法就是在list中查找元素的方法，list越大，查找越慢。

第二种方法是先在字典的索引表里（比如部首表）查这个字对应的页码，然后直接翻到该页，找到这个字。无论找哪个字，这种查找速度都非常快，不会随着字典大小的增加而变慢。

dict就是第二种实现方式，给定一个名字，比如`'Michael'`，dict在内部就可以直接计算出`Michael`对应的存放成绩的“页码”，也就是95这个数字存放的内存地址，直接取出来，所以速度非常快。

你可以猜到，这种key-value存储方式，在放进去的时候，必须根据key算出value的存放位置，这样，取的时候才能根据key直接拿到value。

把数据放入dict的方法，除了初始化时指定外，还可以通过key放入：
```Python
>>> d['Adam'] = 67
>>> d['Adam']
67
```
由于一个key只能对应一个value，所以，多次对一个key放入value，后面的值会把前面的值冲掉：
```Python
>>> d['Jack'] = 90
>>> d['Jack']
90
>>> d['Jack'] = 88
>>> d['Jack']
88
```
如果key不存在，dict就会报错：
```Python
>>> d['Thomas']
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 'Thomas'
```
要避免key不存在的错误，有两种办法，一是通过`in`判断key是否存在：
```Python
>>> 'Thomas' in d
False
```
二是通过dict提供的`get()`方法，如果key不存在，可以返回`None`，或者自己指定的value：
```Python
>>> d.get('Thomas')
>>> d.get('Thomas', -1)
-1
```
注意：返回`None`的时候Python的交互环境不显示结果。

要删除一个key，用`pop(key)`方法，对应的value也会从dict中删除：
```Python
>>> d.pop('Bob')
75
>>> d
{'Michael': 95, 'Tracy': 85}
```
请务必注意，dict内部存放的顺序和key放入的顺序是没有关系的。

和list比较，dict有以下几个特点：

1. 查找和插入的速度极快，不会随着key的增加而变慢；
2. 需要占用大量的内存，内存浪费多。

而list相反：

1. 查找和插入的时间随着元素的增加而增加；
2. 占用空间小，浪费内存很少。

所以，dict是用空间来换取时间的一种方法。

dict可以用在需要高速查找的很多地方，在Python代码中几乎无处不在，正确使用dict非常重要，需要牢记的第一条就是dict的key必须是**不可变对象**。

这是因为dict根据key来计算value的存储位置，如果每次计算相同的key得出的结果不同，那dict内部就完全混乱了。这个通过key计算位置的算法称为哈希算法（Hash）。

要保证hash的正确性，作为key的对象就不能变。在Python中，字符串、整数等都是不可变的，因此，可以放心地作为key。而list是可变的，就不能作为key：
```Python
>>> key = [1, 2, 3]
>>> d[key] = 'a list'
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unhashable type: 'list'
```

### set
------
set和dict类似，也是一组key的集合，但不存储value。由于key不能重复，所以，在set中，没有重复的key。

要创建一个set，需要提供一个list作为输入集合：
```Python
>>> s = set([1, 2, 3])
>>> s
{1, 2, 3}
```
注意，传入的参数`[1, 2, 3]`是一个list，而显示的`{1, 2, 3}`只是告诉你这个set内部有1，2，3这3个元素，显示的顺序也不表示set是有序的。。

重复元素在set中自动被过滤：
```Python
>>> s = set([1, 1, 2, 2, 3, 3])
>>> s
{1, 2, 3}
```
通过`add(key)`方法可以添加元素到set中，可以重复添加，但不会有效果：
```Python
>>> s.add(4)
>>> s
{1, 2, 3, 4}
>>> s.add(4)
>>> s
{1, 2, 3, 4}
```
通过`remove(key)`方法可以删除元素：
```Python
>>> s.remove(4)
>>> s
{1, 2, 3}
```
set可以看成数学意义上的无序和无重复元素的集合，因此，两个set可以做数学意义上的交集、并集等操作：
```Python
>>> s1 = set([1, 2, 3])
>>> s2 = set([2, 3, 4])
>>> s1 & s2
{2, 3}
>>> s1 | s2
{1, 2, 3, 4}
```
set和dict的唯一区别仅在于没有存储对应的value，但是，set的原理和dict一样，所以，同样不可以放入可变对象，因为无法判断两个可变对象是否相等，也就无法保证set内部“不会有重复元素”。试试把list放入set，看看是否会报错。

### 再议不可变对象
-----
上面我们讲了，str是不变对象，而list是可变对象。

对于可变对象，比如list，对list进行操作，list内部的内容是会变化的，比如：
```Python
>>> a = ['c', 'b', 'a']
>>> a.sort()
>>> a
['a', 'b', 'c']
```
而对于不可变对象，比如str，对str进行操作呢：
```Python
>>> a = 'abc'
>>> a.replace('a', 'A')
'Abc'
>>> a
'abc'
```
虽然字符串有个`replace()`方法，也确实变出了`'Abc'`，但变量`a`最后仍是`'abc'`，应该怎么理解呢？

我们先把代码改成下面这样：
```Python
>>> a = 'abc'
>>> b = a.replace('a', 'A')
>>> b
'Abc'
>>> a
'abc'
```

要始终牢记的是，`a`是变量，而`'abc'`才是字符串对象！有些时候，我们经常说，对象`a`的内容是`'abc'`，但其实是指，`a`本身是一个变量，它指向的对象的内容才是`'abc'`：

![](file:///E:/github/md/a.PNG)

当我们调用`a.replace('a', 'A')`时，实际上调用方法`replace`是作用在字符串对象`'abc'`上的，而这个方法虽然名字叫`replace`，但却没有改变字符串`'abc'`的内容。相反，`replace`方法创建了一个新字符串`'Abc'`并返回，如果我们用变量`b`指向该新字符串，就容易理解了，变量`a`仍指向原有的字符串`'abc'`，但变量b却指向新字符串`'Abc'`了：

![](file:///E:/github/md/b.PNG)

所以，对于不变对象来说，调用对象自身的任意方法，也不会改变该对象自身的内容。相反，这些方法会创建新的对象并返回，这样，就保证了不可变对象本身永远是不可变的。

### 小结
------
使用key-value存储结构的dict在Python中非常有用，选择不可变对象作为key很重要，最常用的key是字符串。

tuple虽然是不变对象，但试试把`(1, 2, 3)`和`(1, [2, 3])`放入dict或set中，并解释结果。

前面一个可以，后面一个不可以
```Python
>>> d = {'a':(1,2,3)}
>>> d
{'a': (1, 2, 3)}
>>> d = {'b',(1,[2,3])}
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unhashable type: 'list'
>>> s = set((1,2,3))
>>> s
{1, 2, 3}
>>> s = set((1,[2,3]))
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unhashable type: 'list'
>>>
```
