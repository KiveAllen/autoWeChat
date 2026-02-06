# -*- coding: utf-8 -*-
"""
本地配置文件模板
请复制此文件为 local_config.py 并填写实际配置信息
"""

# MQTT服务器配置列表
MQTT_CONFIGS = [
    {
        "server": "your-mqtt-server.com",      # MQTT服务器地址
        "port": 1883,                          # MQTT端口
        "username": "your-username",           # 用户名
        "password": "your-password",           # 密码
        "subscribe_topic": "wx/your/topic"     # 订阅主题
    },
    # 可以添加更多MQTT客户端配置
    # {
    #     "server": "another-server.com",
    #     "port": 1883,
    #     "username": "another-user",
    #     "password": "another-pass",
    #     "subscribe_topic": "wx/another/topic"
    # }
]

# 健康检查间隔时间（秒）
HEALTH_CHECK_INTERVAL = 30
