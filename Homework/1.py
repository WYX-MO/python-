import sys

studentsNum , addNum = map(int,sys.stdin.readline().split())
grads = list(map(int,sys.stdin.readline().split()))

diff = [0] * (studentsNum+2)
for _ in range(addNum):
    start,end,points = map(int,sys.stdin.readline().split())
    diff[start-1] += points
    diff[end] -= points

current = 0
for _ in range(studentsNum):
    current += diff[_]
    grads[_] += current

print (min(grads))
