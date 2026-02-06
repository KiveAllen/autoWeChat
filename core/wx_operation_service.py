# -*- coding: utf-8 -*-
"""
微信服务层，处理微信消息发送的核心业务逻辑
"""

import concurrent.futures
import os
import queue
import tempfile
import threading
import urllib.request
from typing import List, Optional

import pythoncom

from core import WxOperation


def _get_file_extension(url: str) -> str:
    """从URL获取文件扩展名"""
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    url_lower = url.lower()
    for ext in extensions:
        if ext in url_lower:
            return ext
    return '.jpg'  # 默认扩展名


def _download_images_concurrently(image_urls: List[str], temp_files_list: List[str], max_workers: int = 5):
    """
    并发下载图片

    Args:
        image_urls: 图片URL列表
        temp_files_list: 用于存储临时文件路径的列表
        max_workers: 最大并发数

    Returns:
        list: 下载后的临时文件路径列表
    """
    file_paths = []

    def download_single_image(url):
        try:
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=_get_file_extension(url))
            temp_file.close()

            # 下载文件
            urllib.request.urlretrieve(url, temp_file.name)

            # 添加到临时文件列表中，以便后续清理
            temp_files_list.append(temp_file.name)
            return temp_file.name
        except Exception as e:
            print(f"下载图片失败 {url}: {e}")
            return None

    # 使用线程池并发下载
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(download_single_image, url): url for url in image_urls}
        for future in concurrent.futures.as_completed(future_to_url):
            file_path = future.result()
            if file_path:
                file_paths.append(file_path)

    return file_paths


class WeChatService:
    """微信服务类，封装微信消息发送相关业务逻辑"""

    def __init__(self):
        self.wx_instance = None
        self.com_initialized = False
        # 创建消息队列
        self.message_queue = queue.Queue()
        # 启动处理线程
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()

    def _get_wx_instance(self):
        """获取全局WxOperation实例，避免重复初始化COM库"""
        if not self.com_initialized:
            pythoncom.CoInitialize()
            self.com_initialized = True
            self.wx_instance = WxOperation()

        return self.wx_instance

    def _process_queue(self):
        """处理消息队列中的任务"""
        while True:
            try:
                # 从队列获取任务
                task = self.message_queue.get()
                if task is None:
                    break

                chat_names, messages, image_urls, callback = task

                # 执行发送任务
                result = self._send_message_internal(chat_names, messages, image_urls)

                # 执行回调通知结果
                if callback:
                    callback(result)

                self.message_queue.task_done()

            except Exception as e:
                print(f"处理队列任务时出错: {e}")

    def send_message_to_chats(self, chat_names: List[str], messages: Optional[List[str]] = None,
                              image_urls: Optional[List[str]] = None, callback=None) -> dict:
        """
        发送消息到多个聊天对象
        
        Args:
            chat_names: 聊天对象名称列表
            messages: 消息文本列表
            image_urls: 图片URL列表
            callback: 回调函数，用于异步通知结果
            
        Returns:
            dict: 执行结果
        """
        # 将任务加入队列
        self.message_queue.put((chat_names, messages, image_urls, callback))

        return {"success": True, "message": "消息已加入发送队列"}

    def _send_message_internal(self, chat_names: List[str], messages: Optional[List[str]] = None,
                               image_urls: Optional[List[str]] = None) -> dict:
        """
        实际执行消息发送的内部方法
        
        Args:
            chat_names: 聊天对象名称列表
            messages: 消息文本列表
            image_urls: 图片URL列表
            
        Returns:
            dict: 执行结果
        """
        temp_files = []
        try:
            wx = self._get_wx_instance()

            # 并发下载所有图片URL到临时文件
            file_paths = []
            if image_urls:
                file_paths = _download_images_concurrently(image_urls, temp_files)

            # 遍历所有聊天对象发送消息
            for chat_name in chat_names:
                wx.send_msg(name=chat_name, msgs=messages, file_paths=file_paths if file_paths else None)

            return {"success": True, "message": "消息发送成功"}

        except Exception as e:
            return {"success": False, "message": f"发送消息失败：{e}"}

        finally:
            # 清理临时文件
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except Exception as e:
                    print(f"删除临时文件失败 {temp_file}: {e}")
