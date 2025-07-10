# import pandas as pd
# import numpy as np
# from uiautomation import WindowControl
# # wx = WindowControl(
# #     Name = '微信'
# # )
# wx = WindowControl(searchDepth=1, Name="腾讯QQ")
# def send_m():
#     wx.SendKeys('6',waitTime=0)
#     wx.SendKeys('{Enter}', waitTime=0)
#     wx.TextControl(SubName=last_m[:5]).RightClick()
#
# print(wx)
# wx.SwitchToThisWindow()
# hw = wx.ListControl(Name = '会话')
# print(hw)
# # df =  pd.read_csv('回复数据.csv', encoding='gb18030')
# # print(df)
#
#
# while True:
#     we = wx.TextControl(searchDepth=5)
#
#     while not we.Exists(0):
#         pass
#     print(we.Name)
#
#
#     if True:
#         print(we.Name)
#         we.Click(simulateMove=False)
#
#         last_m = wx.ListControl(Name = '消息').GetChildren()[-1].Name
#         print(last_m)
#         # ar = np.array(df)
#         send_m()
#
#
import uiautomation as auto


def get_all_window_names():
    window_names = []
    # 获取桌面根控件
    desktop = auto.GetRootControl()
    # 遍历所有顶级窗口控件
    for window in desktop.GetChildren():
        if window.ControlType == auto.ControlType.WindowControl:
            window_name = window.Name
            if window_name:
                window_names.append(window_name)
    return window_names


if __name__ == "__main__":
    all_window_names = get_all_window_names()
    for name in all_window_names:
        print(name)
