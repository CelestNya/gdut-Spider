# 教务系统爬虫

一个用于登录大学教务系统并获取课表信息的爬虫。

## 📁 项目结构

```
gdut-Spider/
├── demo.py              # 功能演示程序
├── login.py             # 登录模块
├── schedule.py          # 课表获取模块
├── logger.py            # 日志管理模块
├── pyproject.toml      # 项目配置文件
├── .gitignore          # Git忽略文件
├── README.md           # 项目说明文档
├── USAGE.md           # 使用指南
├── schedules/         # 课表文件夹（JSON文件）
├── cookies/           # Cookie缓存文件夹
└── logs/             # 日志文件夹
```

## 🔧 功能特性

- 自动登录教务系统（密码AES-CBC加密、会话管理）
- Cookie缓存机制，避免重复登录
- 获取课表信息（支持不同学期查询）
- 课表数据解析、格式化和保存
- 课表筛选（按教师、按星期）和统计分析
- 统一的炫彩日志管理
- 支持多用户课表管理

## 📦 安装依赖

```bash
# 使用uv安装依赖
uv sync
```

## 🚀 快速开始

```bash
# 运行功能演示
python demo.py

# 或编写自己的脚本
from login import GDUTAuth
from schedule import ScheduleManager

auth = GDUTAuth()
if auth.login_with_cache("你的学号", "你的密码"):
    schedule_manager = ScheduleManager(auth.get_session(), userid="你的学号")
    schedule_data = schedule_manager.get_schedule(2025, "Autumn")
    if schedule_data:
        schedule_manager.display_schedule(schedule_data, 2025, "Autumn")
        schedule_manager.save_schedule_to_file(schedule_data, 2025, "Autumn")
```

## 📝 代码模块说明

| 模块 | 功能 |
|------|------|
| login.py | 登录认证、Cookie管理 |
| schedule.py | 课表获取、解析、筛选、统计 |
| logger.py | 统一日志管理 |
| demo.py | 功能演示程序 |

## 📊 课表数据结构

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

## ⚠️ 注意事项

1. 请勿频繁请求，避免对服务器造成压力
2. 仅用于个人学习，请勿用于商业用途
3. 请遵守学校的相关规定
4. 请妥善保管个人账号信息

## 🔗 相关链接

- [使用指南](USAGE.md) - 详细的使用说明和示例
- [广东工业大学教务系统](https://jxfw.gdut.edu.cn/)