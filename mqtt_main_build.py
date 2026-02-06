# -*- coding: utf-8 -*-
"""
Windows打包脚本
用于将MQTT微信自动化服务打包成Windows可执行文件
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def clean_build_dirs():
    """清理旧的构建目录"""
    dirs_to_clean = ['dist', 'build', '__pycache__', 'mqtt_main.spec']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理 {dir_name} 目录...")
            if os.path.isfile(dir_name):
                os.remove(dir_name)
            else:
                shutil.rmtree(dir_name)

def check_config_file():
    """检查配置文件"""
    config_path = Path("config/local_config.py")
    template_path = Path("config/local_config_template.py")
    
    if not config_path.exists():
        print("警告: 未找到本地配置文件 config/local_config.py")
        print("将使用默认配置进行打包")
        if template_path.exists():
            print("建议复制 config/local_config_template.py 为 config/local_config.py 并修改配置")
        return False
    return True

def install_dependencies():
    """确保安装必要的依赖"""
    print("检查并安装必要的依赖...")
    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 检查是否有 pathlib 包（可能导致冲突）
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "pathlib"], 
                                capture_output=True, text=True)
        if result.returncode == 0:
            print("检测到 pathlib 包，可能会与 PyInstaller 冲突，建议卸载...")
            choice = input("是否自动卸载 pathlib 包? (y/n): ").lower().strip()
            if choice in ['y', 'yes', '是']:
                subprocess.run([sys.executable, "-m", "pip", "uninstall", "pathlib", "-y"])
                print("pathlib 包已卸载")
    except Exception as e:
        print(f"检查 pathlib 包时出错: {e}")

def generate_spec_file():
    """生成或更新 spec 文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

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
'''
    
    with open('mqtt_main.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("已生成/更新 spec 文件")

def run_pyinstaller():
    """执行PyInstaller打包"""
    try:
        print("开始执行PyInstaller打包...")
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'mqtt_main.spec'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("PyInstaller执行成功!")
            print(result.stdout)
            return True
        else:
            print("PyInstaller执行失败:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"执行PyInstaller时发生错误: {e}")
        return False

def post_build_actions():
    """打包后的处理工作"""
    exe_path = Path("dist/WeChatMQTTService.exe")
    
    if exe_path.exists():
        # 显示文件信息
        file_size = exe_path.stat().st_size
        print("=" * 40)
        print("打包成功!")
        print("=" * 40)
        print(f"可执行文件: {exe_path}")
        print(f"文件大小: {file_size:,} 字节 ({file_size/1024/1024:.2f} MB)")
        
        # 复制配置文件模板
        template_path = Path("config/local_config_template.py")
        dest_config_path = Path("dist/config/local_config.py")
        
        if template_path.exists():
            dest_config_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template_path, dest_config_path)
            print(f"已复制配置文件模板到: {dest_config_path}")
        
        print("=" * 40)
        print("使用说明:")
        print("1. 将 dist 目录中的所有文件复制到目标机器")
        print("2. 在目标机器上修改 config/local_config.py 配置文件")
        print("3. 双击运行 WeChatMQTTService.exe")
        print("=" * 40)
        
        return True
    else:
        print("打包失败! 未找到生成的可执行文件")
        return False

def main():
    print("=" * 40)
    print("开始打包MQTT微信自动化服务...")
    print("=" * 40)
    
    # 检查虚拟环境
    if not os.environ.get('VIRTUAL_ENV'):
        print("警告: 未检测到虚拟环境，建议在虚拟环境中运行")
        print("请先激活虚拟环境: .venv\\Scripts\\activate")
    
    # 安装必要依赖
    install_dependencies()
    
    # 清理旧文件
    clean_build_dirs()
    
    # 检查配置文件
    check_config_file()
    
    # 生成spec文件
    generate_spec_file()
    
    # 执行打包
    if run_pyinstaller():
        # 后续处理
        if post_build_actions():
            print("打包完成!")
            
            # 询问是否打开输出目录
            try:
                choice = input("是否打开输出目录? (y/n): ").lower().strip()
                if choice in ['y', 'yes', '是']:
                    os.startfile(os.path.abspath("dist"))
            except Exception as e:
                print(f"打开输出目录时出错: {e}")
        else:
            print("打包后处理失败!")
            sys.exit(1)
    else:
        print("打包失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()