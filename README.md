# 班级点名器

[![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个基于 Flask 的班级随机点名应用，具有现代化的界面设计、流畅的动画效果和即时的音效反馈。

## 📋 功能特点

- **随机点名**：随机选择学生，带有平滑的卡片切换动画和声音提示
- **学生管理**：添加、编辑、删除学生信息，支持实时更新列表
- **美观界面**：精心设计的现代化 UI，礼花特效和平滑过渡动画
- **单例运行**：启动时检测已运行的实例，避免重复启动
- **离线运行**：完全本地运行，无需互联网连接
- **跨平台**：支持 Windows、macOS 和 Linux 操作系统
- **可打包**：支持使用 PyInstaller 打包为独立可执行文件

## 🛠 技术栈

- **后端**：Flask (Python Web 框架)
- **前端**：原生 JavaScript、HTML5、CSS3
- **数据存储**：本地 JSON 文件
- **动画**：CSS3 动画与 JavaScript Web Animations API
- **打包工具**：PyInstaller
- **音频处理**：HTML5 Audio API

## 📥 安装说明

### 环境要求

- Python 3.6 或更高版本
- 标准库 `http.client` 和 `socket` (用于实例检测)

### 步骤

1. **克隆或下载本仓库**

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行应用**
   ```bash
   # 推荐使用 run_app.py 启动，它会处理环境检查、端口选择和单例启动
   python run_app.py
   ```
   
   应用启动后会自动尝试打开浏览器。如果未自动打开，请手动访问日志中提示的 URL（通常是 `http://127.0.0.1:端口号`）。
   
   也可以直接运行 `main.py` (仅适用于开发或调试):
   ```bash
   python main.py
   ```

## 🎮 使用指南

1. **启动应用**
   - 双击 `run_app.exe` (打包版本) 或运行 `python run_app.py`
   - **单例运行**：如果应用已在后台运行，再次启动会直接打开现有的应用页面，而不是启动一个新的实例

2. **添加学生**
   - 在"添加学生"输入框中输入学生姓名
   - 点击"添加"按钮或按回车键

3. **管理学生**
   - **编辑**：点击学生名称，修改后按 Enter 保存或点击 ✓，按 Esc 或点击 ✗ 取消
   - **删除**：点击学生旁边的 🗑️ 图标

4. **随机点名**
   - 点击页面上方的"开始点名"按钮
   - 程序会随机选择一名学生，展示动画和播放音效

5. **退出应用**
   - 关闭命令行窗口或结束后台进程

## 📁 项目结构

```
.
├── README.md              # 项目文档
├── requirements.txt       # Python 依赖包列表
├── main.py                # Flask 应用主文件 (路由和业务逻辑)
├── run_app.py             # 应用启动脚本 (单例检测、环境检查)
├── rollcall.port          # 运行时自动生成的端口文件 (用于单例检测)
├── students.json          # 学生数据 JSON 文件
├── app_log.txt            # 应用日志文件
├── build.bat              # Windows 打包脚本 (可选)
├── namepicker.spec        # PyInstaller 打包配置 (可选)
├── static/                # 静态资源目录
│   ├── roll.mp3           # 滚动音效
│   ├── select.mp3         # 选中音效
│   └── click.mp3          # 点击音效
└── templates/             # 模板目录
    └── index.html         # 主页面 (HTML/CSS/JavaScript)
```

## ⚠️ 注意事项

1. **数据存储**：学生数据保存在本地 `students.json` 文件中，不会上传到任何服务器。
2. **日志记录**：应用日志保存在 `app_log.txt` 中，有助于排查运行问题。
3. **浏览器兼容性**：建议使用现代浏览器（Chrome、Firefox、Edge等）以获得最佳体验。
4. **单例检测机制**：
   - 应用使用端口文件和 HTTP ping 检测机制确保同时只有一个实例运行
   - 当检测到已有实例时，自动打开浏览器访问该实例，然后退出当前启动
5. **端口使用**：应用使用 5000-5050 范围内的端口，请确保这些端口未被其他应用占用。

## 🔧 开发者说明

- **音效系统**：使用 Web Audio API 处理音频加载和播放
- **动画系统**：结合 CSS 动画和 JavaScript 动画实现流畅效果
- **数据持久化**：使用 JSON 文件存储，通过 Flask 后端 API 管理
- **打包说明**：使用 PyInstaller 打包为独立的可执行文件

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。 