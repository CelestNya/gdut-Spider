# 教务系统爬虫

一个用于登录大学教务系统并获取课表信息的爬虫。
大量使用vibe coding，也用于锻炼自身业务能力。

## 📁 项目结构

```
gdut-Spider/
├── main.py              # 主程序入口（功能演示）
├── login.py             # 登录模块
├── get_schedule.py       # 课表获取模块
├── logger.py            # 日志管理模块
├── requirements.txt      # 依赖包列表
├── .gitignore          # Git忽略文件
├── README.md           # 项目说明文档
├── USAGE.md           # 使用指南
├── output/            # 输出文件夹（JSON文件）
└── logs/             # 日志文件夹
```

## 🔧 功能特性

- 自动登录教务系统（密码AES-CBC加密、会话管理）
- 获取课表信息（支持不同学期查询）
- 课表数据解析、格式化和保存
- 课表筛选（按教师、按星期）和统计分析
- 统一的炫彩日志管理
- 灵活的文件操作模式

## 📦 安装依赖

### 使用uv（推荐）
```bash
uv sync
```

### 使用pip
```bash
pip install -r requirements.txt
```

### 手动安装
```bash
pip install requests beautifulsoup4 pycryptodome
```

## 🚀 快速开始

### 1. 运行功能演示
```bash
python main.py
```

程序会显示功能菜单，你可以选择要演示的功能：
- 登录并获取课表
- 从文件加载课表
- 按教师筛选课程
- 按星期筛选课程
- 课表统计
- 格式化选项
- 获取多个学期的课表

### 2. 基本使用示例

```python
from login import GDUTAuth
from get_schedule import ScheduleManager
from logger import logger

# 1. 登录
auth = GDUTAuth()
if auth.login("你的学号", "你的密码"):
    logger.success("登录成功！")
    
    # 2. 创建课表管理器
    schedule_manager = ScheduleManager(auth.get_session())
    
    # 3. 获取课表
    schedule_data = schedule_manager.get_schedule(2025, "Autumn")
    
    if schedule_data:
        # 4. 格式化显示
        formatted = schedule_manager.format_schedule(schedule_data, 2025, "Autumn")
        print(formatted)
        
        # 5. 保存到文件
        schedule_manager.save_schedule_to_file(schedule_data, 2025, "Autumn")
```

## 📝 代码模块说明

### logger.py - 日志管理模块

提供统一的炫彩日志管理功能，支持多种颜色和日志级别。日志同时输出到控制台（炫彩）和文件（普通格式）。

### login.py - 登录模块

处理教务系统登录功能，包括密码AES-CBC加密和会话管理（JSESSIONID）。

### get_schedule.py - 课表获取模块

处理课表数据的获取、解析、筛选和统计。支持从系统获取或从JSON文件加载课表，提供多种筛选和统计功能。

### main.py - 主程序

程序入口，提供完整的功能演示和交互式菜单。

## 📊 课表数据结构

每门课程包含以下信息：

```json
{
  "course_name": "课程名称",
  "course_code": "课程编号",
  "class_name": "教学班",
  "task_code": "课程任务代码",
  "periods": "节次",
  "weeks": "周次",
  "weekday": "星期",
  "classroom": "教学场地",
  "teachers": "授课教师"
}
```

## 🔐 安全说明

- 密码使用AES-CBC加密传输
- 会话使用Cookie管理
- 不存储敏感信息
- 日志文件保存在本地

## ⚠️ 注意事项

1. 请勿频繁请求，避免对服务器造成压力
2. 仅用于个人学习，请勿用于商业用途
3. 请遵守学校的相关规定
4. 课表数据可能因学校系统更新而变化
5. 请妥善保管个人账号信息

## 🐛 故障排除

### 登录失败
检查用户名密码、网络连接和教务系统访问状态，查看日志获取详细错误信息。

### 课表获取失败
确认登录状态、学期代码正确性，检查课表是否已开放，查看日志获取详细错误信息。

### 依赖包问题
```bash
uv sync
```

### 文件不存在
确认output文件夹中存在对应的JSON文件，检查文件名格式（schedule_2025_Autumn.json）和参数是否正确。

## 📄 许可证

本项目仅供学习交流使用，请勿用于商业用途。

如有问题或建议，请通过Issue反馈。

## 🔗 相关链接

- [使用指南](USAGE.md) - 详细的使用说明
- [广东工业大学教务系统](https://jxfw.gdut.edu.cn/)