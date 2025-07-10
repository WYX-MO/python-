
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
class Father:
    __slots__ = ("_name","__age")
    
    def __init__(self,name,age):
        self._name = name
        self.__age = age

son = Father("张三",18)
print(son._name)
print(son._Father__age)