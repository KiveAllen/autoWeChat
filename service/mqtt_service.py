import json
import threading
import time
import traceback

import paho.mqtt.client as paho_mqtt

# 添加WeChatService导入
from core.wx_operation_service import WeChatService


class WxMqtt:
    def __init__(self, mqtt_server, mqtt_port=1883, mqtt_username=None, mqtt_password=None,
                 subscribe_topic="wx/test/message"):
        self.client = None
        self.send_message_thread = None
        self.thread = None
        self.is_connected = False
        self.server = mqtt_server
        self.port = mqtt_port
        self.username = mqtt_username
        self.password = mqtt_password
        self.subscribe_topic = subscribe_topic
        # 初始化WeChatService实例
        self.wechat_service = WeChatService()

    def start(self) -> None:
        self.client = paho_mqtt.Client(paho_mqtt.CallbackAPIVersion.VERSION2)  # type: ignore
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.username_pw_set(self.username, self.password)
        self.thread = threading.Thread(target=self.connect, daemon=True)
        self.thread.start()

    def connect(self) -> None:
        # 循环尝试连接，直到连接成功
        while not self.is_connected:
            try:
                self.client.connect(self.server, self.port)
                self.client.loop_forever()
                print("mqtt loop_forever.......")
            except Exception as e:
                print(f"mqtt连接失败: {e}, 等待2秒后重试连接...")
                traceback.print_exc()
            time.sleep(2)

    def on_disconnect(self, client, userdata, disconnect_flags, reason, properties):
        self.is_connected = False
        print("mqtt连接断开...")

    def is_connected(self):
        return self.is_connected

    # 连接的回调函数
    def on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("mqtt服务端连接成功")
            self.is_connected = True  # 更新连接状态为成功
            self.subscribe()  # 成功连接后订阅主题
        else:
            print(f"mqtt连接失败，返回码：{reason_code}")
            self.is_connected = False  # 更新连接状态为失败

    # 收到消息的回调函数
    def on_message(self, client, userdata, msg):
        try:
            content = json.loads(msg.payload.decode('utf-8'))
            if content is None:
                print("-------------------------------------++++++++++++++++++mqtt消息格式不正确")
            method = content.get("method", None)
            print(f"接收mqtt消息，topic：{msg.topic}  method: {method}  message: {content}")

            # 处理控制微信的消息
            if method == "sendWechatMessage":
                self.handle_wechat_message(content)

        except Exception as e:
            print(f"异常-mqtt处理失败: {e}")
            traceback.print_exc()

    def handle_wechat_message(self, content):
        """
        处理微信消息发送请求
        """
        try:
            # 解析消息内容
            chat_names = content.get("chatNames", [])
            messages = content.get("messages", [])
            image_urls = content.get("imageUrls", [])

            # 异步发送消息
            result = self.wechat_service.send_message_to_chats(chat_names=chat_names, messages=messages,
                                                               image_urls=image_urls)
            print(f"已提交微信消息发送任务: {content}")
            print(f"任务结果: {result}")
        except Exception as e:
            print(f"处理微信消息失败: {e}")
            traceback.print_exc()

    def publish(self, topic, message):
        self.client.publish(topic, payload=message, qos=0, retain=False)
        print("发送mqtt消息, topic: " + topic + "  message: " + message)

    def subscribe(self):
        self.client.subscribe(self.subscribe_topic)
