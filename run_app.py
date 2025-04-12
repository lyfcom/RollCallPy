"""
班级点名器启动脚本
这个脚本用于启动班级点名器应用，并在打包为exe后作为入口点
"""
import subprocess
import sys
import os
import time
import webbrowser
import shutil
import socket
import logging
import traceback
import functools
from threading import Timer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_log.txt", encoding='utf-8', mode='a'), # 使用追加模式
        logging.StreamHandler()
    ]
)

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port=5000, max_port=5050):
    """寻找可用端口"""
    for port in range(start_port, max_port):
        if not is_port_in_use(port):
            return port
    return None

def resource_path(relative_path):
    """获取资源的绝对路径，适用于PyInstaller打包后的情况"""
    try:
        # PyInstaller创建临时文件夹并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
        # logging.info(f"使用PyInstaller临时路径: {base_path}")
    except AttributeError:
        # 如果不是通过PyInstaller运行，则使用当前文件所在的目录
        base_path = os.path.abspath(os.path.dirname(__file__))
        # logging.info(f"使用脚本目录作为基础路径: {base_path}")
    
    path = os.path.join(base_path, relative_path)
    # logging.info(f"解析资源路径: {relative_path} -> {path}")
    return path

def ensure_static_files():
    """确保静态文件和模板文件存在，并在需要时从打包资源中复制"""
    try:
        base_dir = os.getcwd() # 使用当前工作目录作为目标基础
        static_dir = os.path.join(base_dir, 'static')
        templates_dir = os.path.join(base_dir, 'templates')

        # 确保目标目录存在
        os.makedirs(static_dir, exist_ok=True)
        os.makedirs(templates_dir, exist_ok=True)
        logging.info(f"确保目标目录存在: {static_dir}, {templates_dir}")

        # 定义需要的文件和它们的源路径 (相对于打包资源或脚本目录)
        required_files = {
            os.path.join(static_dir, 'roll.mp3'): resource_path(os.path.join('static', 'roll.mp3')),
            os.path.join(static_dir, 'select.mp3'): resource_path(os.path.join('static', 'select.mp3')),
            os.path.join(static_dir, 'click.mp3'): resource_path(os.path.join('static', 'click.mp3')),
            os.path.join(templates_dir, 'index.html'): resource_path(os.path.join('templates', 'index.html')),
        }

        for target_path, source_path in required_files.items():
            # 检查目标文件是否存在或是否有效 (例如，大小检查 > 100字节)
            is_valid = os.path.exists(target_path) and os.path.getsize(target_path) > 100

            if not is_valid:
                if os.path.exists(source_path):
                    try:
                        shutil.copy2(source_path, target_path)
                        logging.info(f"已复制文件: {os.path.basename(source_path)} -> {target_path}")
                    except Exception as copy_error:
                         logging.error(f"复制文件失败: {source_path} 到 {target_path} - {copy_error}")
                else:
                    # 如果源文件不存在，也记录下来
                    logging.warning(f"源文件未找到，无法复制: {source_path} (目标: {target_path})")
            # else:
            #     # 文件已存在，可以考虑不打印日志，减少干扰
            #     # logging.debug(f"文件已存在且有效: {target_path}")

    except Exception as e:
        logging.error(f"确保文件时出错: {str(e)}")
        logging.error(traceback.format_exc())

def open_browser(port):
    """打开浏览器访问应用"""
    url = f"http://127.0.0.1:{port}"
    try:
        logging.info(f"尝试打开浏览器: {url}")
        webbrowser.open_new(url)
    except Exception as e:
        logging.error(f"打开浏览器失败: {str(e)}")

