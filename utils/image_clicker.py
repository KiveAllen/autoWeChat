from typing import Tuple, Optional

import cv2
import numpy as np
import pyautogui
import os
import sys


def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        # PyInstaller创建临时文件夹，并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def find_image_on_screen(image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int, int, int]]:
    """
    在屏幕上查找指定图像

    Args:
        image_path: 图片文件路径
        confidence: 匹配度阈值，范围0-1，默认0.8

    Returns:
        匹配区域的坐标 (left, top, width, height)，如果没有找到则返回None
    """
    try:
        # 使用资源路径处理函数获取正确的图片路径
        full_image_path = get_resource_path(image_path)

        # 读取模板图像
        template = cv2.imread(full_image_path, cv2.IMREAD_UNCHANGED)
        if template is None:
            print(f"无法加载图片: {full_image_path}")
            return None

        # 获取当前屏幕截图
        screenshot = pyautogui.screenshot()
        screen_np = np.array(screenshot)
        screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

        # 进行模板匹配
        result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)

        # 找到最大匹配值的位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            # 获取模板尺寸
            h, w = template.shape[:2]

            # 返回匹配区域的坐标 (left, top, width, height)
            return max_loc[0], max_loc[1], w, h
        else:
            print(f"未找到匹配图像，最高匹配度: {max_val:.2f}, 阈值: {confidence}")
            return None

    except Exception as e:
        print(f"查找图像时发生错误: {str(e)}")
        return None


def click_below_image(image_path: str, offset_y: int = 50, confidence: float = 0.8) -> bool:
    """
    识别图片并在识别结果下方offset_y像素处点击

    Args:
        image_path: 图片文件路径
        offset_y: 在识别结果下方多少像素处点击，默认50像素
        confidence: 匹配度阈值，范围0-1，默认0.8

    Returns:
        是否成功点击
    """
    # 查找图像
    coords = find_image_on_screen(image_path, confidence)

    if coords is None:
        print(f"未找到图像: {image_path}")
        return False

    left, top, width, height = coords

    # 计算点击位置（图像下方offset_y像素）
    click_x = left + width // 2  # 图像中心X坐标
    click_y = top + height + offset_y  # 图像底部Y坐标 + 偏移量

    # 获取屏幕尺寸，确保点击位置不会超出屏幕边界
    screen_width, screen_height = pyautogui.size()
    click_x = max(0, min(click_x, screen_width - 1))
    click_y = max(0, min(click_y, screen_height - 1))

    try:
        # 移动鼠标并点击
        pyautogui.click(click_x, click_y)
        print(f"已点击位置: ({click_x}, {click_y})，图像下方{offset_y}px")
        return True
    except Exception as e:
        print(f"点击时发生错误: {str(e)}")
        return False
