# -*- coding: utf-8 -*-
"""
MQTT服务主入口文件
用于打包成独立的可执行文件
"""
import json
import time

from service.mqtt_service import WxMqtt


def main():
    # MQTT服务器配置 - 第一个客户端
    server1 = "8.138.207.63"
    port1 = 1883
    username1 = "wx_controller"
    password1 = "123456"
    subscribe_topic1 = "wx/1/message"

    # 第二个MQTT客户端配置（可以根据需要修改配置）
    server2 = "36.141.20.236"
    port2 = 21883
    username2 = "notify_bot"  # 建议使用不同用户名
    password2 = "zhixing123"
    subscribe_topic2 = "wx/2/message"

    # 创建并启动第一个MQTT服务
    mqtt1 = WxMqtt(server1, port1, username1, password1, subscribe_topic1)
    mqtt1.start()

    # 创建并启动第二个MQTT服务
    mqtt2 = WxMqtt(server2, port2, username2, password2, subscribe_topic2)
    mqtt2.start()

    print("MQTT服务已启动")
    print("按 Ctrl+C 停止服务")
    message = {"pyHealthStatus": "OK"}

    try:
        # 保持主线程运行
        while True:
            # 向两个客户端都发布消息
            mqtt1.publish("wx/1/message", json.dumps(message))
            mqtt2.publish("wx/2/message", json.dumps(message))
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n正在停止MQTT服务...")
        print("MQTT服务已停止")


if __name__ == '__main__':
    main()
