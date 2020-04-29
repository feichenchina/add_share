@echo off
REM 声明采用UTF-8编码
chcp 65001
echo                                      Git自动更新脚本
echo ===================================================================================
cd /d %~dp0

echo.
set /p change=请输入Git更新变动（message内容）:
echo.

git add .
git commit -m %change%
git push

echo.
echo ===================================================================================
echo                                      更新完毕
echo.
pause