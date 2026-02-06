# -*- coding: utf-8 -*-
"""
MQTT服务主入口文件
用于打包成独立的可执行文件
"""
import json
import time

try:
    from config.local_config import MQTT_CONFIGS, HEALTH_CHECK_INTERVAL
except ImportError:
    # 如果本地配置文件不存在，使用默认配置
    MQTT_CONFIGS = [{"server": "localhost", "port": 1883, "username": "test", "password": "test",
        "subscribe_topic": "wx/test/message"}]
    HEALTH_CHECK_INTERVAL = 30

from service.mqtt_service import WxMqtt


def main():
    # 从本地配置文件读取MQTT配置

    # 创建并启动MQTT服务
    mqtt_clients = []
    for i, config in enumerate(MQTT_CONFIGS):
        mqtt_client = WxMqtt(config["server"], config["port"], config["username"], config["password"],
            config["subscribe_topic"])
        mqtt_client.start()
        mqtt_clients.append(mqtt_client)
        print(f"MQTT客户端 {i + 1} 已启动: {config['server']}:{config['port']}")

    print(f"MQTT服务已启动，共 {len(mqtt_clients)} 个客户端")
    print("按 Ctrl+C 停止服务")

    try:
        # 保持主线程运行
        while True:
            # 向所有客户端发布健康检查消息
            for i, (mqtt_client, config) in enumerate(zip(mqtt_clients, MQTT_CONFIGS)):
                message = {f"{config['server']} healthStatus": "OK"}
                mqtt_client.publish(config["subscribe_topic"], json.dumps(message))
                print(f"已向客户端 {i + 1} 发送健康检查: {config['server']}")

            time.sleep(HEALTH_CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\n正在停止MQTT服务...")
        for i, mqtt_client in enumerate(mqtt_clients):
            print(f"正在停止客户端 {i + 1}...")
        print("MQTT服务已停止")


if __name__ == '__main__':
    main()
