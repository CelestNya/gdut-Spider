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

### 核心功能
- ✅ 自动登录教务系统
- ✅ 密码AES-CBC加密
- ✅ 会话管理（JSESSIONID）
- ✅ 获取课表信息
- ✅ 支持不同学期的课表查询
- ✅ 课表数据解析和格式化
- ✅ 统一的炫彩日志管理
- ✅ 课表数据保存到JSON文件

### 高级功能
- ✅ 从JSON文件加载课表
- ✅ 按教师筛选课程
- ✅ 按星期筛选课程
- ✅ 课表统计分析
- ✅ 灵活的格式化选项
- ✅ 独立的文件操作模式

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

提供统一的炫彩日志管理功能，支持多种颜色和日志级别。

**主要类：**
- `Logger`: 日志管理类
- `ColoredFormatter`: 炫彩日志格式化器

**主要方法：**
- `debug(message)`: 调试日志（灰色）
- `info(message)`: 信息日志（橙色）
- `warning(message)`: 警告日志（亮黄色）
- `error(message)`: 错误日志（亮红色）
- `success(message)`: 成功日志（亮绿色）
- `failure(message)`: 失败日志（亮红色）
- `section(title)`: 分节标题（亮青色）
- `subsection(title)`: 小节标题（亮蓝色）
- `highlight(message)`: 高亮消息（亮黄色）
- `important(message)`: 重要消息（亮紫色）
- `pink(message)`: 粉色消息
- `lime(message)`: 青柠色消息
- `teal(message)`: 蓝绿色消息

**日志输出：**
- 控制台：炫彩输出
- 文件：普通格式（保存在logs文件夹）

### login.py - 登录模块

处理教务系统登录功能，包括密码加密和会话管理。

**主要类：**
- `GDUTCrypto`: 密码加密工具类
- `GDUTAuth`: 教务系统认证类

**主要方法：**
- `GDUTCrypto.encrypt(password, salt)`: AES-CBC加密密码
- `GDUTAuth.login(username, password)`: 登录教务系统
- `GDUTAuth.check_login_success()`: 检查登录状态
- `GDUTAuth.get_session()`: 获取会话对象

**登录流程：**
1. 获取登录页面
2. 提取加密盐值
3. 加密密码
4. 发送登录请求
5. 验证登录状态（通过JSESSIONID）

### get_schedule.py - 课表获取模块

处理课表数据的获取、解析、筛选和统计。

**主要类：**
- `ScheduleManager`: 课表管理类

**主要方法：**

#### 数据获取
- `get_schedule(year, season)`: 获取课表信息
- `load_schedule_from_file(filepath)`: 从JSON文件加载课表
- `load_schedule_by_name(year, season, output_dir)`: 根据年份和季节加载课表

#### 数据显示
- `format_schedule(schedule_data, year, season)`: 格式化课表数据
- `display_schedule(schedule_data, year, season)`: 显示格式化的课表
- `display_schedule_from_file(filepath, year, season)`: 从文件加载并显示课表
- `display_schedule_by_name(year, season, output_dir)`: 根据年份和季节加载并显示课表

#### 数据筛选
- `filter_courses_by_teacher(schedule_data, teacher_name)`: 根据教师姓名筛选课程
- `filter_courses_by_day(schedule_data, weekday)`: 根据星期筛选课程

#### 数据统计
- `get_course_statistics(schedule_data)`: 获取课表统计信息
- `display_statistics(schedule_data)`: 显示课表统计信息

#### 数据保存
- `save_schedule_to_file(schedule_data, year, season, filename)`: 保存课表到文件

### main.py - 主程序

程序入口，提供完整的功能演示和交互式菜单。

**演示功能：**
1. 登录并获取课表
2. 从文件加载课表
3. 按教师筛选课程
4. 按星期筛选课程
5. 课表统计
6. 格式化选项
7. 获取多个学期的课表

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

**问题：** 登录失败
**解决方案：**
- 检查用户名和密码是否正确
- 确认网络连接正常
- 查看日志输出的详细错误信息
- 检查教务系统是否正常访问

### 课表获取失败

**问题：** 获取课表失败
**解决方案：**
- 确认已成功登录
- 检查学期代码是否正确
- 查看是否课表还未开放
- 查看日志输出的详细错误信息

### 依赖包问题

**问题：** 导入模块失败
**解决方案：**
```bash
# 使用uv
uv sync
```

### 文件不存在

**问题：** 加载JSON文件时提示文件不存在
**解决方案：**
- 确认output文件夹中存在对应的JSON文件
- 检查文件名格式是否正确（schedule_2025_Autumn.json）
- 确认年份和季节参数是否正确

## 📄 许可证

本项目仅供学习交流使用，请勿用于商业用途。

## 📞 联系方式

如有问题或建议，请通过Issue反馈。

## 🔗 相关链接

- [使用指南](USAGE.md) - 详细的使用说明
- [广东工业大学教务系统](https://jxfw.gdut.edu.cn/)