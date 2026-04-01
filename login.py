import bs4
import requests
import os
import pickle
from datetime import datetime, timedelta
from logger import logger


class GDUTCrypto:
    """密码加密工具类"""
    
    @staticmethod
    def encrypt(password: str, salt: str) -> str:
        """AES-CBC加密
        
        Args:
            password: 原始密码
            salt: 加密密钥
            
        Returns:
            str: 加密后的Base64字符串
        """
        prefix = "J69IVxcXqvqNhvk1" * 4 + password
        input_bytes = prefix.encode('ascii')
        
        block_size = 16
        padding_length = block_size - (len(input_bytes) % block_size)
        padded_data = input_bytes + bytes([padding_length] * padding_length)
        
        key_bytes = salt.encode('ascii')
        iv_bytes = "Jisniwqjwqjwqjww".encode('ascii')
        
        from Crypto.Cipher import AES
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        encrypted_data = cipher.encrypt(padded_data)
        
        import base64
        return base64.b64encode(encrypted_data).decode('utf-8')


class GDUTAuth:
    """广工教务系统认证类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.HOST = "https://authserver.gdut.edu.cn"
        self.JXFW_HOST = "jxfw.gdut.edu.cn"
        self.LOGIN_SERVICE_URL = "https://jxfw.gdut.edu.cn/new/ssoLogin"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        self.session.headers.update(self.headers)

    def _build_url(self, path: str, query: str = None) -> str:
        """构建完整URL
        
        Args:
            path: URL路径
            query: 查询字符串
            
        Returns:
            str: 完整URL
        """
        url = f"{self.HOST}/{path.lstrip('/')}" if path else self.HOST
        return f"{url}?{query}" if query else url

    def _extract_salt(self, soup: bs4.BeautifulSoup) -> str:
        """从登录页面提取加密盐值
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            str: 加密盐值，如果未找到返回None
        """
        password_form = soup.find(id="pwdFromId")
        if not password_form:
            return None
        
        for input_elem in password_form.select("input[type=hidden]"):
            if input_elem.get("id") == "pwdEncryptSalt" and input_elem.get("value"):
                return input_elem.get("value")
        
        return None

    def _build_login_data(self, soup: bs4.BeautifulSoup, userid: str, password: str, salt: str) -> dict:
        """构建登录表单数据
        
        Args:
            soup: BeautifulSoup对象
            userid: 学号
            password: 密码
            salt: 加密盐值
            
        Returns:
            dict: 登录表单数据
        """
        password_form = soup.find(id="pwdFromId")
        form_data = {}
        
        for input_elem in password_form.select("input[type=hidden]"):
            name = input_elem.get("name")
            value = input_elem.get("value")
            if name and value:
                form_data[name] = value
        
        form_data["username"] = userid
        form_data["password"] = GDUTCrypto.encrypt(password, salt)
        form_data["captcha"] = ""
        form_data["rememberMe"] = "true"
        
        return form_data

    def _check_jsessionid_count(self) -> bool:
        """检查JSESSIONID数量是否足够
        
        Returns:
            bool: 是否找到至少2个JSESSIONID
        """
        jsession_ids = [(cookie.name, cookie.value) 
                       for cookie in self.session.cookies 
                       if 'JSESSIONID' in cookie.name]
        
        if len(jsession_ids) >= 2:
            logger.info(f"找到 {len(jsession_ids)} 个JSESSIONID:")
            for i, (name, value) in enumerate(jsession_ids, 1):
                logger.info(f"  JSESSIONID {i}: {name} = {value}")
            return True
        
        logger.failure(f"登录失败，只找到 {len(jsession_ids)} 个JSESSIONID")
        return False

    def login(self, userid: str, password: str, max_age_hours: int = 24) -> bool:
        """登录教务系统（自动尝试使用缓存的Cookie）

        Args:
            userid: 学号
            password: 密码
            max_age_hours: Cookie 最大有效期（小时）

        Returns:
            bool: 登录是否成功
        """
        logger.section("开始登录流程")
        logger.info(f"学号: {userid}")

        cookie_file = self._get_cookie_file(userid)

        if os.path.exists(cookie_file):
            logger.info("发现已保存的 Cookie")

            try:
                with open(cookie_file, 'rb') as f:
                    cookie_data = pickle.load(f)

                timestamp = datetime.fromisoformat(cookie_data['timestamp'])
                age = datetime.now() - timestamp

                if age > timedelta(hours=max_age_hours):
                    logger.warning(f"Cookie 已过期（超过 {max_age_hours} 小时）")
                elif self._load_cookies(userid) and self._verify_cookies():
                    logger.success("使用缓存的 Cookie 登录成功")
                    return True
                else:
                    logger.warning("Cookie 验证失败，将重新登录")
                    self.session.cookies.clear()

            except Exception as e:
                logger.warning(f"加载 Cookie 失败: {e}")
                self.session.cookies.clear()

        logger.info("开始从头登录")

        try:
            logger.subsection("步骤1: 获取登录页面")
            response = self.session.get(self.LOGIN_SERVICE_URL)
            response.raise_for_status()

            logger.subsection("步骤2: 解析页面中的隐藏参数")
            soup = bs4.BeautifulSoup(response.text, "html.parser")

            salt = self._extract_salt(soup)
            if not salt:
                logger.failure("未找到加密盐值 'pwdEncryptSalt'")
                return False

            logger.subsection("步骤3: 构建登录参数")
            form_data = self._build_login_data(soup, userid, password, salt)

            logger.subsection("步骤4: 发送登录请求")
            login_path = "authserver/login"
            encoded_login_service = requests.utils.quote(self.LOGIN_SERVICE_URL)
            full_login_uri = self._build_url(login_path, f"service={encoded_login_service}")

            login_response = self.session.post(full_login_uri, data=form_data)

            if self._check_jsessionid_count():
                self._save_cookies(userid)
                return True

            return False

        except requests.RequestException as e:
            logger.failure(f"登录请求失败: {e}")
            return False

    def get_session(self) -> requests.Session:
        """获取当前会话对象
        
        Returns:
            requests.Session: 当前会话对象
        """
        return self.session
    
    def _get_cookie_file(self, userid: str) -> str:
        """获取 Cookie 文件路径

        Args:
            userid: 学号

        Returns:
            str: Cookie 文件路径
        """
        user_dir = os.path.join("cookies", userid)
        return os.path.join(user_dir, "session.pkl")
    
    def _save_cookies(self, userid: str):
        """保存 Cookie 到文件

        Args:
            userid: 学号
        """
        try:
            cookie_file = self._get_cookie_file(userid)
            user_dir = os.path.dirname(cookie_file)
            os.makedirs(user_dir, exist_ok=True)

            cookie_data = {
                "cookies": self.session.cookies,
                "headers": dict(self.session.headers),
                "timestamp": datetime.now().isoformat(),
                "userid": userid
            }

            with open(cookie_file, 'wb') as f:
                pickle.dump(cookie_data, f)

            logger.success(f"Cookie 已保存到: {cookie_file}")

        except Exception as e:
            logger.warning(f"保存 Cookie 失败: {e}")
    
    def _load_cookies(self, userid: str) -> bool:
        """从文件加载 Cookie
        
        Args:
            userid: 学号
            
        Returns:
            bool: 是否成功加载
        """
        cookie_file = self._get_cookie_file(userid)
        
        if not os.path.exists(cookie_file):
            return False
        
        try:
            with open(cookie_file, 'rb') as f:
                cookie_data = pickle.load(f)
            
            self.session.cookies = cookie_data['cookies']
            self.session.headers.update(cookie_data['headers'])
            
            logger.success(f"Cookie 已从文件加载: {cookie_file}")
            logger.info(f"Cookie 创建时间: {cookie_data['timestamp']}")
            return True
            
        except Exception as e:
            logger.warning(f"加载 Cookie 失败: {e}")
            return False
    
    def _verify_cookies(self) -> bool:
        """验证 Cookie 是否有效
        
        Returns:
            bool: Cookie 是否有效
        """
        try:
            jsession_ids = [(cookie.name, cookie.value) 
                           for cookie in self.session.cookies 
                           if 'JSESSIONID' in cookie.name]
            
            if len(jsession_ids) < 2:
                logger.info(f"Cookie 数量不足，只有 {len(jsession_ids)} 个 JSESSIONID")
                return False
            
            logger.info(f"共有 {len(self.session.cookies)} 个 cookies")
            for name, value in jsession_ids:
                logger.info(f"找到 JSESSIONID: {name} = {value}")
            
            test_url = f"https://{self.JXFW_HOST}/new/ssoLogin"
            response = self.session.get(test_url, timeout=5, allow_redirects=True)
            
            if "login" in response.url and "welcome" not in response.url:
                logger.info("Cookie 已失效，被重定向到登录页")
                return False
            
            if "welcome" in response.url or "欢迎" in response.text or "同学" in response.text:
                logger.success("Cookie 验证成功")
                return True
            
            logger.info("Cookie 响应内容异常")
            return False
            
        except Exception as e:
            logger.warning(f"验证 Cookie 失败: {e}")
            return False