import os
import random
import turtle

class Map:
    def __init__(self):
        self.map = [[0 for i in range(4)] for j in range(4)]
        self.size = 4
        self.score = 0
        self.game_over = False

    def init(self):
        self.map = [[0 for i in range(4)] for j in range(4)]
        self.score = 0
        self.game_over = False
        for i in range(2):
            self.map[random.randint(0, self.size - 1)][random.randint(0, self.size - 1)] = 2

    def add(self):
        while True:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self.map[x][y] == 0:
                self.map[x][y] = 2
                break
        print(' ')

    def is_game_over(self):
        # 检查是否还有空位
        for i in range(self.size):
            for j in range(self.size):
                if self.map[i][j] == 0:
                    return False

        # 检查相邻方块是否可以合并
        for i in range(self.size):
            for j in range(self.size):
                if i < self.size - 1 and self.map[i][j] == self.map[i + 1][j]:
                    return False
                if j < self.size - 1 and self.map[i][j] == self.map[i][j + 1]:
                    return False

        return True

    def move(self, direction=-1):
        # 保存移动前的地图状态
        old_map = [row[:] for row in self.map]

        # 0:上 1:下 2:左 3:右
        if direction == 0:
            for col in range(self.size):
                self._move_column(col, -1)
        elif direction == 1:
            for col in range(self.size):
                self._move_column(col, 1)
        elif direction == 2:
            for row in range(self.size):
                self._move_row(row, -1)
        elif direction == 3:
            for row in range(self.size):
                self._move_row(row, 1)

        # 检查地图是否有变化，如果有变化才添加新数字
        if old_map != self.map:
            self.add()

        # 检查游戏是否结束
        self.game_over = self.is_game_over()

    def _move_column(self, col, direction):
        if direction == -1:  # 向上移动
            start, end, step = 0, self.size, 1
        else:  # 向下移动
            start, end, step = self.size - 1, -1, -1

        for i in range(start, end, step):
            if self.map[i][col] != 0:
                k = i
                while (0 <= k + direction < self.size) if direction == 1 else (0 <= k + direction):
                    if self.map[k + direction][col] == 0:
                        self.map[k + direction][col] = self.map[k][col]
                        self.map[k][col] = 0
                    elif self.map[k + direction][col] == self.map[k][col]:
                        self.map[k + direction][col] *= 2
                        self.map[k][col] = 0
                        self.score += self.map[k + direction][col]
                        break
                    else:
                        break
                    k += direction

    def _move_row(self, row, direction):
        if direction == -1:  # 向左移动
            start, end, step = 0, self.size, 1
        else:  # 向右移动
            start, end, step = self.size - 1, -1, -1

        for j in range(start, end, step):
            if self.map[row][j] != 0:
                k = j
                while (0 <= k + direction < self.size) if direction == 1 else (0 <= k + direction):
                    if self.map[row][k + direction] == 0:
                        self.map[row][k + direction] = self.map[row][k]
                        self.map[row][k] = 0
                    elif self.map[row][k + direction] == self.map[row][k]:
                        self.map[row][k + direction] *= 2
                        self.map[row][k] = 0
                        self.score += self.map[row][k + direction]
                        break
                    else:
                        break
                    k += direction

class Turtle2048:
    def __init__(self):
        self.screen = turtle.Screen()
        self.screen.title("2048 Game")
        self.screen.setup(width=600, height=600)
        self.screen.bgcolor("beige")
        self.screen.tracer(0)  # 关闭屏幕更新
        # 设置颜色模式为 255
        self.screen.colormode(255)
        self.pen = turtle.Turtle()
        self.pen.speed(0)
        self.pen.hideturtle()
        self.game_map = Map()
        self.game_map.init()

    def draw_board(self):
        self.pen.clear()
        self.pen.penup()
        self.pen.goto(-200, 200)
        self.pen.color(0, 0, 0)  # 设置背景颜色为白色
        self.pen.write(f"2048 GAME      SCORE: {self.game_map.score}", font=("Arial", 24, "normal"))
        self.pen.goto(-200, 150)
        for i in range(self.game_map.size):
            for j in range(self.game_map.size):
                x = -200 + j * 100
                y = 150 - i * 100
                self.pen.penup()
                self.pen.goto(x, y)
                self.pen.pendown()
                self.pen.color(255 - (20*self.game_map.map[i][j])%255, 255 -(20*self.game_map.map[i][j])%255,0)  # 设置背景颜色为白色
                self.pen.begin_fill()

                # self.pen.goto(x+100, y+100)
                # self.pen.color(0, 0, 0)  # 设置背景颜色为白色
                # self.pen.write(str(self.game_map.map[i][j]), align="center", font=("Arial", 24, "normal"))

                for _ in range(4):
                    self.pen.forward(90)
                    self.pen.right(90)
                self.pen.end_fill()
                self.pen.penup()
                self.pen.goto(x + 50, y + 30)
                if self.game_map.map[i][j] != 0:
                    self.pen.goto(x+45, y-55)
                    self.pen.color(0, 0, 0)  
                    self.pen.write(str(self.game_map.map[i][j]), align="center", font=("Arial", 24, "normal")) 
        self.screen.update()  # 手动更新屏幕

    def operate(self, direction):
        self.game_map.move(direction)
        self.draw_board()
        if self.game_map.game_over:
            self.pen.penup()
            self.pen.goto(0, 0)
            self.pen.color(255, 0, 0)
            self.pen.write("游戏结束!", align="center", font=("Arial", 36, "normal"))
            self.screen.update()

    def main(self):
        self.draw_board()
        self.screen.listen()
        self.screen.onkeypress(lambda: self.operate(0), "Up")
        self.screen.onkeypress(lambda: self.operate(1), "Down")
        self.screen.onkeypress(lambda: self.operate(2), "Left")
        self.screen.onkeypress(lambda: self.operate(3), "Right")
        self.screen.mainloop()

if __name__ == "__main__":
    game = Turtle2048()
    game.main()