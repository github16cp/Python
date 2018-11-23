# 《Python编程：从入门到实践》

<!-- GFM-TOC -->
* [一、变量和简单数据类型](#一、变量和简单数据类型)
    * [变量](#变量)
    * [字符串](#字符串)
    * [数字](#数字)
    * [注释](#注释)
* [二、列表简介](#二、列表简介)

<!-- GFM-TOC -->

# 一、变量和简单数据类型

python程序在运行时，`编辑器`将使用Python`解释器`来运行它。Python解释器读取整个程序，确定其中每个单词的含义。

`编辑器`的语法突出功能在编写程序时也很有帮助
## 变量
每个变量都存储了一个值（与变量相关联的信息），解释器将值与变量关联起来。程序中可以随时修改变量的值，而Python将始终记录变量的最新值。
### 变量的命名与使用
* 变量名只能包含`字母`、`数字`和`下划线`。变量名可以用字母或者下划线打头，但不能以数字打头。
* 变量名不能包含空格。
* Python的关键字和函数名不能用作变量名。
* 变量名应该具有描述性。

应该使用`小写的变量名`。

程序无法运行成功时，解释器会提供一个`traceback`，`traceback`是一条记录，指出了在什么地方陷入了困境。给出出错的代码行，并且列出了出错的代码，还指出了是什么样的错误。

## 字符串
用引号引起的都是字符串，引号可以是`单引号`，也可以是`双引号`。
### 修改字符串的大小写
```Python
name = "ada lovelace" 
print(name.title()) 
```
方法`title()`出现在变量的后面，方法是Python对数据执行的操作。

`title()`以首字母大写的方式显示每个单词。

`upper()`以大写的方式显示单词每个字母。

`lower()`以小写的方式显示单词每个字母。

很多时候，你无法依靠用户来提供正确的大小写，因此
需要将字符串先转换为小写，再存储它们。以后需要显示这些信息时，再将其转换为最合适的大
小写方式。

### 拼接字符串
```Python
first_name = "ada" 
last_name = "lovelace" 
full_name = first_name + " " + last_name 
```
Python使用加号（+）来合并字符串，这种合并字符串的方法称为拼接。

### 使用制表符或换行符来添加空白
在编程中，空白泛指任何非打印字符，如`空格`、`制表符`和`换行符`。你可使用空白来组织输出，以使其更易读。
```Python
message = "\tprint"
```
```Python
        print
```
制表符：`\t`

换行符：`\n`
### 删除空白
Python能够找出字符串开头和末尾多余的空白。要确保字符串末尾没有空白，可使用方法`rstrip()`。

`rstrip()`：删除字符串末尾的空白。

`lstrip()`：删除字符串开头的空白。

`strip()`：删除字符串两端的空白。

### 语法错误
用单引号括起的字符串中，如果包含撇号，就将导致错误。

如果是双引号中包含撇号，没有错误。

### Python 2 中的 print 语句
在Python 2中，无需将要打印的内容放在括号内。从技术上说，Python 3中的`print是一个函数`，因此括号必不可少。

## 数字
整数使用起来最简单
### 整数

在Python中，可对整数执行加（+）减（-）乘（*）除（/）运算。

Python使用**两个乘号**表示乘方运算。

可以使用括号来修改运算次序，让Python按你指定的次序执行运算。

### 浮点数
Python将带小数点的数字都称为`浮点数`。

Python计算`结果`包含的小数位数可能是不确定的。
```Python
>>> 0.2 + 0.1
0.30000000000000004 
>>> 3 * 0.1
0.30000000000000004 
```

### 使用函数 `str()`避免类型错误

类型错误，需要显示的指出将整数用作字符串。
```Python
str(123)
```
### Python 2 中的整数
```Python
>>> python2.7
>>> 3 / 2
1 
```
Python返回的结果为1，而不是1.5。在Python 2中，整数除法的结果只包含整数部分，小数部分被删除。在Python 2中，若要避免这种情况，务必确保至少有一个操作数为浮点数，这样结果也将为浮点数。

## 注释
在Python中，注释用井号（#）标识，井号后面的内容都会被Python解释器忽略。

要成为专业程序员或与其他程序员合作，就必须编写有意义的注释。

如果不确定是否要编写注释，就问问自己，找到合理的解决方案前，是否考虑了多个解决方案。如果答案是肯定的，就编写注释对你的解决方案进行说明吧。

## Python之禅
```Python
import this 
```
```
The Zen of Python, by Tim Peters

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
```

# 二、列表简介

书本32页