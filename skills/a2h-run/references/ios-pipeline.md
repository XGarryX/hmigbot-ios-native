# 运行与编译入口

主控读取 a2h-run/SKILL.md 并逐步执行原五阶段。目标 build 使用：
`python <runtime>/scripts/a2h_ios.py build --project <target>`。
先用 validate 核对真实路径；不把脚本启动当作构建成功，检查退出码、日志和 HAP。
