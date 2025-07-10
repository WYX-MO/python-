# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.optimize import curve_fit

# # 奇数行数据列表
# odd_list = [11.350, 11.45, 11.55, 11.65, 11.75, 11.85, 11.95, 12.05, 12.15, 12.25, 12.35, 12.45, 12.55, 12.65, 12.75, 12.85, 12.95, 13.05, 13.15, 13.25, 13.35, 13.45, 13.55, 13.65, 13.75, 13.85, 13.95, 14.05, 14.15, 14.25, 14.35, 14.45, 14.55, 14.65, 14.75, 14.85, 14.95, 15.05, 15.15, 15.25, 15.35, 15.45, 15.55, 15.65, 15.75, 15.85, 15.95, 16.05, 16.15, 16.25]
# # 偶数行数据列表
# even_list = [0.075, 0.070, 0.100, 0.133, 0.152, 0.173, 0.200, 0.195, 0.174, 0.152, 0.130, 0.110, 0.107, 0.134, 0.256, 0.430, 0.663, 0.970, 1.350, 1.760, 2.160, 2.580, 3.150, 3.500, 3.640, 3.630, 3.540, 3.375, 3.100, 2.715, 2.285, 1.836, 1.379, 0.970, 0.636, 0.398, 0.228, 0.133, 0.103, 0.114, 0.134, 0.161, 0.194, 0.214, 0.245, 0.198, 0.162, 0.137, 0.118, 0.071]

# # 生成对应的 x 轴数据，这里简单以索引作为 x 值
# x_odd = np.arange(len(odd_list))
# x_even = np.arange(len(even_list))

# # 定义线性函数
# def linear(x, a, b):
#     return a * x + b

# # 定义二次函数
# def quadratic(x, a, b, c):
#     return a * x ** 2 + b * x + c

# # 对奇数行数据进行线性拟合
# popt_odd_linear, _ = curve_fit(linear, x_odd, odd_list)
# y_odd_linear = linear(x_odd, *popt_odd_linear)

# # 对奇数行数据进行二次拟合
# popt_odd_quadratic, _ = curve_fit(quadratic, x_odd, odd_list)
# y_odd_quadratic = quadratic(x_odd, *popt_odd_quadratic)

# # 对偶数行数据进行线性拟合
# popt_even_linear, _ = curve_fit(linear, x_even, even_list)
# y_even_linear = linear(x_even, *popt_even_linear)

# # 对偶数行数据进行二次拟合
# popt_even_quadratic, _ = curve_fit(quadratic, x_even, even_list)
# y_even_quadratic = quadratic(x_even, *popt_even_quadratic)

# # 绘制图形
# plt.figure(figsize=(12, 6))

# # 绘制奇数行数据及拟合曲线
# plt.subplot(1, 2, 1)
# plt.scatter(x_odd, odd_list, label='奇数行原始数据', color='blue')
# #plt.plot(x_odd, y_odd_linear, label='奇数行线性拟合', color='red', linestyle='--')
# #plt.plot(x_odd, y_odd_quadratic, label='奇数行二次拟合', color='green', linestyle='-.')
# plt.title('奇数行数据拟合')
# plt.xlabel('索引')
# plt.ylabel('值')
# plt.legend()

# # 绘制偶数行数据及拟合曲线
# plt.subplot(1, 2, 2)
# plt.scatter(x_even, even_list, label='偶数行原始数据', color='blue')
# #plt.plot(x_even, y_even_linear, label='偶数行线性拟合', color='red', linestyle='--')
# #plt.plot(x_even, y_even_quadratic, label='偶数行二次拟合', color='green', linestyle='-.')
# plt.title('偶数行数据拟合')
# plt.xlabel('索引')
# plt.ylabel('值')
# plt.legend()

# plt.tight_layout()
# plt.show()
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from scipy.interpolate import make_interp_spline

# 设置 matplotlib 支持中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

def moving_average(x, y, window_size=3):
    """使用移动平均进行平滑处理"""
    if window_size % 2 == 0:
        window_size += 1  # 确保窗口大小为奇数
    y_smooth = np.convolve(y, np.ones(window_size)/window_size, mode='same')
    return x, y_smooth

def savitzky_golay(x, y, window_length=5, polyorder=3):
    """使用 Savitzky-Golay 滤波器进行平滑处理"""
    if window_length % 2 == 0:
        window_length += 1  # 确保窗口长度为奇数
    y_smooth = savgol_filter(y, window_length, polyorder)
    return x, y_smooth

