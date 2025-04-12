@echo off
chcp 65001 > nul
echo 正在打包班级点名器应用...

REM 清理旧的打包文件
echo 清理旧文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
echo 清理完成！

REM 确保app_log.txt文件存在
echo 创建初始日志文件...
echo 打包时间: %date% %time% > app_log.txt
echo 日志文件已创建!

REM 确保已安装所需的依赖
echo 安装依赖...
pip install pyinstaller flask

REM 执行打包命令
echo 开始打包...
pyinstaller "namepicker.spec" --noconfirm

echo.
echo 打包完成!
echo 可执行文件位于 dist/ClassRollCall 目录下
echo.
echo 使用方法:
echo 1. 将整个 dist/ClassRollCall 目录复制到目标电脑
echo 2. 双击 班级点名器.exe 文件运行程序
echo 3. 程序会自动打开浏览器显示界面
echo 4. 如有问题，请查看 app_log.txt 文件获取详细信息
echo.

REM 复制使用说明到dist目录
copy "使用说明.md" "dist\ClassRollCall\"
echo 已复制使用说明文件到发布目录

REM 暂停查看结果
pause 