import cv2
import numpy as np
import pytesseract
import mss
import pyautogui
import time
from threading import Thread, Lock

# 设置Tesseract可执行文件路径   请自行安装 并更换成你的路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 定义捕获区域，左上角和右下角坐标    题目的坐标
current_top_left = (127, 297)
current_bottom_right = (432, 400)

# 计算当前题目区域的宽度和高度
current_monitor = {
    "top": current_top_left[1],
    "left": current_top_left[0],
    "width": current_bottom_right[0] - current_top_left[0],
    "height": current_bottom_right[1] - current_top_left[1]
}

# 存储上一个绘制的符号
last_numbers = None  # 用于记录上一次的数字
lock = Lock()  # 创建一个锁以保证线程安全


def draw_symbol_with_mouse(symbol, position):
    x, y = position
    pyautogui.moveTo(x, y)  # 移动到指定位置
    pyautogui.mouseDown()  # 按下鼠标左键

    # 减少移动步骤
    if symbol == ">":
        pyautogui.moveRel(30, -30)  # 添加 duration 减少移动时间
        pyautogui.moveRel(-30, -30)
    elif symbol == "<":
        pyautogui.moveRel(-30, -30)
        pyautogui.moveRel(30, -30)

    pyautogui.mouseUp()  # 放开鼠标左键


def print_result(numbers, comparison):
    print(f"识别到的数字: {numbers[0]} 和 {numbers[1]}, 判断结果: {comparison}")


def ocr_process(frame):
    global last_numbers
    # 图像预处理
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # OCR识别
    custom_config = r'--oem 3 --psm 6 outputbase digits -c tessedit_char_whitelist=0123456789?'
    result = pytesseract.image_to_string(binary, config=custom_config)

    # 按问号分割识别结果
    parts = result.split('?')

    # 提取数字并处理
    numbers = [int(''.join(filter(str.isdigit, part))) for part in parts if ''.join(filter(str.isdigit, part))]

    # 进行比较并绘制符号
    if len(numbers) == 2:
        with lock:  # 确保对共享资源的安全访问
            if numbers != last_numbers:  # 只有当新数字不同于上一个数字时才进行绘制
                if numbers[0] > numbers[1]:
                    comparison = ">"
                    draw_symbol_with_mouse(">", (187, 706))
                elif numbers[0] < numbers[1]:
                    comparison = "<"
                    draw_symbol_with_mouse("<",  (187, 706))
                else:
                    comparison = "="
                last_numbers = numbers
                print_thread = Thread(target=print_result, args=(numbers, comparison))
                print_thread.start()


def capture_process():
    with mss.mss() as sct:
        while True:
            img = sct.grab(current_monitor)
            img_np = np.array(img)
            img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
            ocr_process(img_bgr)


capture_thread = Thread(target=capture_process)
capture_thread.start()
