import uiautomation as auto


def detect_wechat_window_info():
    """检测当前所有窗口，找出微信相关的窗口信息"""
    root = auto.GetRootControl()
    children = root.GetChildren()

    print("所有窗口信息:")
    for i, child in enumerate(children):
        if hasattr(child, 'Name') and hasattr(child, 'ClassName'):
            # 搜索包含"微信"或"WeChat"的窗口
            if '微信' in child.Name or 'WeChat' in child.Name or 'wechat' in child.ClassName.lower():
                print(f"窗口 {i}: 名称='{child.Name}', 类名='{child.ClassName}'")

    print("\n所有窗口列表:")
    for i, child in enumerate(children[:20]):  # 显示前20个窗口
        if hasattr(child, 'Name') and hasattr(child, 'ClassName'):
            print(f"{i}: '{child.Name}' - '{child.ClassName}'")


if __name__ == "__main__":
    detect_wechat_window_info()
