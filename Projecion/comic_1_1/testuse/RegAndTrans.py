import cv2
import numpy as np
import pytesseract
import requests
import json
from PIL import Image
import os
from dotenv import load_dotenv  # 新增：用于加载环境变量
# 配置路径
image_path = r"E:\pyLearn\imgs\comic\\1 (3).png"
tesseract_path = r"E:\pyLearn\reses\tesseract.exe"

# 设置Tesseract路径
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# 加载环境变量（如果有）
load_dotenv()
DEEPSEEK_API_KEY = "sk-2b814ccebc6e4d90b76ef40d2dd36f83"  # 替换为新的API密钥
DEEPSEEK_API_URL = "https://api.deepseek.com/v1"

class DeepSeekAPI:
    """DeepSeek API调用客户端"""
    
    def __init__(self, api_key=None, api_base=None, timeout=30):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.api_base = api_base or "https://api.deepseek.com/v1"
        self.timeout = timeout
        
        if not self.api_key:
            raise ValueError("API密钥未设置，请通过环境变量或构造函数传入")
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_text(self, messages, model="deepseek-chat", max_tokens=1024, temperature=0.7):
        """调用DeepSeek文本生成API（用于翻译）"""
        endpoint = f"{self.api_base}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"success": True, "content": content, "raw_data": data}
        except Exception as e:
            return {"success": False, "error": f"API调用失败: {str(e)}"}

