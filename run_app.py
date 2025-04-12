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
        logging.FileHandler("app_log.txt", encoding='utf-8'),
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
        logging.info(f"使用PyInstaller临时路径: {base_path}")
    except Exception:
        base_path = os.path.abspath(".")
        logging.info(f"使用当前目录作为基础路径: {base_path}")
    
    path = os.path.join(base_path, relative_path)
    logging.info(f"资源路径: {relative_path} -> {path}")
    return path

def ensure_static_files():
    """确保静态文件存在"""
    try:
        static_dir = os.path.join(os.getcwd(), 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
            logging.info(f"创建静态文件目录: {static_dir}")
        
        # 检查音频文件是否存在，如不存在则从打包资源复制
        audio_files = ['roll.mp3', 'select.mp3', 'click.mp3']
        for audio in audio_files:
            target_path = os.path.join(static_dir, audio)
            if not os.path.exists(target_path) or os.path.getsize(target_path) < 1000:  # 文件不存在或过小
                # 尝试从多个可能的位置查找源文件
                possible_sources = [
                    resource_path(os.path.join('static', audio)),
                    os.path.join('static', audio),
                    resource_path(audio)
                ]
                
                for source_path in possible_sources:
                    if os.path.exists(source_path) and os.path.getsize(source_path) > 1000:
                        shutil.copy2(source_path, target_path)
                        logging.info(f"已复制音频文件: {source_path} -> {target_path}")
                        break
                else:
                    logging.warning(f"未找到有效的音频文件源: {audio}")
        
        # 确保templates目录存在
        templates_dir = os.path.join(os.getcwd(), 'templates')
        if not os.path.exists(templates_dir):
            os.makedirs(templates_dir)
            source_templates = resource_path('templates')
            if os.path.exists(source_templates):
                for template_file in os.listdir(source_templates):
                    source = os.path.join(source_templates, template_file)
                    target = os.path.join(templates_dir, template_file)
                    if os.path.isfile(source):
                        shutil.copy2(source, target)
                        logging.info(f"已复制模板文件: {source} -> {target}")
    except Exception as e:
        logging.error(f"确保静态文件时出错: {str(e)}")
        logging.error(traceback.format_exc())

def open_browser(port):
    """打开浏览器访问应用"""
    url = f"http://127.0.0.1:{port}"
    try:
        webbrowser.open_new(url)
        logging.info(f"已尝试打开浏览器: {url}")
    except Exception as e:
        logging.error(f"打开浏览器失败: {str(e)}")

def main():
    logging.info("="*50)
    logging.info("班级点名器启动")
    logging.info(f"当前工作目录: {os.getcwd()}")
    logging.info(f"Python版本: {sys.version}")
    logging.info(f"系统平台: {sys.platform}")
    
    # 调整Python路径，确保模块导入正常工作
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
        logging.info(f"将当前目录添加到Python路径: {current_dir}")
    
    # 如果是PyInstaller打包环境，也添加_MEIPASS路径
    try:
        meipass = sys._MEIPASS
        if meipass not in sys.path:
            sys.path.insert(0, meipass)
            logging.info(f"将PyInstaller临时目录添加到Python路径: {meipass}")
    except:
        pass
    
    # 打印Python搜索路径，便于调试
    logging.info(f"Python搜索路径: {sys.path}")
        
    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logging.info(f"脚本目录: {current_dir}")
        os.chdir(current_dir)
        logging.info(f"切换工作目录到: {current_dir}")
        
        # 确保静态文件和目录存在
        ensure_static_files()
        
        # 确保students.json文件存在
        if not os.path.exists('students.json'):
            with open('students.json', 'w', encoding='utf-8') as f:
                f.write('[]')
                logging.info("已创建空的学生名单文件")
        
        # 寻找可用端口
        port = find_available_port()
        if port is None:
            logging.error("无法找到可用端口，请关闭占用5000-5050端口的应用后重试")
            input("按Enter键退出...")
            sys.exit(1)
        
        logging.info(f"使用端口: {port}")
        
        # 设置环境变量，传递给main.py
        os.environ['APP_PORT'] = str(port)
        
        # 运行主应用
        try:
            # 延迟打开浏览器
            browser_timer = Timer(2.5, functools.partial(open_browser, port))
            browser_timer.daemon = True
            browser_timer.start()
            
            logging.info("正在导入主应用...")
            try:
                # 不要直接导入main模块，而是使用exec执行它
                possible_main_files = [
                    os.path.join(os.path.dirname(__file__), 'main.py'),
                    resource_path('main.py'),
                    os.path.join(os.getcwd(), 'main.py'),
                    os.path.abspath('main.py')
                ]
                
                main_file = None
                for path in possible_main_files:
                    if os.path.exists(path) and os.path.getsize(path) > 0:
                        main_file = path
                        logging.info(f"找到有效的main.py文件: {main_file}")
                        break
                
                logging.info(f"尝试加载主应用文件: {main_file}")
                
                if main_file and os.path.exists(main_file):
                    # 读取main.py内容并执行
                    with open(main_file, 'r', encoding='utf-8') as f:
                        main_code = f.read()
                    
                    # 确保Flask应用在主线程中运行
                    logging.info(f"执行main.py内容... (文件大小: {os.path.getsize(main_file)})")
                    exec(main_code, globals())
                    logging.info("主应用执行完成")
                else:
                    # 如果找不到main.py文件，尝试直接导入
                    logging.info("未找到main.py文件，尝试直接导入...")
                    import main
            except Exception as e:
                logging.error(f"执行main.py失败: {str(e)}")
                logging.error(traceback.format_exc())
                
                # 尝试直接导入作为备选方案
                logging.info("尝试备选方案：直接导入main模块...")
                import main
                
            logging.info("应用已启动，请在浏览器中使用...")
            
            # 保持程序运行，直到用户按下Ctrl+C
            try:
                logging.info("程序正在运行中，按Ctrl+C可以退出...")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logging.info("用户中断，程序退出")
        except ImportError as e:
            logging.error(f"导入主应用失败: {str(e)}")
            logging.error(traceback.format_exc())
            input("按任意键退出...")
            sys.exit(1)
        except Exception as e:
            logging.error(f"启动应用失败: {str(e)}")
            logging.error(traceback.format_exc())
            input("按任意键退出...")
            sys.exit(1)
    except Exception as e:
        logging.error(f"程序初始化失败: {str(e)}")
        logging.error(traceback.format_exc())
        input("发生错误，按任意键退出...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"程序运行失败: {str(e)}")
        logging.error(traceback.format_exc())
        input("发生严重错误，按任意键退出...")
        sys.exit(1) 