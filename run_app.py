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
# ---- Standard Library Imports for Networking/Cleanup ----
import http.client
import json
import atexit
# -------------------------------------------------------

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app_log.txt", encoding='utf-8', mode='a'), # 使用追加模式
        logging.StreamHandler()
    ]
)

# --- Constants ---
PORT_FILE = "rollcall.port"
APP_IDENTIFIER = "RollCallPy" # Must match main.py
DEFAULT_START_PORT = 5000
DEFAULT_MAX_PORT = 5050
# -----------------

def is_port_in_use(port, timeout=0.1):
    """检查端口是否被占用 (使用稍长一点的超时)"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            # connect_ex returns 0 if connection succeeds
            result = s.connect_ex(('127.0.0.1', port))
            return result == 0
        except socket.timeout:
            return False # Timeout means nothing is listening or connection is slow
        except Exception as e:
            logging.debug(f"Error checking port {port}: {e}")
            return False

def find_available_port(start_port=DEFAULT_START_PORT, max_port=DEFAULT_MAX_PORT):
    """寻找可用端口"""
    logging.info(f"寻找可用端口范围: {start_port}-{max_port}")
    for port in range(start_port, max_port):
        if not is_port_in_use(port):
            logging.info(f"找到可用端口: {port}")
            return port
    logging.warning("未找到可用端口")
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

def remove_port_file():
    """尝试删除端口文件 (用于 atexit 清理)"""
    try:
        if os.path.exists(PORT_FILE):
            os.remove(PORT_FILE)
            logging.info(f"已删除端口文件: {PORT_FILE}")
    except Exception as e:
        logging.warning(f"删除端口文件 {PORT_FILE} 时出错: {e}")

def ping_instance_http(port, timeout=0.5):
    """使用 http.client ping /ping 端点验证实例"""
    conn = None
    try:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
        conn.request("GET", "/ping")
        response = conn.getresponse()
        if response.status == 200:
            try:
                body = response.read().decode('utf-8')
                data = json.loads(body)
                if isinstance(data, dict) and data.get('app') == APP_IDENTIFIER:
                    logging.debug(f"端口 {port} ping 成功并验证通过。")
                    return True # Verification successful
                else:
                    logging.debug(f"端口 {port} ping 响应内容不匹配: {data}")
            except json.JSONDecodeError:
                logging.debug(f"端口 {port} ping 响应不是有效的 JSON: {body[:100]}") # Log first 100 chars
            except Exception as e:
                logging.warning(f"解析端口 {port} ping 响应时出错: {e}")
        else:
            logging.debug(f"端口 {port} ping 请求返回状态码: {response.status}")
    except (http.client.HTTPException, socket.timeout, ConnectionRefusedError, ConnectionResetError) as e:
        logging.debug(f"无法连接或 ping 端口 {port} 超时/被拒: {type(e).__name__}")
    except Exception as e:
        logging.warning(f"ping 端口 {port} 时发生意外错误: {e}")
    finally:
        if conn:
            conn.close()
    return False # Verification failed

def check_and_handle_existing_instance(start_port=DEFAULT_START_PORT, max_port=DEFAULT_MAX_PORT):
    """优先检查端口文件，然后扫描端口范围验证实例"""
    # 1. 尝试读取端口文件
    instance_found_via_file = False
    if os.path.exists(PORT_FILE):
        logging.info(f"找到端口文件: {PORT_FILE}")
        try:
            with open(PORT_FILE, 'r') as f:
                content = f.read().strip()
                if content.isdigit():
                    port = int(content)
                    logging.info(f"从文件读取到端口: {port}，正在验证...")
                    # 使用稍长的超时时间验证这个特定端口
                    if ping_instance_http(port, timeout=0.8):
                        logging.info(f"通过端口文件验证成功 (端口 {port})。")
                        print(f"应用已在端口 {port} 运行，将打开现有实例。")
                        open_browser(port)
                        logging.info("已打开浏览器指向现有实例，当前进程将退出。")
                        sys.exit(0) # 正常退出
                    else:
                        logging.warning(f"端口 {port} (来自文件) 验证失败或无响应，可能文件已过期。")
                        remove_port_file() # 删除可能无效的端口文件
                else:
                    logging.warning(f"端口文件 {PORT_FILE} 内容无效: '{content}'")
                    remove_port_file()
        except Exception as e:
            logging.error(f"读取或处理端口文件 {PORT_FILE} 时出错: {e}")
            remove_port_file() # 出错时也尝试删除

    # 2. 如果通过文件未找到，则扫描端口范围 (Fallback)
    logging.info(f"未通过端口文件找到运行实例，开始扫描端口 {start_port}-{max_port}...")
    for port in range(start_port, max_port):
        # 快速检查端口是否在使用 (避免对每个都 ping)
        if is_port_in_use(port, timeout=0.1):
            logging.debug(f"端口 {port} 被占用，尝试 ping 验证...")
            # 使用稍短的超时时间进行扫描 ping
            if ping_instance_http(port, timeout=0.2):
                logging.info(f"通过端口扫描验证成功 (端口 {port})。")
                print(f"应用已在端口 {port} 运行，将打开现有实例。")
                open_browser(port)
                logging.info("已打开浏览器指向现有实例，当前进程将退出。")
                sys.exit(0) # 正常退出
            # else: ping 失败，继续扫描下一个端口
        # else: port 不在使用，继续扫描下一个端口

    logging.info("在指定范围内未检测到正在运行的本应用实例。")
    return False # 表示没有找到正在运行的实例

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
        
        # **** 检查是否已有实例在运行 (优先使用端口文件) ****
        check_and_handle_existing_instance()
        # ******************************************************

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
            logging.error("无法找到可用端口 (5000-5050)，且未检测到运行中的实例。请检查端口占用情况")
            input("错误：无法启动应用，没有可用端口。按Enter键退出...")
            sys.exit(1)
        
        logging.info(f"将在端口 {port} 启动新实例。")
        
        # **** 写入端口文件并注册清理 ****
        try:
            with open(PORT_FILE, 'w') as f:
                f.write(str(port))
            logging.info(f"已将端口 {port} 写入文件: {PORT_FILE}")
            # 注册退出时清理端口文件的函数
            atexit.register(remove_port_file)
            logging.info("已注册退出时清理端口文件的任务。")
        except IOError as e:
            logging.warning(f"写入端口文件 {PORT_FILE} 失败: {e} (应用将继续，但快速实例检测可能失效)")
        # *********************************

        # 设置环境变量，传递给main.py (虽然exec不需要，但保留可能有用)
        os.environ['APP_PORT'] = str(port)
        
        # 运行主应用
        try:
            # 延迟打开浏览器
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
                    logging.info(f"开始执行 main.py (端口: {port})...")
                    exec(main_code, main_globals)
                    # exec 会阻塞直到 Flask 服务器停止 (例如 Ctrl+C)
                    logging.info("main.py 执行完毕 (Flask服务器已停止)")
                except SystemExit:
                    logging.info("Flask 服务器正常退出。")
                except Exception as exec_error:
                    logging.error(f"执行 main.py 时发生错误: {exec_error}")
                    logging.error(traceback.format_exc())
                    # 尝试清理端口文件即使执行出错
                    remove_port_file()
                    input("错误：应用主逻辑执行失败。按Enter键退出...")
                    sys.exit(1)
            else:
                 logging.error(f"主应用文件未找到: {main_py_path}")
                 remove_port_file() # 清理可能已写入的端口文件
                 input("错误：缺少核心应用文件。按Enter键退出...")
                 sys.exit(1)

        except Exception as e:
            # 这个捕获可能不会执行，因为 exec 内部的错误会在上面捕获
            logging.error(f"启动应用时发生意外错误: {str(e)}")
            logging.error(traceback.format_exc())
            remove_port_file() # 尝试清理
            input("发生未知启动错误。按任意键退出...")
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"程序初始化失败: {str(e)}")
        logging.error(traceback.format_exc())
        remove_port_file() # 尝试清理
        input("发生严重初始化错误，按任意键退出...")
        sys.exit(1)

    # 移除末尾的循环，app.run() 或 exec(main.py) 会阻塞
    logging.info("班级点名器退出")

if __name__ == "__main__":
    # 添加 finally 确保即使 main 异常退出也记录日志
    try:
        main()
    except SystemExit as e:
        # 捕获 sys.exit() 调用，避免打印不必要的错误信息
        if e.code == 0:
            logging.info("程序正常退出 (检测到现有实例或用户中断)")
        else:
            logging.error(f"程序异常退出，退出码: {e.code}")
            # atexit 可能不会在所有 sys.exit 路径触发，尝试手动清理
            remove_port_file()
    except Exception as e:
        # 这个捕获通常只在main()完全失败时触发
        logging.critical(f"程序运行时发生顶层错误: {str(e)}")
        logging.critical(traceback.format_exc())
        remove_port_file() # 尝试清理
        input("发生无法处理的严重错误，按任意键退出...")
        sys.exit(1)
    finally:
        logging.info("run_app.py 脚本结束。") 