def spline_interpolation(x, y, smooth_factor=3):
    """使用样条插值进行平滑处理"""
    x_smooth = np.linspace(min(x), max(x), len(x) * smooth_factor)
    spl = make_interp_spline(x, y, k=3)  # 三次样条
    y_smooth = spl(x_smooth)
    return x_smooth, y_smooth

def main():
    # 使用之前的奇数行和偶数行数据
    odd_list = [11.350, 11.45, 11.55, 11.65, 11.75, 11.85, 11.95, 12.05, 12.15, 12.25, 12.35, 12.45, 12.55, 12.65, 12.75, 12.85, 12.95, 13.05, 13.15, 13.25, 13.35, 13.45, 13.55, 13.65, 13.75, 13.85, 13.95, 14.05, 14.15, 14.25, 14.35, 14.45, 14.55, 14.65, 14.75, 14.85, 14.95, 15.05, 15.15, 15.25, 15.35, 15.45, 15.55, 15.65, 15.75, 15.85, 15.95, 16.05, 16.15, 16.25]
    even_list = [0.075, 0.070, 0.100, 0.133, 0.152, 0.173, 0.200, 0.195, 0.174, 0.152, 0.130, 0.110, 0.107, 0.134, 0.256, 0.430, 0.663, 0.970, 1.350, 1.760, 2.160, 2.580, 3.150, 3.500, 3.640, 3.630, 3.540, 3.375, 3.100, 2.715, 2.285, 1.836, 1.379, 0.970, 0.636, 0.398, 0.228, 0.133, 0.103, 0.114, 0.134, 0.161, 0.194, 0.214, 0.245, 0.198, 0.162, 0.137, 0.118, 0.071]
    
    # 生成对应的 x 轴数据
    x_odd = np.arange(len(odd_list))
    x_even = np.arange(len(even_list))
    
    # 创建图形
    plt.figure(figsize=(14, 6))
    
    # 绘制奇数行数据的连接和平滑
    plt.subplot(1, 2, 1)
    plt.scatter(x_odd, odd_list, color='blue', label='原始数据点')
    
    # 直接连接相邻点
    plt.plot(x_odd, odd_list, 'r-', alpha=0.5, label='直接连接')
    
    # 移动平均平滑
    x_ma_odd, y_ma_odd = moving_average(x_odd, odd_list, window_size=5)
    plt.plot(x_ma_odd, y_ma_odd, 'g--', label='移动平均平滑')
    
    # Savitzky-Golay 平滑
    x_sg_odd, y_sg_odd = savitzky_golay(x_odd, odd_list, window_length=7, polyorder=3)
    plt.plot(x_sg_odd, y_sg_odd, 'm-.', label='Savitzky-Golay 平滑')
    
    # 样条插值平滑
    x_sp_odd, y_sp_odd = spline_interpolation(x_odd, odd_list, smooth_factor=5)
    plt.plot(x_sp_odd, y_sp_odd, 'c:', label='样条插值平滑')
    
    plt.title('奇数行数据连接与平滑')
    plt.xlabel('索引')
    plt.ylabel('数值')
    plt.legend()
    plt.grid(True)
    
    # 绘制偶数行数据的连接和平滑
    plt.subplot(1, 2, 2)
    plt.scatter(x_even, even_list, color='blue', label='原始数据点')
    
    # 直接连接相邻点
    plt.plot(x_even, even_list, 'r-', alpha=0.5, label='直接连接')
    

    # Savitzky-Golay 平滑
    x_sg_even, y_sg_even = savitzky_golay(x_even, even_list, window_length=7, polyorder=3)
    plt.plot(x_sg_even, y_sg_even, 'm-.', label='Savitzky-Golay 平滑')
    
   
    
    plt.title('偶数行数据连接与平滑')
    plt.xlabel('索引')
    plt.ylabel('数值')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    
    # 输出平滑后的偶数行数据（样条插值结果）
    print("\n平滑后的偶数行数据（样条插值结果）:")
    print("索引\t原始值\t平滑值")
    for i in range(len(x_even)):
        # 找到最接近的平滑值索引
        closest_idx = np.abs(x_sp_even - x_even[i]).argmin()
        print(f"{x_even[i]:.1f}\t{even_list[i]:.3f}\t{y_sp_even[closest_idx]:.3f}")

if __name__ == "__main__":
    main()