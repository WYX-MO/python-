import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import cv2
import matplotlib.pyplot as plt
import re
from collections import defaultdict

# 1. 数据预处理与加载
class MathExprDataset(Dataset):
    def __init__(self, data, transform=None):
        self.data = data  # 存储数据集
        self.transform = transform  # 存储图像转换函数
        
    def __len__(self):
        """返回数据集的长度。"""
        return len(self.data)
    
    def __getitem__(self, idx):
        """
        根据索引获取数据集中的图像和标签。

        参数:
        idx (int): 数据索引。

        返回:
        tuple: 包含图像和标签的元组。
        """
        img_path, label = self.data[idx]  # 获取图像路径和标签
        # 以灰度模式读取图像
        image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        
        if self.transform:  # 如果存在转换函数
            image = self.transform(image)  # 应用转换函数
            
        return image, label

# 2. 符号识别模型 - 基于CNN
class SymbolRecognizer(nn.Module):
    def __init__(self, num_classes=82):  # 82种常见数学符号
        super(SymbolRecognizer, self).__init__()
        # 第一个卷积层，输入通道数为1，输出通道数为32，卷积核大小为3x3
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3)
        # 第二个卷积层，输入通道数为32，输出通道数为64，卷积核大小为3x3
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3)
        # 最大池化层，池化窗口大小为2x2，步长为2
        self.pool = nn.MaxPool2d(2, 2)
        # 第一个Dropout层，丢弃率为0.25
        self.dropout1 = nn.Dropout(0.25)
        # 第一个全连接层，输入特征数为64 * 5 * 5，输出特征数为128
        self.fc1 = nn.Linear(64 * 5 * 5, 128)
        # 第二个Dropout层，丢弃率为0.5
        self.dropout2 = nn.Dropout(0.5)
        # 第二个全连接层，输入特征数为128，输出特征数为分类类别数
        self.fc2 = nn.Linear(128, num_classes)
        
    def forward(self, x):
        """
        前向传播方法。

        参数:
        x (torch.Tensor): 输入张量。

        返回:
        torch.Tensor: 输出张量。
        """
        x = self.pool(F.relu(self.conv1(x)))  # 第一个卷积层 + ReLU激活 + 最大池化
        x = self.pool(F.relu(self.conv2(x)))  # 第二个卷积层 + ReLU激活 + 最大池化
        x = self.dropout1(x.view(-1, 64 * 5 * 5))  # 将张量展平并应用Dropout
        x = F.relu(self.fc1(x))  # 第一个全连接层 + ReLU激活
        x = self.dropout2(x)  # 应用Dropout
        x = self.fc2(x)  # 第二个全连接层
        return x

# 3. 公式结构分析模型 - 基于注意力机制的序列到序列模型
class FormulaParser(nn.Module):
    """
    基于注意力机制的序列到序列模型，用于公式结构分析。

    参数:
    input_size (int): 输入特征的大小。
    hidden_size (int): 隐藏层的大小。
    output_size (int): 输出的大小。
    """
    def __init__(self, input_size, hidden_size, output_size):
        super(FormulaParser, self).__init__()
        self.hidden_size = hidden_size  # 存储隐藏层大小
        
        # 双向GRU编码器，输入大小为input_size，隐藏层大小为hidden_size
        self.encoder = nn.GRU(input_size, hidden_size, bidirectional=True)
        # 单向GRU解码器，输入大小为hidden_size*2，隐藏层大小为hidden_size
        self.decoder = nn.GRU(hidden_size*2, hidden_size)
        # 注意力层，输入大小为hidden_size*3，输出大小为1
        self.attention = nn.Linear(hidden_size*3, 1)
        # 输出层，输入大小为hidden_size，输出大小为output_size
        self.out = nn.Linear(hidden_size, output_size)
        # 对数Softmax层，用于输出概率分布
        self.softmax = nn.LogSoftmax(dim=1)
        
    def forward(self, input, hidden):
        """
        前向传播方法。

        参数:
        input (torch.Tensor): 输入张量。
        hidden (torch.Tensor): 隐藏状态张量。

        返回:
        list: 包含输出张量的列表。
        """
        # 编码器处理输入符号特征序列
        encoder_outputs, encoder_hidden = self.encoder(input, hidden)
        
        # 解码器初始化
        decoder_input = torch.zeros(1, 1, self.hidden_size*2)
        decoder_hidden = encoder_hidden[-1].unsqueeze(0)
        
        # 注意力机制的解码过程
        outputs = []
        for i in range(MAX_LENGTH):  # MAX_LENGTH未定义，可能需要全局定义
            # 计算注意力权重
            attn_weights = torch.zeros(encoder_outputs.size(0))
            for j in range(encoder_outputs.size(0)):
                attn_weights[j] = self.attention(torch.cat((decoder_hidden[0], 
                                                             encoder_outputs[j]), 1))
            attn_weights = F.softmax(attn_weights, dim=0)
            
            # 应用注意力权重
            context = torch.zeros(1, self.hidden_size*2)
            for j in range(encoder_outputs.size(0)):
                context += attn_weights[j] * encoder_outputs[j]
            
            # 解码器一步
            decoder_output, decoder_hidden = self.decoder(
                torch.cat((decoder_input, context.unsqueeze(0)), 2), 
                decoder_hidden
            )
            
            # 预测输出符号
            output = self.softmax(self.out(decoder_output[0]))
            outputs.append(output)
            
            # 准备下一个输入
            topv, topi = output.topk(1)
            if topi.item() == EOS_TOKEN:  # EOS_TOKEN表示序列结束，未定义，可能需要全局定义
                break
            decoder_input = output.detach()
            
        return outputs

