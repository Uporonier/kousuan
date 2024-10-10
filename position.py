import pyautogui
import time
#
#
#   本代码用来辅助获取屏幕定位
#
#


print("将鼠标移动到你想要的位置...")
time.sleep(3)  # 给你3秒钟的时间来移动鼠标
x, y = pyautogui.position()  # 获取鼠标当前的位置
print(f"当前鼠标坐标: ({x}, {y})")
