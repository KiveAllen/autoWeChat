# autoWeChat - 微信自动化操作框架

一个功能强大的Python自动化框架，专为Windows平台设计，支持通过MQTT协议远程控制微信客户端进行消息发送、文件传输等操作。

> ⚠️ **免责声明**：本项目仅供技术研究和学习使用，请严格遵守微信平台使用条款及相关法律法规。

## 🌟 核心特性

### 🚀 多模式运行
- **直接调用模式**：通过Python API直接调用微信自动化功能
- **MQTT远程控制模式**：支持通过MQTT协议远程触发微信消息发送
- **异步队列处理**：内置消息队列机制，支持高并发消息处理

### 📨 消息发送能力
- ✅ **文本消息**：支持纯文本、Emoji表情、特殊字符发送
- ✅ **文件传输**：支持本地文件和网络图片URL发送
- ✅ **批量操作**：可同时向多个联系人/群聊发送消息
- ✅ **混合发送**：支持文本+文件组合发送

### 🎯 智能识别技术
- 🔍 **图像识别**：基于OpenCV的模板匹配技术精确定位界面元素
- 📍 **偏移点击**：独特的图像下方固定像素点击机制（用户偏好）
- 🔄 **智能重试**：自动重试机制确保操作成功率
- 🛡️ **防吞字处理**：自动处理微信Emoji显示异常问题

### ⚙️ 系统集成
- 🌐 **MQTT协议**：支持标准MQTT协议通信
- 🔧 **配置管理**：灵活的配置系统支持多环境部署
- 📊 **日志监控**：完善的日志记录和状态反馈
- 🔄 **自动恢复**：断线重连和异常恢复机制

## 🛠 技术架构

```
autoWeChat/
├── core/                  # 核心业务逻辑
│   ├── wx_operation.py      # 微信基础操作类
│   └── wx_operation_service.py  # 微信服务层
├── service/               # 服务组件
│   └── mqtt_service.py      # MQTT服务实现
├── utils/                 # 工具模块
│   ├── image_clicker.py     # 图像识别点击
│   ├── clipboard_utils.py   # 剪贴板操作
│   └── window_utils.py      # 窗口管理
├── config/                # 配置文件
│   └── config.py          # 系统配置
├── main.py               # 直接调用入口
├── mqtt_main.py          # MQTT服务入口
├── mqtt_main_build.py # Windows打包脚本
└── mqtt_main.spec # PyInstaller配置文件
```

## 📋 环境要求

### 系统环境
- **操作系统**：Windows 10/11 (64位)
- **Python版本**：3.8+
- **微信客户端**：Windows桌面版微信

### Python依赖
```bash
pip install -r requirements.txt
```

**核心依赖包**：
- `uiautomation~=2.0.18` - Windows UI自动化
- `paho-mqtt~=2.1.0` - MQTT客户端
- `opencv-python>=4.5.0` - 图像处理
- `pyautogui>=0.9.50` - 鼠标键盘控制
- `pywin32>=306` - Windows API接口
- `pythoncom` - COM组件支持

## 🚀 快速开始

### 1. 直接调用模式

```python
from core import WxOperation

def main():
    # 初始化微信操作实例
    wx = WxOperation()
    
    # 发送文本消息
    wx.send_msg(
        name='测试群聊',
        msgs=['Hello World!', '这是一条自动发送的消息 🚀'],
        file_paths=['path/to/image.jpg']
    )

if __name__ == '__main__':
    main()
```

### 2. MQTT远程控制模式

```python
from service import WxMqtt

# 配置MQTT服务
mqtt_client = WxMqtt(
    mqtt_server="your-mqtt-server.com",
    mqtt_port=1883,
    mqtt_username="username",
    mqtt_password="password",
    subscribe_topic="wx/control"
)

# 启动服务
mqtt_client.start()
```

### 3. MQTT消息格式

通过MQTT发送以下JSON格式消息来控制微信：

```json
{
  "method": "sendWechatMessage",
  "chatNames": ["群聊1", "好友A"],
  "messages": ["通知内容", "第二条消息"],
  "imageUrls": ["http://example.com/image.jpg"]
}
```

## 📖 API文档

### 核心类说明