# 4. 连笔处理模块
def process_cursive_writing(image):
    """
    处理手写连笔的特殊方法。

    参数:
    image (numpy.ndarray): 输入的灰度图像。

    返回:
    list: 包含分割后符号区域的边界框列表。
    """
    # 1. 使用形态学操作分割粘连符号
    # 创建3x3的矩形结构元素
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # 进行开运算，先腐蚀后膨胀，去除小的噪声和粘连
    opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # 2. 基于笔画宽度分析进行分割
    # 计算距离变换，得到每个像素到最近背景像素的距离
    dist_transform = cv2.distanceTransform(opened, cv2.DIST_L2, 5)
    # 阈值处理，将距离大于0.7倍最大距离的像素设为前景
    _, sure_fg = cv2.threshold(dist_transform, 0.7*dist_transform.max(), 255, 0)
    
    # 3. 应用分水岭算法
    sure_fg = np.uint8(sure_fg)  # 将前景图像转换为uint8类型
    # 计算未知区域，即开运算结果减去确定的前景
    unknown = cv2.subtract(opened, sure_fg)
    # 计算连通组件，得到每个连通区域的标签
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1  # 标签加1，背景标签为1
    markers[unknown == 255] = 0  # 未知区域标签设为0
    # 应用分水岭算法，对彩色图像进行分割
    markers = cv2.watershed(cv2.cvtColor(image, cv2.COLOR_GRAY2BGR), markers)
    
    # 4. 提取分割后的符号区域
    symbol_regions = []
    for label in np.unique(markers):
        if label == 0 or label == 1:  # 跳过背景和未知区域
            continue
        mask = np.zeros(markers.shape, dtype=np.uint8)
        mask[markers == label] = 255  # 创建当前标签的掩码
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            # 计算轮廓的边界框
            x, y, w, h = cv2.boundingRect(cnt)
            symbol_regions.append((x, y, w, h))
    
    return symbol_regions

# 5. 数学表达式解析器 - 处理运算优先级
class MathExpressionParser:
    """
    数学表达式解析器，用于处理运算优先级，将中缀表达式转换为后缀表达式并转换为LaTeX格式。
    """
    def __init__(self):
        # 定义运算符优先级
        self.operator_precedence = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2,
            '^': 3,
        }
        
    def infix_to_postfix(self, tokens):
        """
        将中缀表达式转换为后缀表达式(逆波兰表示法)。

        参数:
        tokens (list): 中缀表达式的令牌列表。

        返回:
        list: 后缀表达式的令牌列表。
        """
        output = []  # 存储输出的后缀表达式
        stack = []  # 存储运算符的栈
        
        for token in tokens:
            if token in self.operator_precedence:  # 如果是运算符
                # 处理运算符优先级
                while (stack and stack[-1] != '(' and 
                       self.operator_precedence[stack[-1]] >= self.operator_precedence[token]):
                    output.append(stack.pop())  # 弹出栈顶运算符到输出列表
                stack.append(token)  # 当前运算符入栈
            elif token == '(':  # 如果是左括号
                stack.append(token)  # 左括号入栈
            elif token == ')':  # 如果是右括号
                # 弹出直到遇到左括号
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # 弹出左括号
            else:  # 如果是操作数
                # 操作数直接输出
                output.append(token)
        
        # 弹出剩余的运算符
        while stack:
            output.append(stack.pop())
            
        return output
    
    def postfix_to_latex(self, postfix_tokens):
        """
        将后缀表达式转换为LaTeX格式。

        参数:
        postfix_tokens (list): 后缀表达式的令牌列表。

        返回:
        str: LaTeX格式的表达式。
        """
        stack = []  # 存储中间结果的栈
        
        for token in postfix_tokens:
            if token in self.operator_precedence:  # 如果是运算符
                # 处理运算符
                b = stack.pop()  # 弹出第二个操作数
                a = stack.pop()  # 弹出第一个操作数
                
                if token == '+':
                    result = f"{a} + {b}"
                elif token == '-':
                    result = f"{a} - {b}"
                elif token == '*':
                    result = f"{a} \\times {b}"
                elif token == '/':
                    result = f"\\frac{{{a}}}{{{b}}}"
                elif token == '^':
                    result = f"{a}^{{{b}}}"
                
                stack.append(result)  # 将结果入栈
            else:  # 如果是操作数
                # 操作数直接入栈
                stack.append(token)
        
        return stack[0]  # 返回最终结果