class RegAndTranser:
    def __init__(self, image_path):
        self.image_path = image_path

    def show(self, image):
        cv2.imshow("Image", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def detect_text_boxes(self):
        """使用OpenCV检测图像中的文本框"""
        image = cv2.imread(self.image_path)
        image_o = image.copy()
        if image is None:
            raise ValueError("无法加载图像，请检查路径是否正确")
        self.show(image)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # 灰度化
        ret, thresh = cv2.threshold(gray, 125, 255, cv2.THRESH_BINARY)
        self.show(thresh)  # 二值化
        kernel = np.ones((5, 5), np.uint8)
        img = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        self.show(img)  # 开
        # img = cv2.bitwise_not(img)
        img = img.astype(np.uint8)
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)  # 找轮廓
        text_boxes = []
        image_ = img.copy()
        cv2.drawContours(image_, contours, -1, (0, 255, 0), 2)
        open2 = cv2.morphologyEx(image_, cv2.MORPH_OPEN, kernel)
        self.show(open2)

        timg = image_.copy()
        # timg = cv2.bitwise_not(timg)
        timg = cv2.cvtColor(timg, cv2.COLOR_GRAY2BGR)

        contours, _ = cv2.findContours(open2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(timg, contours, -1, (0, 255, 0), 2)

        self.show(timg)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # ret,thresh = cv2.threshold(image,125,255,cv2.THRESH_BINARY)
        cnts = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = w / float(h)
            if (0.2 < aspect_ratio < 1) and (w * h > 0):
                cnts.append(cnt)
        contours = cnts
        merged_contours = []
        i = 0
        while i < len(contours) - 1:
            x, y, w, h = cv2.boundingRect(contours[i])
            x_next, y_next, w_next, h_next = cv2.boundingRect(contours[i + 1])
            print("test1:" + str(x) + " " + str(y) + " " + str(w) + " " + str(h) + " | " + str(x_next) + " " + str(y_next) + " " + str(w_next) + " " + str(h_next))
            # 判断是否应该合并
            if abs(y_next - y) < 10 and abs(x_next - (x - w_next)) < 10 and abs(h_next - h) < 10:
                print("ok")
                # 计算合并后的边界框
                x_merged = min(x, x_next)
                y_merged = min(y, y_next)
                w_merged = max(x + w, x_next + w_next) - x_merged
                h_merged = max(y + h, y_next + h_next) - y_merged

                # 检查是否还能与下一个轮廓合并
                merged = True
                j = i + 2
                while j < len(contours):
                    x_j, y_j, w_j, h_j = cv2.boundingRect(contours[j])
                    if abs(y_j - y_merged) < 10 and abs(x_j - (x_merged + w_merged)) < 10 and abs(h_j - h_merged) < 10:
                        x_merged = min(x_merged, x_j)
                        y_merged = min(y_merged, y_j)
                        w_merged = max(x_merged + w_merged, x_j + w_j) - x_merged
                        h_merged = max(y_merged + h_merged, y_j + h_j) - y_merged
                        j += 1
                    else:
                        break

                merged_contours.append((x_merged, y_merged, w_merged, h_merged))
                cv2.rectangle(image, (x_merged, y_merged), (x_merged + w_merged, y_merged + h_merged), (255, 0, 0), 2)
                self.show(image)
                i = j  # 跳过所有已合并的轮廓
            else:
                merged_contours.append((x, y, w, h))
                i += 1

        # 处理最后一个轮廓
        if i < len(contours):
            x, y, w, h = cv2.boundingRect(contours[i])
            merged_contours.append((x, y, w, h))

        # 过滤和绘制合并后的边界框
        for x, y, w, h in merged_contours:
            aspect_ratio = w / float(h)
            if (0.2 < aspect_ratio < 10) and (w * h > 10000):
                text_boxes.append((x, y, w, h))
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                self.show(image)

        return image_o, image, text_boxes

    def extract_text_from_boxes(self, image, boxes):
        """从检测到的文本框中提取文本"""
        extracted_texts = []
        for i, (x, y, w, h) in enumerate(boxes):
            box_image = image[y:y + h, x:x + w]
            pil_img = Image.fromarray(cv2.cvtColor(box_image, cv2.COLOR_BGR2RGB))
            self.show(box_image)
            text = pytesseract.image_to_string(pil_img, lang='jpn_vert')

            if text.strip():
                extracted_texts.append({
                    'box': (x, y, w, h),
                    'text': text.strip()
                })
        return extracted_texts

    def translate_with_deepseek(self, text, source_lang='ja', target_lang='zh'):
        """使用DeepSeek API的聊天接口进行翻译（通过提示词指定翻译任务）"""
        if not text:
            return None

        # 构建翻译提示词（明确要求从源语言翻译到目标语言）
        system_prompt = {
            "role": "system",
            "content": f"你是一个专业的翻译工具，将{source_lang}翻译为{target_lang}，要求准确、流畅。"
        }
        user_prompt = {
            "role": "user",
            "content": text
        }

        # 初始化API客户端
        api = DeepSeekAPI(api_key=DEEPSEEK_API_KEY)
        # 调用生成接口（使用聊天模型）
        response = api.generate_text(messages=[system_prompt, user_prompt])

        if response["success"]:
            return response["content"].strip()
        else:
            print(f"翻译错误: {response.get('error', '未知错误')}")
            return None

    def process(self):
        # 1. 检测文本框
        image_o, image, text_boxes = self.detect_text_boxes()
        print(f"检测到 {len(text_boxes)} 个文本框")
        # 2. 提取文本
        for cnt in text_boxes:
            x, y, w, h = cnt
            img = image_o[y:y + h, x:x + w]
            self.show(img)

        extracted_texts = self.extract_text_from_boxes(image_o, text_boxes)

        if not extracted_texts:
            print("没有检测到可识别的文本")
            return

        print("检测到的文本:")
        for item in extracted_texts:
            # 3. 翻译文本（使用新的API调用方式）
            original_text = item['text']
            translated_text = self.translate_with_deepseek(original_text)

            print(f"\n原始文本(日语):\n{original_text}")
            print(f"\n翻译文本(中文):\n{translated_text if translated_text else '翻译失败'}")

            # 在图像上绘制文本框和翻译结果
            x, y, w, h = item['box']
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if translated_text:
                # 处理长文本换行
                translated_lines = [translated_text[i:i + 20] for i in range(0, len(translated_text), 20)]
                for i, line in enumerate(translated_lines):
                    cv2.putText(image, line, (x, y + h + 20 + i * 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # 保存结果图像
        output_path = self.image_path.replace('.png', '_result.png')
        cv2.imwrite(output_path, image)
        self.show(image)
        print(f"\n结果已保存到: {output_path}")

if __name__ == "__main__":
    RAT = RegAndTranser(image_path)
    RAT.process()