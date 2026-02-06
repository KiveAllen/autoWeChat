"""微信群发消息"""

import re
import time
from typing import Iterable

import uiautomation as auto

from config import (WeChat, Interval)
from utils import (copy_files_to_clipboard, wake_up_window, click_below_image)
import os
import sys


class WxOperation:
    """
    微信群发消息的类，提供了与微信应用交互的方法集，用于发送消息，管理联系人列表等功能。

    Attributes:
    ----------
    wx_window: auto.WindowControl
        微信控制窗口

    Methods:
    -------
    __goto_chat_box(name):
        跳转到 指定好友窗口
    __send_text(*msgs):
        发送文本。
    __send_file(*filepath):
        发送文件
    send_msg(name, msgs, file_paths=None, add_remark_name=False, at_everyone=False,
            text_interval=0.05, file_interval=0.5) -> None:
        向指定的好友或群聊发送消息和文件。支持同时发送文本和文件。
    """

    def __init__(self):
        self.wx_window = None
        self.wx_window: auto.WindowControl
        auto.SetGlobalSearchTimeout(Interval.BASE_INTERVAL)
        self.visible_flag: bool = False

    def locate_wechat_window(self):
        if not self.visible_flag:
            wake_up_window(process_name=WeChat.WeChat_PROCESS_NAME)
            time.sleep(0.5)
            self.wx_window = auto.WindowControl(Name=WeChat.WINDOW_NAME, ClassName=WeChat.WINDOW_CLASSNAME)
            if not self.wx_window.Exists(Interval.MAX_SEARCH_SECOND,
                                         searchIntervalSeconds=Interval.MAX_SEARCH_INTERVAL):
                raise Exception('微信似乎并没有登录!')
            self.visible_flag = bool(self.visible_flag)
        # 微信窗口置顶
        self.wx_window.SetTopmost(isTopmost=True)

    def __goto_chat_box(self, name: str) -> bool:
        """
        跳转到指定 name好友的聊天窗口。

        Args:
            name(str): 必选参数，好友名称

        Returns:
            None
        """
        assert name, "无法跳转到名字为空的聊天窗口"
        self.wx_window.SendKeys(text='{Ctrl}F', waitTime=Interval.BASE_INTERVAL)
        self.wx_window.SendKeys(text='{Ctrl}A', waitTime=Interval.BASE_INTERVAL)
        self.wx_window.SendKey(key=auto.SpecialKeyNames['DELETE'])
        auto.SetClipboardText(text=name)
        time.sleep(Interval.BASE_INTERVAL)
        self.wx_window.SendKeys(text='{Ctrl}V', waitTime=Interval.BASE_INTERVAL)

        image_path = 'assets/images/group.png'
        if click_below_image(image_path=image_path, offset_y=50):
            return True

        # 无匹配用户, 取消搜索框
        self.wx_window.SendKeys(text='{Esc}', waitTime=Interval.BASE_INTERVAL)
        return False

    def __send_text(self, *msgs, wait_time, send_shortcut) -> None:
        """
        发送文本.

        Args:
            input_name(str): 必选参数, 为输入框
            *msgs(str): 必选参数，为发送的文本
            wait_time(float): 必选参数，为动态等待时间
            send_shortcut(str): 必选参数，为发送快捷键

        Returns:
            None
        """

        def insert_zwsp_after_emoji(text: str) -> str:
            """
            统计文本中emoji的数量，在整个字符串末尾添加相应数量的零宽空格 \u200b，
            避免微信吞字问题。
            """
            # 检测emoji表情符号的正则表达式
            emoji_pattern = re.compile("["
                                       "\U0001F600-\U0001F64F"  # emoticons
                                       "\U0001F300-\U0001F5FF"  # symbols & pictographs
                                       "\U0001F680-\U0001F6FF"  # transport & map symbols
                                       "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                       "\U00002500-\U00002BEF"  # chinese char
                                       "\U00002702-\U000027B0"
                                       "\U00002702-\U000027B0"
                                       "\U000024C2-\U0001F251"
                                       "\U0001f926-\U0001f937"
                                       "\U00010000-\U0010ffff"
                                       "\u2640-\u2642"
                                       "\u2600-\u2B55"
                                       "\u200d"
                                       "\u23cf"
                                       "\u23e9"
                                       "\u231a"
                                       "\ufe0f"  # dingbats
                                       "\u3030"
                                       "]+", flags=re.UNICODE)

            # 查找所有匹配的emoji
            emojis_found = emoji_pattern.findall(text)

            # 计算emoji总数量
            emoji_count = sum(len(emoji_group) for emoji_group in emojis_found)

            # 在文本末尾添加相应数量的零宽空格
            return text + ('\u200b' * emoji_count)

        for msg in msgs:
            assert msg, "发送的文本内容为空"
            self.wx_window.SendKeys(text='{Ctrl}a', waitTime=wait_time)
            self.wx_window.SendKey(key=auto.SpecialKeyNames['DELETE'], waitTime=wait_time)

            # 设置到剪切板再黏贴到输入框
            msg = insert_zwsp_after_emoji(msg)
            auto.SetClipboardText(text=msg)
            time.sleep(wait_time * 2.5)
            self.wx_window.SendKeys(text='{Ctrl}v', waitTime=wait_time * 2)

            # 发送消息
            self.wx_window.SendKeys(text=f'{send_shortcut}', waitTime=wait_time * 2)

    def __send_file(self, *file_paths, wait_time, send_shortcut) -> None:
        """
        发送文件.

        Args:
            *file_paths(str): 必选参数，为文件的路径
            wait_time(float): 必选参数，为动态等待时间
            send_shortcut(str): 必选参数，为发送快捷键

        Returns:
            None
        """
        # 复制文件到剪切板
        if copy_files_to_clipboard(file_paths=file_paths):
            # 粘贴到输入框
            self.wx_window.SendKeys(text='{Ctrl}V', waitTime=wait_time)
            # 按下回车键
            self.wx_window.SendKeys(text=f'{send_shortcut}', waitTime=wait_time / 2)

            time.sleep(wait_time)  # 等待发送动作完成

    def send_msg(self, name, msgs=None, file_paths=None, text_interval=Interval.SEND_TEXT_INTERVAL,
                 file_interval=Interval.SEND_FILE_INTERVAL, send_shortcut='{Enter}') -> None:
        """
        发送消息，可同时发送文本和文件（至少选一项

        Args:
            name(str):必选参数，接收消息的好友名称, 可以单发
            msgs(Iterable[str], Optional): 可选参数，发送的文本消息
            file_paths(Iterable[str], Optional):可选参数，发送的文件路径
            text_interval(float): 可选参数，默认为0.05
            file_interval(float): 可选参数，默认为0.5
            send_shortcut(str): 可选参数，默认为 Enter

        Raises:
            ValueError: 如果用户名为空或发送的消息和文件同时为空时抛出异常
            TypeError: 如果发送的文本消息或文件路径类型不是列表或元组时抛出异常
        """

        # 定位到微信窗口
        self.locate_wechat_window()

        if not name:
            raise ValueError("用户名不能为空")

        if not any([msgs, file_paths]):
            raise ValueError("发送的消息和文件不可同时为空")

        if msgs and not isinstance(msgs, Iterable):
            raise TypeError("发送的文本消息必须是可迭代的")

        if file_paths and not isinstance(file_paths, Iterable):
            raise TypeError("发送的文件路径必须是可迭代的")

        # 如果当前面板已经是需发送好友, 则无需再次搜索跳转
        # if not self.__match_nickname(name=name):
        if not self.__goto_chat_box(name=name):
            raise NameError('搜索失败')

        # 设置输入框为当前焦点
        image_path = 'assets/images/emoji.png'
        if not click_below_image(image_path=image_path, offset_y=50):
            raise NameError('群聊不存在')

        if msgs:
            self.__send_text(*msgs, wait_time=text_interval, send_shortcut=send_shortcut)
        if file_paths:
            self.__send_file(*file_paths, wait_time=file_interval, send_shortcut=send_shortcut)

        # 取消微信窗口置顶
        self.wx_window.SetTopmost(isTopmost=False)
