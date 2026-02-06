# 本地配置说明

## 配置文件位置

敏感配置信息存储在 `config/local_config.py` 文件中，该文件已被添加到 `.gitignore` 中，不会被提交到Git仓库。

## 配置文件结构

```python
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
]

# 健康检查间隔时间（秒）
HEALTH_CHECK_INTERVAL = 30
```

## 使用步骤

1. **复制模板文件**：
   ```bash
   cp config/local_config_template.py config/local_config.py
   ```

2. **编辑配置文件**：
   修改 `config/local_config.py` 中的配置信息

3. **运行服务**：
   ```bash
   python mqtt_main.py
   ```

## 安全提醒

- ❌ 不要将 `local_config.py` 文件提交到Git仓库
- ✅ 使用 `.gitignore` 确保敏感信息不被泄露
- ✅ 定期更换密码和密钥
- ✅ 在生产环境中使用强密码

## 故障排除

如果遇到配置文件导入错误，程序会自动使用默认配置：
- 服务器: localhost
- 端口: 1883
- 用户名: test
- 密码: test
