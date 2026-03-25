import logging
import sys
import os
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """炫彩日志格式化器"""
    
    COLORS = {
        'DEBUG': '\033[38;5;243m',
        'INFO': '\033[38;5;214m',
        'WARNING': '\033[38;5;226m',
        'ERROR': '\033[38;5;196m',
        'CRITICAL': '\033[38;5;201m',
        'RESET': '\033[0m',
        'GREEN': '\033[38;5;46m',
        'BLUE': '\033[38;5;33m',
        'CYAN': '\033[38;5;51m',
        'MAGENTA': '\033[38;5;213m',
        'YELLOW': '\033[38;5;226m',
        'ORANGE': '\033[38;5;208m',
    }
    
    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        timestamp = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
        gray = self.COLORS['DEBUG']
        colored_timestamp = f"{gray}[{timestamp}]{reset}"
        
        colored_levelname = f"{color}[{levelname}]{reset}"
        message = record.getMessage()
        
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
        
        if not self.logger.handlers:
            logs_dir = "logs"
            os.makedirs(logs_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_filename = os.path.join(logs_dir, f"{name}_{timestamp}.log")
            
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(ColoredFormatter())
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
        colored_message = self._colorize(f"【{title}】", cyan)
        self.logger.info(colored_message)
    
    def subsection(self, title: str):
        """小节标题（亮蓝色）"""
        blue = ColoredFormatter.COLORS['BLUE']
        colored_message = self._colorize(f"  {title}", blue)
        self.logger.info(colored_message)


logger = Logger("GDUTSpider")