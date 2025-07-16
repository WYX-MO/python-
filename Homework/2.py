# '''
# 5
# 1
# 2
# 3
# 4
# 1
# '''
# import sys 
# def longest(nums):
#     if not nums:
#         return 0
#     current_max = 1
#     global_max = 1
#     for i in range(1, len(nums)):
#         if nums[i] == nums[i - 1]:
#             current_max += 1
#         else:
#             current_max = 1
#         if current_max > global_max:
#             global_max = current_max
#     return global_max
# cowNum = int(sys.stdin.readline().strip())
# cow = []
# diff = []
# current  = 0
# max =0
# flag =1
# tag =0
# for _ in range(cowNum):
#     cow.append(int(sys.stdin.readline().strip()))
# for _ in range(cowNum-1):
#     # print(cow[_-1] ,cow[_],cow[_+1])
#     if cow[_] <= cow[_+1]:
#         if tag == 0:
#             if cow[_] == cow[_+1]:
#                 diff.append(0)
#             else:
#                 tag =1
#                 diff.append(flag)
#         else:
#             diff.append(flag)
#     else:

#         if tag == 1:
#             tag =0
#             diff.append(flag)
#         else:
#             diff.append(0)
#         flag +=1

#         t = _
#         while(diff[t]!=0):
#             if cow[t]==cow[t-1]:
#                 diff[t]=0
#                 t-=1
#             else:
#                 break

# if cow[-1]>cow[-2]:
#     diff.append(flag)
# else:
#     diff.append(0)

# print(diff)



# max = longest(diff)
# print(max if max !=1 else 0)

import sys

cowNum = int(sys.stdin.readline().strip())
cow = []
for _ in range(cowNum):
    cow.append(int(sys.stdin.readline().strip()))

rindex = maxIndex()