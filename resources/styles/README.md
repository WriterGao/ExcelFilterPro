# 样式资源

本目录包含应用程序的样式表文件。

## 文件结构

- `main.qss` - 主要样式表文件
- `dark_theme.qss` - 深色主题样式
- `light_theme.qss` - 浅色主题样式

## 样式说明

样式表基于Qt StyleSheet语法，定义了：
- 窗口和组件的颜色主题
- 字体和布局规范
- 按钮和控件的视觉效果
- 动画和过渡效果

## 使用方法

在应用程序中通过以下方式加载样式：

```python
from src.utils.helpers import resource_path

style_file = resource_path("resources/styles/main.qss")
with open(style_file, 'r', encoding='utf-8') as f:
    app.setStyleSheet(f.read())
``` 