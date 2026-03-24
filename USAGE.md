# 广工教务系统爬虫 - 使用指南

本指南将帮助你快速上手使用广工教务系统爬虫。

## 📦 安装

### 1. 克隆或下载项目
```bash
cd gdut-spider
```

### 2. 安装依赖
```bash
# 使用uv（推荐）
uv sync
```

## 🚀 快速开始

### 方式1：运行交互式演示
```bash
python main.py
```

程序会显示功能菜单，输入对应数字即可体验不同功能。

### 方式2：编写自己的脚本

#### 基本使用 - 登录并获取课表
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
        # 4. 显示课表
        schedule_manager.display_schedule(schedule_data, 2025, "Autumn")
        
        # 5. 保存到文件
        schedule_manager.save_schedule_to_file(schedule_data, 2025, "Autumn")
```

#### 从文件加载课表
```python
from get_schedule import ScheduleManager

# 创建课表管理器（不需要登录）
schedule_manager = ScheduleManager()

# 从文件加载并显示
schedule_manager.display_schedule_by_name(2025, "Autumn")
```

#### 按教师筛选课程
```python
from get_schedule import ScheduleManager

schedule_manager = ScheduleManager()

# 加载课表
schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")

# 筛选特定教师的课程
teacher_courses = schedule_manager.filter_courses_by_teacher(schedule_data, "韩晓卓")

# 显示筛选结果
schedule_manager.display_schedule(teacher_courses)
```

#### 按星期筛选课程
```python
from get_schedule import ScheduleManager

schedule_manager = ScheduleManager()

# 加载课表
schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")

# 筛选周一的课程（"1"表示周一）
monday_courses = schedule_manager.filter_courses_by_day(schedule_data, "1")

# 显示筛选结果
schedule_manager.display_schedule(monday_courses)
```

#### 查看课表统计
```python
from get_schedule import ScheduleManager

schedule_manager = ScheduleManager()

# 加载课表
schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")

# 显示统计信息
schedule_manager.display_statistics(schedule_data)
```

## 📖 常用功能

### 1. 获取不同学期的课表

```python
from login import GDUTAuth
from get_schedule import ScheduleManager

auth = GDUTAuth()
if auth.login("你的学号", "你的密码"):
    schedule_manager = ScheduleManager(auth.get_session())
    
    # 2025年秋季
    schedule_manager.display_schedule_by_name(2025, "Autumn")
    
    # 2026年春季
    schedule_manager.display_schedule_by_name(2026, "Spring")
    
    # 2026年秋季（可能还未开放）
    schedule_manager.display_schedule_by_name(2026, "Autumn")
```

### 2. 保存多个学期的课表

```python
from login import GDUTAuth
from get_schedule import ScheduleManager

auth = GDUTAuth()
if auth.login("你的学号", "你的密码"):
    schedule_manager = ScheduleManager(auth.get_session())
    
    # 获取并保存多个学期
    terms = [
        (2025, "Autumn"),
        (2026, "Spring"),
        (2026, "Autumn")
    ]
    
    for year, season in terms:
        schedule_data = schedule_manager.get_schedule(year, season)
        if schedule_data:
            schedule_manager.save_schedule_to_file(schedule_data, year, season)
```

### 3. 查找特定课程

```python
from get_schedule import ScheduleManager

schedule_manager = ScheduleManager()

# 加载课表
schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")

# 查找包含特定关键词的课程
for course in schedule_data:
    if "数学" in course['course_name']:
        print(f"找到数学课程: {course['course_name']}")
        print(f"  教师: {course['teachers']}")
        print(f"  教室: {course['classroom']}")
        print(f"  时间: 周{course['weekday']} {course['periods']}节")
```

### 4. 生成课表报告

```python
from get_schedule import ScheduleManager

schedule_manager = ScheduleManager()

# 加载课表
schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")

# 显示统计信息
schedule_manager.display_statistics(schedule_data)

# 按星期分组显示
week_map = {"1": "周一", "2": "周二", "3": "周三", 
            "4": "周四", "5": "周五", "6": "周六", "7": "周日"}

