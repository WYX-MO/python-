import speech_recognition as sr
import threading
import time
import sys

# 语音识别线程dd
r = sr.Recognizer()
while True:
    try:
        with sr.Microphone() as source:
            print("请说话...")
            audio = r.listen(source)
        # 使用 PocketSphinx 进行识别
        text = r.recognize_sphinx(audio)
        print(f"识别结果: {text}")
        sys.exit()
    except sr.UnknownValueError:
        print("无法识别语音")
    except sr.RequestError as e:
        print(f"请求错误; {e}")