# 6. 完整的识别流程
def recognize_math_expression(image_path):
    """
    完整的数学表达式识别流程。

    参数:
    image_path (str): 输入图像的路径。

    返回:
    str: 识别结果的LaTeX格式表达式。
    """
    # 加载图像
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # 预处理
    processed_image = preprocess_image(image)
    
    # 处理连笔，分割符号
    symbol_regions = process_cursive_writing(processed_image)
    
    # 提取并识别每个符号
    recognized_symbols = []
    for region in symbol_regions:
        x, y, w, h = region
        symbol_img = processed_image[y:y+h, x:x+w]  # 提取符号图像
        symbol_img = resize_and_normalize(symbol_img)  # 调整大小并归一化
        
        # 使用符号识别模型预测
        with torch.no_grad():
            # 将图像转换为模型输入张量
            input_tensor = torch.from_numpy(symbol_img).unsqueeze(0).unsqueeze(0).float()
            output = symbol_recognizer(input_tensor)  # 模型预测
            _, predicted = torch.max(output, 1)  # 获取预测结果的索引
            symbol = symbol_dict[predicted.item()]  # 根据索引获取符号
            
        recognized_symbols.append({
            'symbol': symbol,
            'position': (x, y, w, h)
        })
    
    # 分析符号之间的空间关系
    structured_tokens = analyze_structure(recognized_symbols)
    
    # 使用数学表达式解析器处理优先级
    parser = MathExpressionParser()
    postfix_tokens = parser.infix_to_postfix(structured_tokens)
    latex_expression = parser.postfix_to_latex(postfix_tokens)
    
    return latex_expression

# 辅助函数
def preprocess_image(image):
    """
    图像预处理：二值化、降噪、归一化。

    参数:
    image (numpy.ndarray): 输入的灰度图像。

    返回:
    numpy.ndarray: 预处理后的图像。
    """
    # 二值化，使用Otsu's方法自动确定阈值
    _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # 降噪，使用开运算去除小的噪声
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # 归一化大小，将图像调整为256x64
    resized = cv2.resize(opening, (256, 64))
    
    return resized

def resize_and_normalize(image):
    """
    调整符号图像大小并归一化。

    参数:
    image (numpy.ndarray): 输入的符号图像。

    返回:
    numpy.ndarray: 调整大小并归一化后的图像。
    """
    image = cv2.resize(image, (28, 28))  # 调整图像大小为28x28
    image = image / 255.0  # 归一化像素值到[0, 1]
    return image

def analyze_structure(symbols):
    """
    分析符号间的结构关系，确定二维布局。

    参数:
    symbols (list): 包含符号和位置信息的字典列表。

    返回:
    list: 按结构关系排序的符号列表。
    """
    # 这里需要实现复杂的布局分析算法
    # 简化版本：按x坐标排序
    symbols.sort(key=lambda x: x['position'][0])
    return [s['symbol'] for s in symbols]

# 初始化模型
symbol_recognizer = SymbolRecognizer()
# 公式解析器，输入大小为128，隐藏层大小为128，输出大小为50个LaTeX符号
formula_parser = FormulaParser(input_size=128, hidden_size=128, output_size=50)  
# 符号字典，将索引映射到对应的符号
symbol_dict = {i: c for i, c in enumerate('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+-*/=()[]{}^_.,:;')}

# 示例调用
if __name__ == "__main__":
    latex_formula = recognize_math_expression("handwritten_formula.jpg")
    print(f"识别结果: {latex_formula}")