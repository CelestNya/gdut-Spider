import logging
import sys
import os
from datetime import datetime


class ColorFormatter(logging.Formatter):
    """彩色日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[37m',       # 白色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m',       # 重置
        'GREEN': '\033[32m',      # 绿色
        'BLUE': '\033[34m',       # 蓝色
        'BOLD': '\033[1m',       # 粗体
    }
    
    def format(self, record):
        # 获取日志级别对应的颜色
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # 格式化时间戳
        timestamp = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
        
        # 格式化消息
        message = record.getMessage()
        
        # 应用颜色
        colored_levelname = f"{color}{levelname}{reset}"
        colored_message = f"{color}{message}{reset}"
        
        # 返回格式化后的日志
        return f"[{timestamp}] [{colored_levelname}] {colored_message}"


class ColoredFormatter(logging.Formatter):
    """炫彩日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[38;5;243m',      # 暗灰色
        'INFO': '\033[38;5;214m',       # 橙色
        'WARNING': '\033[38;5;226m',     # 亮黄色
        'ERROR': '\033[38;5;196m',      # 亮红色
        'CRITICAL': '\033[38;5;201m',   # 亮紫色
        'RESET': '\033[0m',             # 重置
        'GREEN': '\033[38;5;46m',       # 亮绿色
        'BLUE': '\033[38;5;33m',        # 亮蓝色
        'CYAN': '\033[38;5;51m',        # 亮青色
        'MAGENTA': '\033[38;5;213m',    # 亮紫色
        'YELLOW': '\033[38;5;226m',     # 亮黄色
        'ORANGE': '\033[38;5;208m',     # 橙色
        'PINK': '\033[38;5;219m',       # 粉色
        'LIME': '\033[38;5;154m',       # 青柠色
        'TEAL': '\033[38;5;80m',        # 蓝绿色
        'BOLD': '\033[1m',              # 粗体
        'DIM': '\033[2m',               # 暗淡
    }
    
    def format(self, record):
        # 获取日志级别对应的颜色
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # 格式化时间戳（使用暗灰色）
        timestamp = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
        gray = self.COLORS['DEBUG']
        colored_timestamp = f"{gray}[{timestamp}]{reset}"
        
        # 格式化级别名（使用对应颜色）
        colored_levelname = f"{color}[{levelname}]{reset}"
        
        # 格式化消息
        message = record.getMessage()
        
        # 返回格式化后的日志
        return f"{colored_timestamp} {colored_levelname} {message}"


class Logger:
    """统一日志管理类"""
    
    def __init__(self, name: str = "GDUTSpider", level: int = logging.INFO):
        """初始化日志器
        
        Args:
            name: 日志器名称
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 创建logs文件夹
            logs_dir = "logs"
            os.makedirs(logs_dir, exist_ok=True)
            
            # 生成带时间戳的日志文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_filename = os.path.join(logs_dir, f"{name}_{timestamp}.log")
            
            # 创建文件handler（使用普通格式化器）
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            # 创建控制台handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            
            # 创建炫彩格式化器
            formatter = ColoredFormatter()
            console_handler.setFormatter(formatter)
            
            # 添加handler
            self.logger.addHandler(console_handler)
    
    def _colorize(self, message: str, color_code: str) -> str:
        """给消息添加颜色
        
        Args:
            message: 消息内容
            color_code: 颜色代码
            
        Returns:
            str: 带颜色的消息
        """
        return f"{color_code}{message}{ColoredFormatter.COLORS['RESET']}"
    
    def debug(self, message: str):
        """调试日志（灰色）"""
        gray = ColoredFormatter.COLORS['DEBUG']
        colored_message = self._colorize(message, gray)
        self.logger.debug(colored_message)
    
    def info(self, message: str):
        """信息日志（橙色）"""
        orange = ColoredFormatter.COLORS['ORANGE']
        colored_message = self._colorize(message, orange)
        self.logger.info(colored_message)
    
    def warning(self, message: str):
        """警告日志（亮黄色）"""
        yellow = ColoredFormatter.COLORS['YELLOW']
        colored_message = self._colorize(message, yellow)
        self.logger.warning(colored_message)
    
    def error(self, message: str):
        """错误日志（亮红色）"""
        red = ColoredFormatter.COLORS['ERROR']
        colored_message = self._colorize(message, red)
        self.logger.error(colored_message)
    
    def success(self, message: str):
        """成功日志（亮绿色）"""
        green = ColoredFormatter.COLORS['GREEN']
        colored_message = self._colorize(f"✅ {message}", green)
        self.logger.info(colored_message)
    
    def failure(self, message: str):
        """失败日志（亮红色）"""
        red = ColoredFormatter.COLORS['ERROR']
        colored_message = self._colorize(f"❌ {message}", red)
        self.logger.error(colored_message)
    
    def section(self, title: str):
        """分节标题（亮青色）"""
        cyan = ColoredFormatter.COLORS['CYAN']
        bold = ColoredFormatter.COLORS.get('BOLD', '')
        colored_message = self._colorize(f"【{title}】", cyan)
        self.logger.info(colored_message)
    
    def subsection(self, title: str):
        """小节标题（亮蓝色）"""
        blue = ColoredFormatter.COLORS['BLUE']
        colored_message = self._colorize(f"  {title}", blue)
        self.logger.info(colored_message)
    
    def highlight(self, message: str):
        """高亮消息（亮黄色）"""
        yellow = ColoredFormatter.COLORS['YELLOW']
        colored_message = self._colorize(message, yellow)
        self.logger.info(colored_message)
    
    def important(self, message: str):
        """重要消息（亮紫色）"""
        magenta = ColoredFormatter.COLORS['MAGENTA']
        colored_message = self._colorize(message, magenta)
        self.logger.info(colored_message)
    
    def pink(self, message: str):
        """粉色消息"""
        pink = ColoredFormatter.COLORS['PINK']
        colored_message = self._colorize(message, pink)
        self.logger.info(colored_message)
    
    def lime(self, message: str):
        """青柠色消息"""
        lime = ColoredFormatter.COLORS['LIME']
        colored_message = self._colorize(message, lime)
        self.logger.info(colored_message)
    
    def teal(self, message: str):
        """蓝绿色消息"""
        teal = ColoredFormatter.COLORS['TEAL']
        colored_message = self._colorize(message, teal)
        self.logger.info(colored_message)


# 创建全局日志实例
logger = Logger("GDUTSpider")