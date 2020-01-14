@echo off
REM 声明采用UTF-8编码
chcp 65001
echo                                      Git自动更新脚本
echo ===================================================================================
echo.
set /p change=请输入Git更新变动:
echo.
cd "C:\\Users\\98113\\Desktop\\python知识网站分享"

git add .
git commit -m %change%
git push

echo.
echo ===================================================================================
echo                                      更新完毕
echo.
pause