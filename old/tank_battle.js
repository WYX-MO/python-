// 初始化游戏变量
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// 游戏对象
const tank = {
  x: 400,
  y: 300,
  width: 40,
  height: 40,
  speed: 5,
  direction: 'up'
};

// 键盘控制
const keys = {
  ArrowUp: false,
  ArrowDown: false,
  ArrowLeft: false,
  ArrowRight: false
};

// 事件监听
window.addEventListener('keydown', (e) => {
  if (e.code in keys) {
    keys[e.code] = true;
  }
});

window.addEventListener('keyup', (e) => {
  if (e.code in keys) {
    keys[e.code] = false;
  }
});

// 游戏循环
function gameLoop() {
  update();
  draw();
  requestAnimationFrame(gameLoop);
}

// 更新游戏状态
function update() {
  if (keys.ArrowUp) {
    tank.y -= tank.speed;
    tank.direction = 'up';
  }
  if (keys.ArrowDown) {
    tank.y += tank.speed;
    tank.direction = 'down';
  }
  if (keys.ArrowLeft) {
    tank.x -= tank.speed;
    tank.direction = 'left';
  }
  if (keys.ArrowRight) {
    tank.x += tank.speed;
    tank.direction = 'right';
  }
}

// 绘制游戏
function draw() {
  // 清空画布
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // 绘制坦克
  ctx.fillStyle = 'green';
  ctx.fillRect(tank.x, tank.y, tank.width, tank.height);
}

// 启动游戏
gameLoop();