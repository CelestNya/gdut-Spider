import requests
import json
import re
import os
from logger import logger


class ScheduleManager:
    """课表管理类"""
    
    def __init__(self, session: requests.Session = None):
        """初始化课表管理器
        
        Args:
            session: 已登录的会话对象，如果为None则只能进行文件操作
        """
        self.session = session
        self.JXFW_HOST = "jxfw.gdut.edu.cn"
        logger.debug("ScheduleManager初始化完成")

    def convert_to_xnxqdm(self, year: int, season: str) -> str:
        """将年份和季节转换为学年学期代码
        
        Args:
            year: 年份，如2025
            season: 季节，"Autumn"或"Spring"
            
        Returns:
            str: 学年学期代码，如"202501"或"202502"
        """
        season_map = {
            "Autumn": "01",
            "Spring": "02"
        }
        
        season_code = season_map.get(season, "01")
        
        # Spring学年的代码是前一年加上"02"
        if season == "Spring":
            year = year - 1
        
        xnxqdm = f"{year}{season_code}"
        logger.debug(f"转换: {year}年{season} -> {xnxqdm}")
        return xnxqdm

    def get_schedule(self, year: int, season: str) -> list:
        """获取课表信息
        
        Args:
            year: 年份，如2025
            season: 季节，"Autumn"或"Spring"
            
        Returns:
            list: 课表数据列表，如果课表未开放返回空列表
        """
        if self.session is None:
            logger.error("未提供session对象，无法获取课表")
            return []
        
        logger.section(f"获取 {year}年{season} 课表")
        
        try:
            # 转换为学年学期代码
            xnxqdm = self.convert_to_xnxqdm(year, season)
            logger.info(f"学年学期代码: {xnxqdm}")
            
            # 先访问教务系统主页，建立会话
            logger.subsection("访问教务系统主页")
            home_url = f"https://{self.JXFW_HOST}/"
            home_response = self.session.get(home_url)
            logger.debug(f"主页响应状态码: {home_response.status_code}")
            
            # 访问课表页面
            logger.subsection("访问课表页面")
            schedule_url = f"https://{self.JXFW_HOST}/xsgrkbcx!xsAllKbList.action?xnxqdm={xnxqdm}"
            logger.debug(f"课表URL: {schedule_url}")
            
            # 添加Referer头
            headers = {
                "Referer": home_url,
                "X-Requested-With": "XMLHttpRequest"
            }
            
            response = self.session.get(schedule_url, headers=headers)
            response.raise_for_status()
            
            logger.debug(f"课表响应状态码: {response.status_code}")
            logger.debug(f"响应头: {dict(response.headers)}")
            logger.debug(f"响应内容类型: {response.headers.get('Content-Type', 'unknown')}")
            
            # 检查是否课表未开放
            if self.check_schedule_not_available(response.text, year, season):
                return []
            
            # 解析课表数据
            logger.subsection("解析课表数据")
            schedule_data = self.parse_schedule_data(response.text)
            logger.info(f"解析完成，共 {len(schedule_data)} 门课程")
            
            return schedule_data
            
        except requests.RequestException as e:
            logger.failure(f"获取课表失败: {e}")
            return []

    def load_schedule_from_file(self, filepath: str) -> list:
        """从JSON文件加载课表数据
        
        Args:
            filepath: JSON文件路径
            
        Returns:
            list: 课表数据列表，如果文件不存在或解析失败返回空列表
        """
        if not os.path.exists(filepath):
            logger.error(f"文件不存在: {filepath}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                schedule_data = json.load(f)
            logger.success(f"成功加载课表文件: {filepath}")
            logger.info(f"共 {len(schedule_data)} 门课程")
            return schedule_data
        except json.JSONDecodeError as e:
            logger.failure(f"JSON解析失败: {e}")
            return []
        except Exception as e:
            logger.failure(f"加载文件失败: {e}")
            return []

    def load_schedule_by_name(self, year: int, season: str, output_dir: str = "output") -> list:
        """根据年份和季节加载课表文件
        
        Args:
            year: 年份，如2025
            season: 季节，"Autumn"或"Spring"
            output_dir: 输出文件夹，默认为"output"
            
        Returns:
            list: 课表数据列表，如果文件不存在或解析失败返回空列表
        """
        filename = f"schedule_{year}_{season}.json"
        filepath = os.path.join(output_dir, filename)
        return self.load_schedule_from_file(filepath)

    def check_schedule_not_available(self, html_content: str, year: int, season: str) -> bool:
        """检查课表是否未开放
        
        Args:
            html_content: HTML内容
            year: 年份
            season: 季节
            
        Returns:
            bool: 如果课表未开放返回True
        """
        not_available_keywords = [
            "本学期课表还未开放",
            "请稍后查询",
            "课表未开放"
        ]
        
        for keyword in not_available_keywords:
            if keyword in html_content:
                logger.warning(f"⚠️  {year}年{season}课表还未开放，请稍后查询！")
                return True
        
        return False

    def parse_schedule_data(self, html_content: str) -> list:
        """解析课表数据
        
        Args:
            html_content: HTML内容
            
        Returns:
            list: 解析后的课表数据列表
        """
        schedule_data = []
        
        # 拼音首字母到英文的映射
        key_mapping = {
            "kcmc": "course_name",
            "kcbh": "course_code",
            "jxbmc": "class_name",
            "kcrwdm": "task_code",
            "jcdm2": "periods",
            "zcs": "weeks",
            "xq": "weekday",
            "jxcdmcs": "classroom",
            "teaxms": "teachers"
        }
        
        # 使用正则表达式提取JSON数据
        # 查找所有类似 {"kcmc":"...","kcbh":"...","jxbmc":"...","kcrwdm":"...","jcdm2":"...","zcs":"...","xq":"...","jxcdmcs":"...","teaxms":"..."} 的模式
        pattern = r'\{[^}]*"kcmc"[^}]*\}'
        matches = re.findall(pattern, html_content)
        logger.debug(f"找到 {len(matches)} 个课程数据匹配")
        
        for i, match in enumerate(matches, 1):
            try:
                # 将字符串转换为字典
                data = json.loads(match)
                
                # 转换键名为英文
                converted_data = {}
                for key, value in data.items():
                    new_key = key_mapping.get(key, key)
                    converted_data[new_key] = value
                
                schedule_data.append(converted_data)
                logger.debug(f"成功解析课程 {i}: {converted_data.get('course_name', 'N/A')}")
            except json.JSONDecodeError as e:
                logger.debug(f"解析课程 {i} 失败: {e}")
                continue
        
        return schedule_data

    def format_schedule(self, schedule_data: list, year: int = None, season: str = None) -> str:
        """格式化课表数据
        
        Args:
            schedule_data: 课表数据列表
            year: 年份（可选）
            season: 季节（可选）
            
        Returns:
            str: 格式化后的课表字符串
        """
        if not schedule_data:
            if year and season:
                return f"{year}年{season}暂无课表数据"
            return "暂无课表数据"
        
        result = []
        
        # 添加标题
        if year and season:
            result.append(f"{year}年{season}课表信息")
        else:
            result.append("课表信息")
        
        # 星期映射
        week_map = {
            "1": "周一",
            "2": "周二", 
            "3": "周三",
            "4": "周四",
            "5": "周五",
            "6": "周六",
            "7": "周日"
        }
        
        for i, course in enumerate(schedule_data, 1):
            result.append(f"\n课程 {i}:")
            result.append(f"  课程名称: {course.get('course_name', 'N/A')}")
            result.append(f"  课程编号: {course.get('course_code', 'N/A')}")
            result.append(f"  教学班: {course.get('class_name', 'N/A')}")
            result.append(f"  授课教师: {course.get('teachers', 'N/A')}")
            result.append(f"  教学场地: {course.get('classroom', 'N/A')}")
            result.append(f"  星期: {week_map.get(course.get('weekday', ''), 'N/A')}")
            result.append(f"  节次: {course.get('periods', 'N/A')}")
            result.append(f"  周次: {course.get('weeks', 'N/A')}")
        
        result.append(f"\n共 {len(schedule_data)} 门课程")
        
        return "\n".join(result)

    def display_schedule(self, schedule_data: list, year: int = None, season: str = None):
        """显示格式化的课表数据
        
        Args:
            schedule_data: 课表数据列表
            year: 年份（可选）
            season: 季节（可选）
        """
        formatted = self.format_schedule(schedule_data, year, season)
        print(formatted)

    def display_schedule_from_file(self, filepath: str, year: int = None, season: str = None):
        """从文件加载并显示课表
        
        Args:
            filepath: JSON文件路径
            year: 年份（可选）
            season: 季节（可选）
        """
        schedule_data = self.load_schedule_from_file(filepath)
        if schedule_data:
            self.display_schedule(schedule_data, year, season)

    def display_schedule_by_name(self, year: int, season: str, output_dir: str = "output"):
        """根据年份和季节加载并显示课表
        
        Args:
            year: 年份，如2025
            season: 季节，"Autumn"或"Spring"
            output_dir: 输出文件夹，默认为"output"
        """
        schedule_data = self.load_schedule_by_name(year, season, output_dir)
        if schedule_data:
            self.display_schedule(schedule_data, year, season)

    def save_schedule_to_file(self, schedule_data: list, year: int, season: str, filename: str = None):
        """保存课表到文件
        
        Args:
            schedule_data: 课表数据列表
            year: 年份
            season: 季节
            filename: 文件名，如果为None则自动生成
        """
        if not schedule_data:
            logger.warning("没有课表数据可保存")
            return
        
        # 创建output文件夹
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        if filename is None:
            filename = f"schedule_{year}_{season}.json"
        
        # 构建完整文件路径
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(schedule_data, f, ensure_ascii=False, indent=2)
            logger.success(f"课表已保存到: {filepath}")
        except Exception as e:
            logger.failure(f"保存课表失败: {e}")

    def filter_courses_by_teacher(self, schedule_data: list, teacher_name: str) -> list:
        """根据教师姓名筛选课程
        
        Args:
            schedule_data: 课表数据列表
            teacher_name: 教师姓名
            
        Returns:
            list: 筛选后的课程列表
        """
        filtered = []
        for course in schedule_data:
            teachers = course.get('teachers', '')
            if teacher_name in teachers:
                filtered.append(course)
        return filtered

    def filter_courses_by_day(self, schedule_data: list, weekday: str) -> list:
        """根据星期筛选课程
        
        Args:
            schedule_data: 课表数据列表
            weekday: 星期，如"1"表示周一
            
        Returns:
            list: 筛选后的课程列表
        """
        filtered = []
        for course in schedule_data:
            course_weekday = course.get('weekday', '')
            if course_weekday == weekday:
                filtered.append(course)
        return filtered

    def get_course_statistics(self, schedule_data: list) -> dict:
        """获取课表统计信息
        
        Args:
            schedule_data: 课表数据列表
            
        Returns:
            dict: 统计信息字典
        """
        stats = {
            'total_courses': len(schedule_data),
            'unique_teachers': set(),
            'unique_classrooms': set(),
            'courses_by_day': {}
        }
        
        week_map = {
            "1": "周一",
            "2": "周二", 
            "3": "周三",
            "4": "周四",
            "5": "周五",
            "6": "周六",
            "7": "周日"
        }
        
        for course in schedule_data:
            # 统计教师
            teachers = course.get('teachers', '')
            if teachers:
                stats['unique_teachers'].add(teachers)
            
            # 统计教室
            classroom = course.get('classroom', '')
            if classroom:
                stats['unique_classrooms'].add(classroom)
            
            # 统计每天的课程数
            weekday = course.get('weekday', '')
            day_name = week_map.get(weekday, weekday)
            if day_name not in stats['courses_by_day']:
                stats['courses_by_day'][day_name] = 0
            stats['courses_by_day'][day_name] += 1
        
        # 转换set为list
        stats['unique_teachers'] = list(stats['unique_teachers'])
        stats['unique_classrooms'] = list(stats['unique_classrooms'])
        
        return stats

    def display_statistics(self, schedule_data: list):
        """显示课表统计信息
        
        Args:
            schedule_data: 课表数据列表
        """
        stats = self.get_course_statistics(schedule_data)
        
        print("\n" + "=" * 60)
        print("课表统计信息")
        print("=" * 60)
        print(f"总课程数: {stats['total_courses']}")
        print(f"教师数量: {len(stats['unique_teachers'])}")
        print(f"教室数量: {len(stats['unique_classrooms'])}")
        print("\n每天课程数:")
        for day, count in stats['courses_by_day'].items():
            print(f"  {day}: {count} 门")
        print("=" * 60)