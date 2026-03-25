from login import GDUTAuth
from get_schedule import ScheduleManager
from logger import logger

def login():
    """统一登录函数"""
    auth = GDUTAuth()
    if auth.login(USERNAME, PASSWORD):
        logger.success("登录成功！")
        return auth
    else:
        logger.failure("登录失败！")
        return None


def demo_login_and_fetch():
    """演示登录并获取课表"""
    logger.section("演示1：登录并获取课表")
    
    auth = login()
    if not auth:
        return
    
    schedule_manager = ScheduleManager(auth.get_session(), userid=USERNAME)
    year, season = 2025, "Autumn"
    schedule_data = schedule_manager.get_schedule(year, season)
    
    if schedule_data:
        schedule_manager.display_schedule(schedule_data, year, season)
        schedule_manager.save_schedule_to_file(schedule_data, year, season)
    else:
        logger.info(f"{year}年{season}课表未开放或无数据")


def demo_load_from_file():
    """演示从文件加载课表"""
    logger.section("演示2：从文件加载课表")
    
    schedule_manager = ScheduleManager()
    year, season = 2025, "Autumn"
    schedule_data = schedule_manager.load_schedule_by_name(year, season)
    
    if schedule_data:
        schedule_manager.display_schedule(schedule_data, year, season)
    else:
        logger.info(f"未找到 {year}年{season} 课表文件")


def demo_filter_by_teacher():
    """演示按教师筛选课程"""
    logger.section("演示3：按教师筛选课程")
    
    schedule_manager = ScheduleManager()
    schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")
    
    if schedule_data:
        teacher_name = "韩晓卓"
        teacher_courses = schedule_manager.filter_courses_by_teacher(schedule_data, teacher_name)
        
        if teacher_courses:
            logger.info(f"教师 {teacher_name} 的课程：")
            schedule_manager.display_schedule(teacher_courses)
        else:
            logger.info(f"未找到教师 {teacher_name} 的课程")


def demo_filter_by_day():
    """演示按星期筛选课程"""
    logger.section("演示4：按星期筛选课程")
    
    schedule_manager = ScheduleManager()
    schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")
    
    if schedule_data:
        weekday = "1"
        day_courses = schedule_manager.filter_courses_by_day(schedule_data, weekday)
        
        if day_courses:
            logger.info("周一的课程：")
            schedule_manager.display_schedule(day_courses)
        else:
            logger.info("周一没有课程")


def demo_statistics():
    """演示课表统计"""
    logger.section("演示5：课表统计")
    
    schedule_manager = ScheduleManager()
    schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")
    
    if schedule_data:
        schedule_manager.display_statistics(schedule_data)


def demo_format_options():
    """演示格式化选项"""
    logger.section("演示6：格式化选项")
    
    schedule_manager = ScheduleManager()
    schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")
    
    if schedule_data:
        logger.subsection("带年份和季节的格式化")
        print(schedule_manager.format_schedule(schedule_data, 2025, "Autumn"))
        
        logger.subsection("不带年份和季节的格式化")
        print(schedule_manager.format_schedule(schedule_data))


def demo_multiple_terms():
    """演示获取多个学期的课表"""
    logger.section("演示7：获取多个学期的课表")
    
    auth = login()
    if not auth:
        return
    
    schedule_manager = ScheduleManager(auth.get_session(), userid=USERNAME)
    test_cases = [
        (2025, "Autumn"),
        (2026, "Spring"),
        (2026, "Autumn"),
    ]
    
    for year, season in test_cases:
        logger.subsection(f"获取 {year}年{season} 课表")
        schedule_data = schedule_manager.get_schedule(year, season)
        
        if schedule_data:
            logger.info(f"共 {len(schedule_data)} 门课程")
            schedule_manager.save_schedule_to_file(schedule_data, year, season)
        else:
            logger.info(f"{year}年{season}课表未开放或无数据")


def demo_list_schedules():
    """演示列出所有已保存的课表"""
    logger.section("演示8：列出所有已保存的课表")
    
    schedule_manager = ScheduleManager()
    schedule_manager.display_all_schedules()


def main():
    """主函数"""
    logger.section("广工教务系统爬虫 - 功能演示")
    
    # 登录凭据

    global USERNAME, PASSWORD
    USERNAME, PASSWORD = "", ""
    
    
    print("\n" + "=" * 60)
    print("功能演示菜单")
    print("=" * 60)
    print("1. 登录并获取课表")
    print("2. 从文件加载课表")
    print("3. 按教师筛选课程")
    print("4. 按星期筛选课程")
    print("5. 课表统计")
    print("6. 格式化选项")
    print("7. 获取多个学期的课表")
    print("8. 列出所有已保存的课表")
    print("0. 运行所有演示")
    print("=" * 60)
    
    choice = input("\n请选择演示功能 (0-8): ").strip()
    
    demos = {
        "1": demo_login_and_fetch,
        "2": demo_load_from_file,
        "3": demo_filter_by_teacher,
        "4": demo_filter_by_day,
        "5": demo_statistics,
        "6": demo_format_options,
        "7": demo_multiple_terms,
        "8": demo_list_schedules,
    }
    
    if choice == "0":
        for demo in demos.values():
            demo()
            print("\n")
    elif choice in demos:
        demos[choice]()
    else:
        logger.warning("无效的选择！")
    
    logger.section("演示结束")


if __name__ == "__main__":
    main()