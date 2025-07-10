import tkinter as tk
import cv2
from PIL import Image, ImageDraw, ImageFont


def save_input_as_image():
    text = entry.get()
    # 创建一个 32x32 的灰度图像
    image = Image.new('L', (32, 32), color=255)
    draw = ImageDraw.Draw(image)
    # 加载字体，你可以根据需要修改字体和大小
    font = ImageFont.load_default()
    draw.text((10, 10), text, fill=0, font=font)
    # 指定保存路径，你可以修改为自己的路径
    save_path = 'output_image.png'
    image.save(save_path)
    print(f"图片已保存到 {save_path}")


# 创建主窗口
root = tk.Tk()
root.title("输入文本并保存为图片")

# 创建输入框
entry = tk.Entry(root, width=30)
entry.pack(pady=20)
# 绑定回车键事件
entry.bind("<Return>", lambda event: save_input_as_image())

# 创建按钮
button = tk.Button(root, text="保存为图片", command=save_input_as_image)
button.pack(pady=10)

# 运行主循环
root.mainloop()
    