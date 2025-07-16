
import random
# a = [1,2,3,4,1]
# a.remove(1)
# print(4 in a)

# #强烈建议用生成式语法来创建列表
# b = [ i for i in range(1,100) if i % 5 == 0 ]
# print(b)
# c = [ i**2 for i in b]
# print(c)
# d = [i for i in c if i>500]
# print(d)
# e = random.sample(d,5)
# print(e)
# e = random.choice(d)
# print(e)

# a, b, c = b, c, a

#1
# import string
# import random
# all_chars = string.digits + string.ascii_letters
# n = int(input())
# res = [random.choice(all_chars) for _ in range(n)]
# res = "".join(res)
# print(res)

#高级函数
# old_strings = ['in', 'apple', 'zoo', 'waxberry', 'pear']
# new_strings = sorted(old_strings, key=len)
# print(new_strings)  # ['in', 'zoo', 'pear', 'apple', 'waxberry']

#3偏函数
# import functools
# def a(a,b):
#     return a+b
# def b(a,b):
#     return a-b

# func = functools.partial(a,5)
# ans = func(1)
# print(ans)

#4
# import time
# import functools
# from functools import wraps
# from functools import lru_cache


# def record_time(func):

#     @wraps(func)
#     def wrapper(*args,**kwargs):
#         start = time.time()
#         result = func(*args,**kwargs)
#         end = time.time()
#         print(end-start)
#         return result
#     return wrapper

# @record_time
# def func():
#     time.sleep(1)
#     return 100

# @record_time
# def fib1(n):
#     if n in(1,2):
#         return 1
#     return fib1(n-1) + fib1(n-2)

# # @record_time
# @lru_cache
# def fib2(n):
#     if n in(1,2):
#         return 1
#     return fib2(n-1) + fib2(n-2)

#5
# class Father:
#     __slots__ = ("_name","__age")

#     def __init__(self,name,age):
#         self._name = name
#         self.__age = age

# son = Father("张三",18)
# print(son._name)
# print(son._Father__age)

# import random
# import enum

# #枚举类
# class Suite(Enum):
#     SPADE,HEART,CLUB,DIAMOND = range(4)

# class Card:
#     def __init__(self,suite,face):
#         self.suite = suite
#         self.face = face

#     def __repr__(self):
#         suites = '♠♥♣♦'
#         faces = ['', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
#         return f"{suites[self.suite]}{faces[self.face]}"
#     def __eq__(self,other):
#         return self.face == other.face
#     def __gt__(self,other):
#         return self.face > other.face
#     def __ge__(self,other):
#         return self.face >= other.face
#     def __lt__(self,other):
#         return self.face < other.face
#     def __le__(self,other):
#         return self.face <= other.face
#     def __ne__(self,other):
#         return self.face != other.face

# class Poker:
#     def __init__(self):
#         self.cards = [Card(suite,face) 
#         for suite in Suite 
#         for face in range(1,14)]
#         self.current = 0
    
#     def shuffle(self):
#         self.current = 0
#         random.shullf(sefl.card)

#     def deal(self):
#         card = self.cards[self.current]
#         self.current +=1
#         return card

#     @porperty
#     def has_next(self):
#         return self.current < len(self.cards)

# class Player:
#     def __init__(self,name):
#         self.name = name
#         self.cards = []
#     def __repr__(self):
#         return f"{self.name}：{self.cards}"
#     def get_card(self,card):
#         self.cards.append(card)
#     def arrange(self):
#         self.cards.sort()

# class InputError(ValueError):
#     """自定义异常类型"""
#     pass


# def fac(num):
#     """求阶乘"""
#     if num < 0:
#         raise InputError('只能计算非负整数的阶乘')
#     if num in (0, 1):
#         return 1
#     return num * fac(num - 1)
# flag = True
# while flag:
#     num = int(input('n = '))
#     try:
#         print(f'{num}! = {fac(num)}')
#         flag = False
#     except InputError as err:
#         print(err)

# class Test:
#     num1 = 0

#     def __init__(self):
#         self.num2 = 2
    
#     def c1(self):
#         print(self.num2)

#     def c2(self):
#         print(self.num1)
    
#     @staticmethod
#     def c3():
#         print("3")

# import json
# my_inf = {
#     "name":"王逸轩",
#     "age":18,
#     "gundam":{
#         "v":"牛",
#         "fa78":"全装甲"
#     }
# }
# str1 = json.dumps(my_inf)
# print(str1)
# try :
#     with open('data.json','w') as f:
#         json.dump(my_inf,f)
# except TypeError as e:
#     print(e)

# my_inf2 = json.loads(str1)

# 
import random
i =20
print(i)
for _ in range(i):
    print(random.randint(1,9))