def main():
    logging.info("="*50)
    logging.info("班级点名器启动")
    logging.info(f"Python版本: {sys.version.split()[0]}")
    logging.info(f"系统平台: {sys.platform}")
    
    # 移除 sys.path 修改
    
    try:
        # 获取当前脚本所在目录并切换工作目录
        # 这对于确保相对路径 (如 static/, templates/, students.json) 正确解析很重要
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if os.getcwd() != current_dir:
             logging.info(f"当前目录: {os.getcwd()}")
             os.chdir(current_dir)
             logging.info(f"已切换工作目录到: {current_dir}")
        else:
            logging.info(f"当前工作目录已是脚本目录: {current_dir}")
        
        # 确保静态/模板文件和目录存在
        ensure_static_files()
        
        # 确保students.json文件存在于当前工作目录
        students_json_path = os.path.join(current_dir, 'students.json')
        if not os.path.exists(students_json_path):
            try:
                with open(students_json_path, 'w', encoding='utf-8') as f:
                    f.write('[]')
                logging.info(f"已创建空的学生名单文件: {students_json_path}")
            except IOError as e:
                logging.error(f"创建 students.json 文件失败: {e}")
                input("错误：无法创建数据文件，请检查权限。按Enter键退出...")
                sys.exit(1)
        
        # 寻找可用端口
        port = find_available_port()
        if port is None:
            logging.error("无法找到可用端口 (5000-5050)，请检查端口占用情况")
            input("错误：所需端口已被占用。按Enter键退出...")
            sys.exit(1)
        
        logging.info(f"使用端口: {port}")
        
        # 设置环境变量，传递给main.py (虽然exec不需要，但保留可能有用)
        os.environ['APP_PORT'] = str(port)
        
        # 运行主应用
        try:
            # 延迟打开浏览器 (稍微缩短延迟)
            browser_timer = Timer(1.0, functools.partial(open_browser, port))
            browser_timer.daemon = True
            browser_timer.start()
            
            main_py_path = os.path.join(current_dir, 'main.py')
            logging.info(f"准备执行主应用文件: {main_py_path}")
            
            if os.path.exists(main_py_path):
                try:
                    with open(main_py_path, 'r', encoding='utf-8') as f:
                        main_code = f.read()
                    
                    # 创建一个全局命名空间来执行代码
                    # 显式传递 __name__ = '__main__' 来运行 main.py 中的主块
                    # 传递 __file__ 让 main.py 知道自己的路径
                    main_globals = {
                        '__name__': '__main__',
                        '__file__': main_py_path,
                        # 可以传递其他需要的全局变量
                    }
                    logging.info("开始执行 main.py ...")
                    exec(main_code, main_globals)
                    # exec 会阻塞直到 Flask 服务器停止 (例如 Ctrl+C)
                    logging.info("main.py 执行完毕 (Flask服务器已停止)")
                except SystemExit:
                    logging.info("Flask 服务器正常退出。")
                except Exception as exec_error:
                    logging.error(f"执行 main.py 时发生错误: {exec_error}")
                    logging.error(traceback.format_exc())
                    input("错误：应用主逻辑执行失败。按Enter键退出...")
                    sys.exit(1)
            else:
                 logging.error(f"主应用文件未找到: {main_py_path}")
                 input("错误：缺少核心应用文件。按Enter键退出...")
                 sys.exit(1)

        except Exception as e:
            # 这个捕获可能不会执行，因为 exec 内部的错误会在上面捕获
            logging.error(f"启动应用时发生意外错误: {str(e)}")
            logging.error(traceback.format_exc())
            input("发生未知启动错误。按任意键退出...")
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"程序初始化失败: {str(e)}")
        logging.error(traceback.format_exc())
        input("发生严重初始化错误，按任意键退出...")
        sys.exit(1)

    # 移除末尾的循环，app.run() 或 exec(main.py) 会阻塞
    logging.info("班级点名器退出")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 这个捕获通常只在main()完全失败时触发
        logging.critical(f"程序运行时发生顶层错误: {str(e)}")
        logging.critical(traceback.format_exc())
        input("发生无法处理的严重错误，按任意键退出...")
        sys.exit(1) 