# 班级点名器

一个基于Flask的班级随机点名网页应用，具有精美的动画效果和音效反馈。

## 功能特点

- 随机点名功能，带有流畅的动画效果
- 实时音效反馈系统
- 学生名单管理（添加/删除）
- 精美的视觉效果（五彩纸屑、闪光效果等）
- 完全本地运行，无需联网
- 响应式设计，适配各种屏幕尺寸
- 支持打包为独立可执行文件

## 技术栈

- 后端：Flask
- 前端：原生JavaScript + CSS3
- 数据存储：JSON文件
- 动画：CSS3 Animations + JavaScript Animations
- 打包工具：PyInstaller

## 安装说明

1. 确保已安装Python 3.6+
2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python main.py
```

4. 在浏览器中访问：
```
http://localhost:5000
```

## 使用说明

1. 添加学生：
   - 在"添加学生"输入框中输入学生姓名
   - 点击"添加"按钮或按回车键

2. 删除学生：
   - 在学生列表中点击对应学生旁的"删除"按钮

3. 随机点名：
   - 点击顶部的"开始点名"按钮
   - 等待动画和音效完成
   - 查看被选中的学生姓名

## 项目结构

```
.
├── README.md              # 项目说明文档
├── requirements.txt       # Python依赖包列表
├── main.py               # Flask应用主文件
├── run_app.py            # 应用运行入口
├── build.bat             # Windows打包脚本
├── namepicker.spec       # PyInstaller打包配置
├── students.json         # 学生数据存储文件
├── app_log.txt           # 应用日志文件
├── 使用说明.md           # 详细使用说明
├── 打包说明.txt          # 打包相关说明
├── static/              # 静态资源目录
│   ├── roll.mp3        # 滚动音效
│   ├── select.mp3      # 选中音效
│   └── click.mp3       # 点击音效
└── templates/          # 模板目录
    └── index.html      # 主页面
```

## 注意事项

1. 学生名单保存在本地的`students.json`文件中
2. 所有音效文件都是本地存储，无需联网
3. 建议使用现代浏览器（Chrome、Firefox、Edge等）以获得最佳体验
4. 应用日志保存在`app_log.txt`中
5. 打包说明请参考`打包说明.txt`

## 开发者说明

- 音效系统使用Web Audio API
- 动画使用requestAnimationFrame实现流畅效果
- 使用CSS3 transform和animation实现视觉效果
- 数据持久化使用JSON文件存储
- 使用PyInstaller进行应用打包
- 日志系统记录应用运行状态

## 许可证

MIT License 