for day in ["1", "2", "3", "4", "5", "6", "7"]:
    day_courses = schedule_manager.filter_courses_by_day(schedule_data, day)
    if day_courses:
        print(f"\n{week_map[day]}的课程：")
        schedule_manager.display_schedule(day_courses)
```

## 🎯 使用技巧

### 技巧1：批量处理多个学期
```python
# 定义要处理的学期列表
terms = [(2025, "Autumn"), (2026, "Spring")]

# 批量获取并保存
for year, season in terms:
    schedule_data = schedule_manager.get_schedule(year, season)
    if schedule_data:
        schedule_manager.save_schedule_to_file(schedule_data, year, season)
```

### 技巧2：组合筛选条件
```python
# 先按教师筛选
teacher_courses = schedule_manager.filter_courses_by_teacher(schedule_data, "张老师")

# 再从结果中按星期筛选
monday_courses = schedule_manager.filter_courses_by_day(teacher_courses, "1")
```

### 技巧3：自定义格式化输出
```python
# 加载课表
schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")

# 自定义格式化
for course in schedule_data:
    print(f"{course['course_name']} - {course['teachers']}")
    print(f"  时间: 周{course['weekday']} {course['periods']}节")
    print(f"  地点: {course['classroom']}")
    print(f"  周次: {course['weeks']}")
    print()
```

### 技巧4：导出为CSV格式
```python
import csv
from get_schedule import ScheduleManager

schedule_manager = ScheduleManager()
schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")

# 导出到CSV
with open('schedule.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=schedule_data[0].keys())
    writer.writeheader()
    writer.writerows(schedule_data)

print("已导出到 schedule.csv")
```

## 📊 数据结构

### 课程对象
每门课程包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| course_name | str | 课程名称 |
| course_code | str | 课程编号 |
| class_name | str | 教学班 |
| task_code | str | 课程任务代码 |
| periods | str | 节次（如"08,09"） |
| weeks | str | 周次（如"1,2,3"） |
| weekday | str | 星期（"1"=周一，"7"=周日） |
| classroom | str | 教学场地 |
| teachers | str | 授课教师 |

### 星期代码
- "1": 周一
- "2": 周二
- "3": 周三
- "4": 周四
- "5": 周五
- "6": 周六
- "7": 周日

### 季节代码
- "Autumn": 秋季
- "Spring": 春季

## 🔧 配置说明

### 修改登录信息
在代码中找到以下部分并修改：
```python
username = "你的学号"
password = "你的密码"
```

### 修改输出目录
默认输出目录为 `output/`，可以在代码中修改：
```python
output_dir = "output"  # 修改为你想要的目录
```

### 修改日志级别
在 `logger.py` 中修改：
```python
logger = Logger("GDUTSpider", level=logging.DEBUG)  # 显示调试信息
logger = Logger("GDUTSpider", level=logging.INFO)   # 只显示基本信息
logger = Logger("GDUTSpider", level=logging.WARNING) # 只显示警告和错误
```

## 🐛 常见问题

### Q: 登录失败怎么办？
A: 检查以下几点：
1. 学号和密码是否正确
2. 网络连接是否正常
3. 教务系统是否可以访问
4. 查看日志文件了解详细错误

### Q: 课表获取失败？
A: 可能的原因：
1. 该学期课表还未开放
2. 网络连接问题
3. 登录状态已过期

### Q: 如何查看详细日志？
A: 查看 `logs/` 文件夹中的日志文件，文件名包含时间戳。

### Q: JSON文件保存在哪里？
A: 默认保存在 `output/` 文件夹中，文件名格式为 `schedule_2025_Autumn.json`。

### Q: 可以离线使用吗？
A: 可以！如果已经保存了JSON文件，可以不登录直接加载：
```python
schedule_manager = ScheduleManager()
schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")
```

## 📚 更多示例

查看 `main.py` 文件，包含了所有功能的完整示例。

## 🆘 获取帮助

如果遇到问题：
1. 查看日志文件（logs/文件夹）
2. 查看README.md了解更多信息
3. 运行 `python main.py` 查看功能演示

## 📄 许可证

本项目仅供学习交流使用，请勿用于商业用途。