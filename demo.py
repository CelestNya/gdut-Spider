from login import GDUTAuth
from schedule import ScheduleManager
from logger import logger


def login():
    """统一登录函数（带缓存）"""
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
        schedule_manager.save_schedule_to_file(schedule_data, year, season)
        logger.info(f"共 {len(schedule_data)} 门课程")
    else:
        logger.info(f"{year}年{season}课表未开放或无数据")


def demo_load_from_file():
    """演示从文件加载课表"""
    logger.section("演示2：从文件加载课表")

    schedule_manager = ScheduleManager(userid=USERNAME)
    year, season = 2025, "Autumn"
    schedule_data = schedule_manager.load_schedule_by_name(year, season)

    if schedule_data:
        logger.info(f"成功加载 {len(schedule_data)} 门课程")
    else:
        logger.info(f"未找到 {year}年{season} 课表文件")


def demo_multiple_terms():
    """演示获取多个学期的课表"""
    logger.section("演示3：获取多个学期的课表")

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


def main():
    """主函数"""
    logger.section("广工教务系统爬虫 - 功能演示")

    # 登录凭据
    global USERNAME, PASSWORD
    USERNAME = input("请输入学号: ")
    if not USERNAME:
        logger.failure("请输入学号！")
        return

    PASSWORD = input("请输入密码: ")
    if not PASSWORD:
        logger.failure("请输入密码！")
        return

    print("\n" + "=" * 60)
    print("功能演示菜单")
    print("=" * 60)
    print("1. 登录并获取课表")
    print("2. 从文件加载课表")
    print("3. 获取多个学期的课表")
    print("0. 运行所有演示")
    print("=" * 60)

    choice = input("\n请选择演示功能 (0-3): ").strip()

    demos = {
        "1": demo_login_and_fetch,
        "2": demo_load_from_file,
        "3": demo_multiple_terms,
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