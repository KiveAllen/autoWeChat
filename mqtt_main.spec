# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 分析主程序及其依赖
a = Analysis(
    ['mqtt_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # 包含配置文件目录
        ('config', 'config'),
        # 如果有其他数据文件也可以在这里添加
    ],
    hiddenimports=[
        # 显式包含可能被自动检测遗漏的模块
        'paho.mqtt.client',
        'core.wx_operation_service',
        'service.mqtt_service',
        'utils.config_utils',
        'utils.window_utils',
        'utils.process_utils',
        'utils.clipboard_utils',
        'utils.file_io_utils',
        'utils.hash_utils',
        'utils.image_clicker',
        'cv2',  # OpenCV
        'numpy',
        'pyautogui',
        'uiautomation',
        'win32gui',
        'win32con',
        'win32api',
        'pywintypes',
        'pythoncom',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不必要的模块以减小文件大小
        'tkinter',
        'matplotlib',
        'scipy',
        'sklearn',
        'tensorflow',
        'torch',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 处理Python字节码
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WeChatMQTTService',  # 可执行文件名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用UPX压缩（如果可用）
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以指定图标文件路径
)
