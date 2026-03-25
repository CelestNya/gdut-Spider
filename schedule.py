import requests
import json
import re
import os
from datetime import datetime
from logger import logger


class ScheduleManager:
    """课表管理类"""
    
    WEEK_MAP = {
        "1": "周一",
        "2": "周二", 
        "3": "周三",
        "4": "周四",
        "5": "周五",
        "6": "周六",
        "7": "周日"
    }
    
    SEASON_MAP = {
        "Autumn": "01",
        "Spring": "02"
    }
    
    KEY_MAPPING = {
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
    
    NOT_AVAILABLE_KEYWORDS = [
        "本学期课表还未开放",
        "请稍后查询",
        "课表未开放"
    ]
    
    def __init__(self, session: requests.Session = None, userid: str = None):
        """初始化课表管理器
        
        Args:
            session: 已登录的会话对象，如果为None则只能进行文件操作
            userid: 用户账号ID
        """
        self.session = session
        self.userid = userid
        self.JXFW_HOST = "jxfw.gdut.edu.cn"

    def _convert_to_xnxqdm(self, year: int, season: str) -> str:
        """将年份和季节转换为学年学期代码
        
        Args:
            year: 年份，如2025
            season: 季节，"Autumn"或"Spring"
            
        Returns:
            str: 学年学期代码，如"202501"或"202502"
        """
        season_code = self.SEASON_MAP.get(season, "01")
        
        if season == "Spring":
            year = year - 1
        
        return f"{year}{season_code}"

    def _check_schedule_not_available(self, html_content: str, year: int, season: str) -> bool:
        """检查课表是否未开放
        
        Args:
            html_content: HTML内容
            year: 年份
            season: 季节
            
        Returns:
            bool: 如果课表未开放返回True
        """
        for keyword in self.NOT_AVAILABLE_KEYWORDS:
            if keyword in html_content:
                logger.warning(f"⚠️  {year}年{season}课表还未开放，请稍后查询！")
                return True
        return False

    def _parse_schedule_data(self, html_content: str) -> list:
        """解析课表数据
        
        Args:
            html_content: HTML内容
            
        Returns:
            list: 解析后的课表数据列表
        """
        schedule_data = []
        pattern = r'\{[^}]*"kcmc"[^}]*\}'
        matches = re.findall(pattern, html_content)
        
        for match in matches:
            try:
                data = json.loads(match)
                converted_data = {
                    self.KEY_MAPPING.get(key, key): value 
                    for key, value in data.items()
                }
                schedule_data.append(converted_data)
            except json.JSONDecodeError:
                continue
        
        return schedule_data

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
            xnxqdm = self._convert_to_xnxqdm(year, season)
            logger.info(f"学年学期代码: {xnxqdm}")
            
            logger.subsection("访问教务系统主页")
            home_url = f"https://{self.JXFW_HOST}/"
            self.session.get(home_url)
            
            logger.subsection("访问课表页面")
            schedule_url = f"https://{self.JXFW_HOST}/xsgrkbcx!xsAllKbList.action?xnxqdm={xnxqdm}"
            headers = {
                "Referer": home_url,
                "X-Requested-With": "XMLHttpRequest"
            }
            
            response = self.session.get(schedule_url, headers=headers)
            response.raise_for_status()
            
            if self._check_schedule_not_available(response.text, year, season):
                return []
            
            logger.subsection("解析课表数据")
            schedule_data = self._parse_schedule_data(response.text)
            logger.info(f"解析完成，共 {len(schedule_data)} 门课程")
            
            return schedule_data
            
        except requests.RequestException as e:
            logger.failure(f"获取课表失败: {e}")
            return []

    def _get_schedule_file(self, year: int, season: str) -> str:
        """获取课表文件路径
        
        Args:
            year: 年份
            season: 季节
            
        Returns:
            str: 文件路径
        """
        if not self.userid:
            return None
        
        filename = f"schedule_{year}_{season}.json"
        user_dir = os.path.join("schedules", self.userid)
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, filename)

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
                data = json.load(f)
            
            schedule_data = data.get('schedule', [])
            metadata = data.get('metadata', {})
            logger.success(f"成功加载课表文件: {filepath}")
            logger.info(f"账号: {metadata.get('userid', 'unknown')}")
            logger.info(f"更新时间: {metadata.get('update_time', 'unknown')}")
            logger.info(f"共 {len(schedule_data)} 门课程")
            return schedule_data
        except json.JSONDecodeError as e:
            logger.failure(f"JSON解析失败: {e}")
            return []
        except Exception as e:
            logger.failure(f"加载文件失败: {e}")
            return []

    def load_schedule_by_name(self, year: int, season: str) -> list:
        """根据年份和季节加载课表文件
        
        Args:
            year: 年份，如2025
            season: 季节，"Autumn"或"Spring"
            
        Returns:
            list: 课表数据列表，如果文件不存在或解析失败返回空列表
        """
        if not self.userid:
            logger.warning("未提供userid，无法加载课表")
            return []
        
        filepath = self._get_schedule_file(year, season)
        if filepath:
            return self.load_schedule_from_file(filepath)
        return []

    def list_all_schedules(self) -> list:
        """列出所有已保存的课表文件
        
        Returns:
            list: 课表元数据列表，每个元素包含文件名、账号、更新时间等信息
        """
        schedules = []
        output_dir = "schedules"
        
        if not os.path.exists(output_dir):
            logger.warning(f"输出文件夹不存在: {output_dir}")
            return schedules
        
        for userid in os.listdir(output_dir):
            user_dir = os.path.join(output_dir, userid)
            if not os.path.isdir(user_dir):
                continue
            
            for filename in os.listdir(user_dir):
                if filename.startswith("schedule_") and filename.endswith(".json"):
                    filepath = os.path.join(user_dir, filename)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        metadata = data.get('metadata', {})
                        schedules.append({
                            "filename": filename,
                            "filepath": filepath,
                            "userid": metadata.get('userid', userid),
                            "update_time": metadata.get('update_time', 'unknown'),
                            "year": metadata.get('year', 'unknown'),
                            "season": metadata.get('season', 'unknown'),
                            "course_count": metadata.get('course_count', 0)
                        })
                    except Exception as e:
                        logger.warning(f"读取文件 {filepath} 失败: {e}")
                        continue
        
        schedules.sort(key=lambda x: x['update_time'], reverse=True)
        return schedules

    def display_all_schedules(self):
        """显示所有已保存的课表"""
        schedules = self.list_all_schedules()
        
        if not schedules:
            logger.info("没有找到已保存的课表文件")
            return
        
        logger.section("已保存的课表列表")
        
        for i, schedule in enumerate(schedules, 1):
            print(f"\n课表 {i}:")
            print(f"  文件名: {schedule['filename']}")
            print(f"  账号: {schedule['userid']}")
            print(f"  学期: {schedule['year']}年{schedule['season']}")
            print(f"  更新时间: {schedule['update_time']}")
            print(f"  课程数量: {schedule['course_count']} 门")
            print(f"  文件路径: {schedule['filepath']}")
        
        print(f"\n共找到 {len(schedules)} 个课表文件")

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
        
        if year and season:
            result.append(f"{year}年{season}课表信息")
        else:
            result.append("课表信息")
        
        for i, course in enumerate(schedule_data, 1):
            result.append(f"\n课程 {i}:")
            result.append(f"  课程名称: {course.get('course_name', 'N/A')}")
            result.append(f"  课程编号: {course.get('course_code', 'N/A')}")
            result.append(f"  教学班: {course.get('class_name', 'N/A')}")
            result.append(f"  授课教师: {course.get('teachers', 'N/A')}")
            result.append(f"  教学场地: {course.get('classroom', 'N/A')}")
            result.append(f"  星期: {self.WEEK_MAP.get(course.get('weekday', ''), 'N/A')}")
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
        print(self.format_schedule(schedule_data, year, season))

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
        
        if not self.userid:
            logger.warning("未提供userid，无法保存课表")
            return
        
        filepath = self._get_schedule_file(year, season)
        if not filepath:
            return
        
        if filename:
            user_dir = os.path.join("schedules", self.userid)
            filepath = os.path.join(user_dir, filename)
        
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        save_data = {
            "metadata": {
                "userid": self.userid,
                "update_time": update_time,
                "year": year,
                "season": season,
                "course_count": len(schedule_data)
            },
            "schedule": schedule_data
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
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
        return [course for course in schedule_data 
                if teacher_name in course.get('teachers', '')]

    def filter_courses_by_day(self, schedule_data: list, weekday: str) -> list:
        """根据星期筛选课程
        
        Args:
            schedule_data: 课表数据列表
            weekday: 星期，如"1"表示周一
            
        Returns:
            list: 筛选后的课程列表
        """
        return [course for course in schedule_data 
                if course.get('weekday', '') == weekday]

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
        
        for course in schedule_data:
            teachers = course.get('teachers', '')
            if teachers:
                stats['unique_teachers'].add(teachers)
            
            classroom = course.get('classroom', '')
            if classroom:
                stats['unique_classrooms'].add(classroom)
            
            weekday = course.get('weekday', '')
            day_name = self.WEEK_MAP.get(weekday, weekday)
            stats['courses_by_day'][day_name] = stats['courses_by_day'].get(day_name, 0) + 1
        
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