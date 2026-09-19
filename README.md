# python-learning

Python 学习笔记和练习项目。当前包含一个使用 Tkinter 绘制的跳动粒子爱心。

![爱心动画预览](heart_preview.gif)

## 运行爱心动画

当前开发环境为 Python 3.13。代码仅使用 Python 标准库，无需安装第三方依赖；Python 环境需要包含 Tkinter 支持。

在项目目录中执行：

```bash
python beating_heart.py
```

按 `Esc` 或关闭窗口退出。可在脚本顶部调整窗口尺寸、粒子数量、心跳速度和目标帧率。

## 在 PyCharm 中使用

1. 克隆本仓库，或打开已有的本地项目目录。
2. 在项目设置中选择本地 Python 解释器，也可以创建 `.venv` 虚拟环境。
3. 右键 `beating_heart.py`，选择运行。
4. 修改文件后使用 Git 提交，再通过 Push 推送到本仓库的 `main` 分支。

`.gitignore` 已配置为忽略虚拟环境、Python 缓存和 `.idea` 本机 IDE 配置。

## 文件说明

- `beating_heart.py`：爱心动画程序。
- `heart_preview.gif`：动画预览。
- `heart_preview.png`：静态预览。