#### `WxOperation` - 微信基础操作类
```python
class WxOperation:
    def send_msg(self, name: str, msgs=None, file_paths=None, 
                 text_interval=0.05, file_interval=0.25, 
                 send_shortcut='{Enter}') -> None:
        """
        发送消息到指定联系人
        
        Args:
            name: 接收方名称（好友/群聊）
            msgs: 文本消息列表
            file_paths: 文件路径列表
            text_interval: 文本发送间隔
            file_interval: 文件发送间隔
            send_shortcut: 发送快捷键
        """
```

#### `WeChatService` - 微信服务类
```python
class WeChatService:
    def send_message_to_chats(self, chat_names: List[str], 
                            messages: Optional[List[str]] = None,
                            image_urls: Optional[List[str]] = None,
                            callback=None) -> dict:
        """
        异步发送消息到多个聊天对象
        """
```

#### `WxMqtt` - MQTT服务类
```python
class WxMqtt:
    def start(self) -> None:
        """启动MQTT服务"""
    
    def publish(self, topic: str, message: str):
        """发布MQTT消息"""
```

## ⚙️ 配置说明

### 微信配置 (`config/config.py`)
```python
class WeChatConfig:
    WeChat_PROCESS_NAME = 'Weixin.exe'    # 微信进程名
    WINDOW_NAME = '微信'                   # 窗口标题
    WINDOW_CLASSNAME = 'Qt51514QWindowIcon'  # 窗口类名

# 时间间隔配置
class IntervalConfig:
    BASE_INTERVAL = 0.1           # 基础操作间隔
    SEND_TEXT_INTERVAL = 0.05     # 文本发送间隔
    SEND_FILE_INTERVAL = 0.25     # 文件发送间隔
```

### 图像识别配置
```python
# utils/image_clicker.py
confidence = 0.8      # 图像匹配度阈值
offset_y = 50         # 点击偏移像素（用户偏好）
```

## 🔧 高级功能

### 1. 批量消息处理
```python
from core import WeChatService

service = WeChatService()

# 批量发送给多个群聊
result = service.send_message_to_chats(
    chat_names=['群聊A', '群聊B', '群聊C'],
    messages=['批量通知内容'],
    image_urls=['http://example.com/notice.jpg']
)
```

### 2. 异步回调处理
```python
def send_callback(result):
    if result['success']:
        print("消息发送成功！")
    else:
        print(f"发送失败: {result['message']}")

service.send_message_to_chats(
    chat_names=['测试群'],
    messages=['异步消息'],
    callback=send_callback
)
```

### 3. 多MQTT客户端
```python
# 同时连接多个MQTT服务器
mqtt1 = WxMqtt("server1.com", 1883, "user1", "pass1", "wx/topic1")
mqtt2 = WxMqtt("server2.com", 1883, "user2", "pass2", "wx/topic2")

mqtt1.start()
mqtt2.start()
```

## 📊 性能优化

### 并发处理
- 使用线程池并发下载网络图片
- 消息队列异步处理避免阻塞
- 自动资源清理和内存管理

### 图像识别优化
- 缓存模板图像提高匹配速度
- 动态调整匹配阈值
- 屏幕边界检测防止越界

## 🔒 安全注意事项

### 使用建议
- ❌ 不要在生产环境中频繁大量发送消息
- ❌ 避免发送违法违规内容
- ✅ 建议添加发送频率限制
- ✅ 定期检查微信账号状态

### 风险提示
- 本工具通过模拟用户操作实现功能
- 过度使用可能导致账号异常
- 建议在测试账号上先行验证

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境搭建
```bash
git clone https://github.com/KiveAllen/autoWeChat.git
cd autoWeChat
pip install -r requirements.txt
```

### 代码规范
- 遵循PEP 8编码规范
- 添加必要的类型注解
- 编写单元测试
- 提供清晰的文档注释

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢以下开源项目的贡献：
- [uiautomation](https://github.com/yinkaisheng/Python-UIAutomation-for-Windows)
- [OpenCV](https://opencv.org/)
- [paho-mqtt](https://www.eclipse.org/paho/)
- [pyautogui](https://github.com/asweigart/pyautogui)

---

<p align="center">Made with ❤️ for automation enthusiasts</p>