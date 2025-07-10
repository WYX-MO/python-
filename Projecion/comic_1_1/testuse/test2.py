# program2.py
import sys

def print_result(result):
    print(f"计算结果是: {result}")

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("请提供计算结果作为参数")
        sys.exit(1)
    
    result = sys.argv[1]  # 获取程序1的结果
    print_result(result)