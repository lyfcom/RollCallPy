from flask import Flask, render_template, jsonify, request, send_from_directory, abort
import random
import json
import os
import webbrowser
import logging
from threading import Timer
from werkzeug.utils import secure_filename

# 配置日志
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app_log.txt", encoding='utf-8', mode='a'),
            logging.StreamHandler()
        ]
    )

# 获取端口号，默认5000
port = int(os.environ.get('APP_PORT', 5000))
logging.info(f"Flask 应用将使用端口: {port}")

app = Flask(__name__, static_folder='static', template_folder='templates')

# 学生名单文件路径
STUDENTS_FILE = 'students.json'
MAX_STUDENTS = 100  # 最大学生数限制

def open_browser():
    url = f"http://127.0.0.1:{port}/"
    webbrowser.open_new(url)
    logging.info(f"尝试打开浏览器: {url}")

def load_students():
    try:
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, 'r', encoding='utf-8') as f:
                students = json.load(f)
                return students if isinstance(students, list) else []
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"加载学生名单失败: {str(e)}")
    return []

def save_students(students):
    try:
        with open(STUDENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(students, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        logging.error(f"保存学生名单失败: {str(e)}")
        return False

@app.route('/')
def index():
    try:
        logging.info("访问首页")
        return render_template('index.html')
    except Exception as e:
        logging.error(f"渲染首页时出错: {str(e)}")
        return jsonify({'error': f'渲染页面失败: {str(e)}'}), 500

@app.route('/api/students', methods=['GET'])
def get_students():
    try:
        students = load_students()
        logging.info(f"获取学生列表: {len(students)}个")
        return jsonify(students)
    except Exception as e:
        logging.error(f"获取学生列表失败: {str(e)}")
        return jsonify({'error': '服务器错误'}), 500

@app.route('/api/students', methods=['POST'])
def add_student():
    students = load_students()
    
    if len(students) >= MAX_STUDENTS:
        return jsonify({'error': '学生数量已达到上限'}), 400
        
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': '无效的请求数据'}), 400
            
        new_student = data['name'].strip()
        if not new_student:
            return jsonify({'error': '学生姓名不能为空'}), 400
            
        if len(new_student) > 50:  # 名字长度限制
            return jsonify({'error': '学生姓名过长'}), 400
            
        if new_student in students:
            return jsonify({'error': '该学生已存在'}), 400
            
        students.append(new_student)
        if save_students(students):
            logging.info(f"添加学生: {new_student}")
            return jsonify(students)
        else:
            return jsonify({'error': '保存失败'}), 500
            
    except Exception as e:
        logging.error(f"添加学生失败: {str(e)}")
        return jsonify({'error': '服务器错误'}), 500

@app.route('/api/students/<name>', methods=['DELETE'])
def delete_student(name):
    try:
        students = load_students()
        if name in students:
            students.remove(name)
            if save_students(students):
                logging.info(f"删除学生: {name}")
                return jsonify(students)
            else:
                return jsonify({'error': '保存失败'}), 500
        return jsonify({'error': '学生不存在'}), 404
    except Exception as e:
        logging.error(f"删除学生失败: {str(e)}")
        return jsonify({'error': '服务器错误'}), 500

@app.route('/api/random', methods=['GET'])
def get_random_student():
    students = load_students()
    if not students:
        return jsonify({'error': '没有学生'}), 400
    chosen = random.choice(students)
    logging.info(f"随机选择学生: {chosen}")
    return jsonify({'name': chosen})

@app.errorhandler(404)
def not_found_error(error):
    logging.warning(f"404错误: {request.path}")
    return jsonify({'error': '资源不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"500错误: {str(error)}")
    return jsonify({'error': '服务器内部错误'}), 500

def check_environment():
    """检查环境配置并打印日志"""
    logging.info("="*30 + " Flask 应用启动检查 " + "="*30)
    logging.info(f"当前工作目录: {os.getcwd()}")
    logging.info(f"静态文件目录: {app.static_folder} (存在: {os.path.exists(app.static_folder)})")
    logging.info(f"模板文件目录: {app.template_folder} (存在: {os.path.exists(app.template_folder)})")
    logging.info(f"学生名单文件: {STUDENTS_FILE} (存在: {os.path.exists(STUDENTS_FILE)})")
    
    # 检查音频文件
    audio_files = ['roll.mp3', 'select.mp3', 'click.mp3']
    static_folder_path = os.path.join(os.getcwd(), app.static_folder)
    if os.path.exists(static_folder_path):
        for audio in audio_files:
            path = os.path.join(static_folder_path, audio)
            size = os.path.getsize(path) if os.path.exists(path) else 0
            logging.info(f"音频文件: {audio} (存在: {os.path.exists(path)}, 大小: {size} 字节)")
    else:
        logging.warning(f"静态文件夹不存在: {static_folder_path}")

    # 检查模板文件
    template_folder_path = os.path.join(os.getcwd(), app.template_folder)
    if os.path.exists(template_folder_path):
        templates = os.listdir(template_folder_path)
        logging.info(f"模板文件列表: {templates}")
    else:
        logging.warning(f"模板文件夹不存在: {template_folder_path}")

    # 打印路由信息
    routes = []
    try:
        for rule in app.url_map.iter_rules():
            # 排除默认的 static 路由和 HEAD/OPTIONS 方法
            if rule.endpoint != 'static':
                 methods = ', '.join(sorted([m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]))
                 if methods:
                    routes.append(f"{rule} ({methods})")
    except Exception as e:
        logging.error(f"获取路由信息时出错: {e}")
    logging.info(f"注册的应用路由: {routes}")

if __name__ == '__main__':
    # 检查环境
    check_environment()
    
    # 确保数据目录存在
    if not os.path.exists('static'):
        os.makedirs('static')
        logging.info("创建静态文件目录")
        
    # 初始化学生数据文件
    students_json_path = os.path.join(os.getcwd(), STUDENTS_FILE)
    if not os.path.exists(students_json_path):
        save_students([])
        logging.info(f"初始化学生数据文件: {students_json_path}")
    
    logging.info(f"Flask应用即将在端口 {port} 上启动 (直接运行)")
    
    # 应用程序启动
    try:
        # Flask运行
        # 移除 threaded=True，让 werkzeug 处理
        app.run(debug=False, host='127.0.0.1', port=port, use_reloader=False)
    except Exception as e:
        logging.error(f"Flask应用启动失败: {str(e)}")
        raise
