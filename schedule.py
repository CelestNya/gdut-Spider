import requests
import json
import re
import os
from datetime import datetime
from logger import logger


class ScheduleManager:
    """课表管理类"""

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

        user_dir = os.path.dirname(filepath)
        os.makedirs(user_dir, exist_ok=True)

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