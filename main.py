from utils import WxOperation


def main():
    wx = WxOperation()
    wx.send_msg(name='测试发送群', msgs=['hello'])
    # 获取指定群聊名称
    print()


if __name__ == '__main__':
    main()
