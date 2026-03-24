from login import GDUTAuth
from get_schedule import ScheduleManager
from logger import logger


def demo_login_and_fetch():
    """演示登录和获取课表"""
    logger.section("演示1：登录并获取课表")
    
    # 创建认证对象
    auth = GDUTAuth()
    
    # 输入登录信息
    username = "student_id"
    password = "student_password"
    
    # 登录
    if auth.login(username, password):
        logger.success("登录成功！")
        
        # 创建课表管理器
        schedule_manager = ScheduleManager(auth.get_session())
        
        # 获取2025年秋季课表
        year, season = 2025, "Autumn"
        schedule_data = schedule_manager.get_schedule(year, season)
        
        if schedule_data:
            # 显示课表
            schedule_manager.display_schedule(schedule_data, year, season)
            
            # 保存到文件
            schedule_manager.save_schedule_to_file(schedule_data, year, season)
        else:
            logger.info(f"{year}年{season}课表未开放或无数据")
    else:
        logger.failure("登录失败！")


def demo_load_from_file():
    """演示从文件加载课表"""
    logger.section("演示2：从文件加载课表")
    
    # 创建课表管理器（不需要session）
    schedule_manager = ScheduleManager()
    
    # 从文件加载课表
    year, season = 2025, "Autumn"
    schedule_data = schedule_manager.load_schedule_by_name(year, season)
    
    if schedule_data:
        # 显示课表
        schedule_manager.display_schedule(schedule_data, year, season)
    else:
        logger.info(f"未找到 {year}年{season} 课表文件")


def demo_filter_by_teacher():
    """演示按教师筛选课程"""
    logger.section("演示3：按教师筛选课程")
    
    # 创建课表管理器
    schedule_manager = ScheduleManager()
    
    # 加载课表
    schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")
    
    if schedule_data:
        # 筛选特定教师的课程
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
    
    # 创建课表管理器
    schedule_manager = ScheduleManager()
    
    # 加载课表
    schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")
    
    if schedule_data:
        # 筛选周一的课程
        weekday = "1"  # 周一
        day_courses = schedule_manager.filter_courses_by_day(schedule_data, weekday)
        
        if day_courses:
            logger.info("周一的课程：")
            schedule_manager.display_schedule(day_courses)
        else:
            logger.info("周一没有课程")


def demo_statistics():
    """演示课表统计"""
    logger.section("演示5：课表统计")
    
    # 创建课表管理器
    schedule_manager = ScheduleManager()
    
    # 加载课表
    schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")
    
    if schedule_data:
        # 显示统计信息
        schedule_manager.display_statistics(schedule_data)


def demo_format_options():
    """演示格式化选项"""
    logger.section("演示6：格式化选项")
    
    # 创建课表管理器
    schedule_manager = ScheduleManager()
    
    # 加载课表
    schedule_data = schedule_manager.load_schedule_by_name(2025, "Autumn")
    
    if schedule_data:
        # 带年份和季节的格式化
        logger.subsection("带年份和季节的格式化")
        formatted = schedule_manager.format_schedule(schedule_data, 2025, "Autumn")
        print(formatted)
        
        # 不带年份和季节的格式化
        logger.subsection("不带年份和季节的格式化")
        formatted = schedule_manager.format_schedule(schedule_data)
        print(formatted)


def demo_multiple_terms():
    """演示获取多个学期的课表"""
    logger.section("演示7：获取多个学期的课表")
    
    # 创建认证对象
    auth = GDUTAuth()
    
    # 输入登录信息
    username = "student_id"
    password = "student_password"
    
    # 登录
    if auth.login(username, password):
        logger.success("登录成功！")
        
        # 创建课表管理器
        schedule_manager = ScheduleManager(auth.get_session())
        
        # 测试获取不同学期的课表
        test_cases = [
            (2025, "Autumn"),  # 202501
            (2026, "Spring"),  # 202502
            (2026, "Autumn"),  # 202601 - 应该还未开放
        ]
        
        for year, season in test_cases:
            logger.subsection(f"获取 {year}年{season} 课表")
            
            # 获取课表
            schedule_data = schedule_manager.get_schedule(year, season)
            
            if schedule_data:
                # 显示简要信息
                logger.info(f"共 {len(schedule_data)} 门课程")
                
                # 保存到文件
                schedule_manager.save_schedule_to_file(schedule_data, year, season)
            else:
                logger.info(f"{year}年{season}课表未开放或无数据")
    else:
        logger.failure("登录失败！")


def main():
    """主函数 - 演示所有功能"""
    logger.section("广工教务系统爬虫 - 功能演示")
    
    # 演示菜单
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
    print("0. 运行所有演示")
    print("=" * 60)
    
    # 获取用户选择
    choice = input("\n请选择演示功能 (0-7): ").strip()
    
    # 根据选择执行对应功能
    if choice == "1":
        demo_login_and_fetch()
    elif choice == "2":
        demo_load_from_file()
    elif choice == "3":
        demo_filter_by_teacher()
    elif choice == "4":
        demo_filter_by_day()
    elif choice == "5":
        demo_statistics()
    elif choice == "6":
        demo_format_options()
    elif choice == "7":
        demo_multiple_terms()
    elif choice == "0":
        # 运行所有演示
        demo_login_and_fetch()
        print("\n")
        demo_load_from_file()
        print("\n")
        demo_filter_by_teacher()
        print("\n")
        demo_filter_by_day()
        print("\n")
        demo_statistics()
        print("\n")
        demo_format_options()
        print("\n")
        demo_multiple_terms()
    else:
        logger.warning("无效的选择！")
    
    logger.section("演示结束")


if __name__ == "__main__":
    main()