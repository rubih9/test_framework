class TestFrameworkError(Exception):
    """测试框架基础异常类"""
    pass

class ConfigError(TestFrameworkError):
    """配置相关错误"""
    pass

class TestCaseError(TestFrameworkError):
    """测试用例相关错误"""
    pass

class APIError(TestFrameworkError):
    """API请求相关错误"""
    def __init__(self, message: str, status_code: int = None, response: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class ValidationError(TestFrameworkError):
    """数据验证错误"""
    pass

class ReportError(TestFrameworkError):
    """报告生成相关错误"""
    pass

class EmailError(TestFrameworkError):
    """邮件发送相关错误"""
    pass 