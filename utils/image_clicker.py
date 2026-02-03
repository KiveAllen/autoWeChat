# utils/image_clicker.py
import cv2
import pyautogui
import numpy as np
from typing import Tuple, Optional


class ImageClicker:
    """
    图像识别并点击工具类
    """

    def __init__(self):
        # 设置pyautogui的一些参数
        pyautogui.FAILSAFE = True  # 鼠标移动到屏幕左上角会引发异常
        pyautogui.PAUSE = 0.1      # 每次pyautogui操作后的默认暂停时间

    def find_image_on_screen(self, image_path: str, confidence: float = 0.8) -> Optional[Tuple[int, int, int, int]]:
        """
        在屏幕上查找指定图像

        Args:
            image_path: 图片文件路径
            confidence: 匹配度阈值，范围0-1，默认0.8

        Returns:
            匹配区域的坐标 (left, top, width, height)，如果没有找到则返回None
        """
        try:
            # 读取模板图像
            template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if template is None:
                print(f"无法加载图片: {image_path}")
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
                return (max_loc[0], max_loc[1], w, h)
            else:
                print(f"未找到匹配图像，最高匹配度: {max_val:.2f}, 阈值: {confidence}")
                return None

        except Exception as e:
            print(f"查找图像时发生错误: {str(e)}")
            return None

    def click_below_image(self, image_path: str, offset_y: int = 50, confidence: float = 0.8) -> bool:
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
        coords = self.find_image_on_screen(image_path, confidence)

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

    def find_multiple_images(self, image_path: str, confidence: float = 0.8) -> list:
        """
        查找屏幕上所有匹配的图像

        Args:
            image_path: 图片文件路径
            confidence: 匹配度阈值，范围0-1，默认0.8

        Returns:
            匹配区域坐标列表 [(left, top, width, height), ...]
        """
        try:
            template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if template is None:
                print(f"无法加载图片: {image_path}")
                return []

            screenshot = pyautogui.screenshot()
            screen_np = np.array(screenshot)
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)

            # 进行模板匹配
            result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)

            # 找出所有匹配度大于阈值的位置
            locations = np.where(result >= confidence)
            locations = list(zip(*locations[::-1]))  # 转换为(x, y)格式

            # 获取模板尺寸
            h, w = template.shape[:2]

            # 构建匹配区域坐标列表
            matches = []
            for loc in locations:
                match_rect = (loc[0], loc[1], w, h)
                matches.append(match_rect)

            # 去除重复的匹配结果（使用非极大值抑制）
            filtered_matches = self.non_max_suppression(matches, overlap_threshold=0.5)

            return filtered_matches

        except Exception as e:
            print(f"查找多个图像时发生错误: {str(e)}")
            return []

    def non_max_suppression(self, boxes: list, overlap_threshold: float = 0.5) -> list:
        """
        非极大值抑制，去除重复的匹配结果

        Args:
            boxes: 匹配区域坐标列表 [(left, top, width, height), ...]
            overlap_threshold: 重叠阈值

        Returns:
            过滤后的匹配区域坐标列表
        """
        if len(boxes) == 0:
            return []

        # 将坐标转换为 (x1, y1, x2, y2) 格式
        boxes_array = []
        scores = []
        for box in boxes:
            left, top, width, height = box
            boxes_array.append([left, top, left + width, top + height])
            # 使用匹配度作为分数（这里简化处理，实际使用时应包含分数）
            scores.append(1.0)

        boxes_array = np.array(boxes_array)
        scores = np.array(scores)

        # 计算面积
        areas = (boxes_array[:, 2] - boxes_array[:, 0]) * (boxes_array[:, 3] - boxes_array[:, 1])

        # 获取排序后的索引
        indices = np.argsort(scores)[::-1]

        picked = []
        while len(indices) > 0:
            current = indices[0]
            picked.append(current)

            if len(indices) == 1:
                break

            # 计算交集
            xx1 = np.maximum(boxes_array[current][0], boxes_array[indices[1:]][0])
            yy1 = np.maximum(boxes_array[current][1], boxes_array[indices[1:]][1])
            xx2 = np.minimum(boxes_array[current][2], boxes_array[indices[1:]][2])
            yy2 = np.minimum(boxes_array[current][3], boxes_array[indices[1:]][3])

            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)

            intersection = w * h
            union = areas[current] + areas[indices[1:]] - intersection

            iou = intersection / union

            # 移除IoU大于阈值的框
            remaining_indices = np.where(iou <= overlap_threshold)[0] + 1
            indices = indices[remaining_indices]

        return [boxes[i] for i in picked]
