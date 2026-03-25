import bs4
import requests
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
        logger.debug(f"开始加密密码，salt: {salt}")
        
        # 前缀处理："J69IVxcXqvqNhvk1"重复4次
        prefix = "J69IVxcXqvqNhvk1"
        input_data = prefix * 4 + password
        
        # 转换为ASCII字节数组
        input_bytes = input_data.encode('ascii')
        logger.debug(f"输入数据长度: {len(input_bytes)} bytes")
        
        # 手动填充（PKCS7）
        block_size = 16
        padding_length = block_size - (len(input_bytes) % block_size)
        padded_data = input_bytes + bytes([padding_length] * padding_length)
        logger.debug(f"填充后长度: {len(padded_data)} bytes, 填充长度: {padding_length}")
        
        # 初始化密钥和IV
        key_bytes = salt.encode('ascii')
        iv_bytes = "Jisniwqjwqjwqjww".encode('ascii')
        logger.debug(f"密钥长度: {len(key_bytes)} bytes, IV长度: {len(iv_bytes)} bytes")
        
        # AES-CBC加密
        from Crypto.Cipher import AES
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        encrypted_data = cipher.encrypt(padded_data)
        
        # 转换为Base64字符串
        import base64
        encrypted_str = base64.b64encode(encrypted_data).decode('utf-8')
        logger.debug(f"加密完成，结果长度: {len(encrypted_str)}")
        
        return encrypted_str


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
        logger.debug("GDUTAuth初始化完成")

    def uri_builder(self, path: str, query: str) -> str:
        """构建完整URL
        
        Args:
            path: URL路径
            query: 查询字符串
            
        Returns:
            str: 完整URL
        """
        url = f"{self.HOST}/{path.lstrip('/')}" if path else self.HOST
        return f"{url}?{query}" if query else url

    def login(self, userid: str, password: str) -> bool:
        """登录教务系统
        
        Args:
            userid: 学号
            password: 密码
            
        Returns:
            bool: 登录是否成功
        """
        logger.section("开始登录流程")
        logger.info(f"学号: {userid}")
        
        login_path = "authserver/login"
        encoded_login_service = requests.utils.quote(self.LOGIN_SERVICE_URL)
        full_login_uri = self.uri_builder(login_path, f"service={encoded_login_service}")
        logger.debug(f"登录URL: {full_login_uri}")
        
        try:
            # 1. 获取登录页面以提取隐藏参数
            logger.subsection("步骤1: 获取登录页面")
            response = self.session.get(self.LOGIN_SERVICE_URL)
            logger.debug(f"登录页面响应状态码: {response.status_code}")
            logger.debug(f"登录页面URL: {response.url}")
            response.raise_for_status()
            
            # 2. 解析页面中的隐藏参数
            logger.subsection("步骤2: 解析页面中的隐藏参数")
            soup = bs4.BeautifulSoup(response.text, "html.parser")
            password_form = soup.find(id="pwdFromId")
            if not password_form:
                logger.failure("未找到登录表单 'pwdFromId'")
                return False
            
            logger.debug("找到登录表单")
            hidden_inputs = password_form.select("input[type=hidden]")
            logger.debug(f"找到 {len(hidden_inputs)} 个隐藏输入字段")
            
            if not hidden_inputs:
                logger.failure("未找到隐藏输入字段")
                return False
            
            # 提取加密盐值
            salt = None
            logger.debug("开始提取加密盐值...")
            for i, input_elem in enumerate(hidden_inputs, 1):
                name = input_elem.get("name")
                value = input_elem.get("value")
                elem_id = input_elem.get("id")
                logger.debug(f"隐藏字段 {i}: name={name}, id={elem_id}, value={value[:50] if value else None}")
                
                if elem_id == "pwdEncryptSalt" and value:
                    salt = value
                    logger.debug(f"找到加密盐值: {salt}")
                    break
            
            if not salt:
                logger.failure("未找到加密盐值 'pwdEncryptSalt'")
                return False
            
            # 3. 构建登录参数
            logger.subsection("步骤3: 构建登录参数")
            form_data = {}
            for input_elem in hidden_inputs:
                if input_elem.get("name") and input_elem.get("value"):
                    name = input_elem.get("name")
                    value = input_elem.get("value")
                    form_data[name] = value
                    logger.debug(f"添加表单字段: {name} = {value[:50] if len(str(value)) > 50 else value}")
            
            # 加密密码
            logger.debug("开始加密密码...")
            encrypted_password = GDUTCrypto.encrypt(password, salt)
            form_data["username"] = userid
            form_data["password"] = encrypted_password
            form_data["captcha"] = ""
            form_data["rememberMe"] = "true"
            
            logger.debug("最终表单数据:")
            for key, value in form_data.items():
                if key == "password":
                    logger.debug(f"  {key} = {value[:50]}... (加密后的密码)")
                else:
                    logger.debug(f"  {key} = {value}")
            
            # 4. 发送登录请求
            logger.subsection("步骤4: 发送登录请求")
            login_response = self.session.post(full_login_uri, data=form_data)
            logger.debug(f"登录响应状态码: {login_response.status_code}")
            logger.debug(f"登录响应URL: {login_response.url}")
            
            # 5. 检查登录是否成功（通过检查两个JSESSIONID）
            return self.check_login_success()
                
        except requests.RequestException as e:
            logger.failure(f"登录请求失败: {e}")
            return False

    def check_login_success(self) -> bool:
        """通过检查两个JSESSIONID来验证登录是否成功
        
        Returns:
            bool: 登录是否成功
        """
        logger.subsection("步骤5: 检查登录状态")
        
        # 获取所有cookies
        cookies = self.session.cookies
        
        # 查找包含JSESSIONID的cookie
        jsession_ids = []
        for cookie in cookies:
            if 'JSESSIONID' in cookie.name:
                jsession_ids.append((cookie.name, cookie.value))
        
        # 检查是否找到两个JSESSIONID
        if len(jsession_ids) >= 2:
            logger.success("登录成功！")
            logger.info(f"找到 {len(jsession_ids)} 个JSESSIONID:")
            for i, (name, value) in enumerate(jsession_ids, 1):
                logger.info(f"  JSESSIONID {i}: {name} = {value}")
            return True
        else:
            logger.failure(f"登录失败，只找到 {len(jsession_ids)} 个JSESSIONID")
            if jsession_ids:
                logger.info("找到的JSESSIONID:")
                for i, (name, value) in enumerate(jsession_ids, 1):
                    logger.info(f"  JSESSIONID {i}: {name} = {value}")
            return False
    
    def get_session(self) -> requests.Session:
        """获取当前会话对象
        
        Returns:
            requests.Session: 当前会话对象
        """
        return self.session