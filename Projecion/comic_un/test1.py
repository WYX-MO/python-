# program1.py（改进版）
import sys
import os
import subprocess
from pathlib import Path

def calculate():
    result = 1 + 1
    return result

def call_program2(result):
    # 调用程序2并传递结果
    path = os.path.abspath(__file__)
    path = path.rsplit('\\', 1)[0]+"\\test2.py"
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到程序2: {path}")
    cmd = [
        "python",
        path,
        str(result)
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
    else:
        print(result.stdout)

if __name__ == "__main__":
    result = calculate()
    call_program2(result)  # 直接调用程序2