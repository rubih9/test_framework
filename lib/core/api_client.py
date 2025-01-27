import aiohttp
import asyncio
from typing import Dict, Any, Optional, Union
from loguru import logger
from ..utils.exceptions import APIError
from ..utils.helpers import format_json

class APIClient:
    def __init__(self, base_urls: Dict[str, str], timeout: int = 30, retry_count: int = 3, retry_delay: float = 1.0):
        """初始化API客户端
        
        Args:
            base_urls: 平台对应的基础URL字典
            timeout: 请求超时时间（秒）
            retry_count: 重试次数
            retry_delay: 重试延迟（秒）
        """
        self.base_urls = {k: v.rstrip('/') for k, v in base_urls.items()}
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.session = None
        self._setup_session_headers()
        
    def _setup_session_headers(self):
        """设置会话默认请求头"""
        self.default_headers = {
            'User-Agent': 'TestFramework/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self.default_headers
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
            
    async def request(
        self,
        method: str,
        endpoint: str,
        platform: str = "default",
        headers: Optional[Dict[str, str]] = None,
        data: Any = None,
        params: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
        verify_ssl: bool = True
    ) -> Dict[str, Any]:
        """发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            platform: 平台标识符
            headers: 请求头
            data: 请求数据
            params: URL参数
            files: 上传文件
            verify_ssl: 是否验证SSL证书
            
        Returns:
            响应数据
            
        Raises:
            APIError: API请求错误
        """
        if platform not in self.base_urls:
            raise APIError(f"未知的平台: {platform}")
            
        url = f"{self.base_urls[platform]}/{endpoint.lstrip('/')}"
        method = method.upper()
        
        # 合并请求头
        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)
            
        # 准备请求参数
        request_kwargs = {
            'headers': request_headers,
            'params': params,
            'ssl': verify_ssl
        }
        
        # 根据请求方法处理数据
        if method in ['POST', 'PUT', 'PATCH']:
            if files:
                # 处理文件上传
                form_data = aiohttp.FormData()
                for key, file_info in files.items():
                    form_data.add_field(key, **file_info)
                if data:
                    for key, value in data.items():
                        form_data.add_field(key, str(value))
                request_kwargs['data'] = form_data
            else:
                request_kwargs['json'] = data
        elif data:
            request_kwargs['data'] = data
            
        for attempt in range(self.retry_count):
            try:
                logger.info(f"发送请求: {method} {url}")
                logger.debug(f"请求头: {request_headers}")
                logger.debug(f"请求参数: {params}")
                logger.debug(f"请求数据: {data}")
                
                async with self.session.request(method, url, **request_kwargs) as response:
                    status_code = response.status
                    
                    try:
                        response_data = await response.json()
                    except:
                        response_data = await response.text()
                        
                    logger.info(f"响应状态码: {status_code}")
                    logger.debug(f"响应数据: {format_json(response_data)}")
                    
                    if 200 <= status_code < 300:
                        return {
                            'status_code': status_code,
                            'data': response_data
                        }
                    else:
                        error_msg = f"API请求失败: {status_code} - {response_data}"
                        if attempt < self.retry_count - 1:
                            logger.warning(f"{error_msg}, 将在 {self.retry_delay} 秒后重试")
                            await asyncio.sleep(self.retry_delay)
                            continue
                        raise APIError(error_msg, status_code, response_data)
                        
            except aiohttp.ClientError as e:
                error_msg = f"请求异常: {str(e)}"
                if attempt < self.retry_count - 1:
                    logger.warning(f"{error_msg}, 将在 {self.retry_delay} 秒后重试")
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise APIError(error_msg)
                
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送GET请求"""
        return await self.request('GET', endpoint, **kwargs)
        
    async def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送POST请求"""
        return await self.request('POST', endpoint, **kwargs)
        
    async def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送PUT请求"""
        return await self.request('PUT', endpoint, **kwargs)
        
    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送DELETE请求"""
        return await self.request('DELETE', endpoint, **kwargs)
        
    async def patch(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送PATCH请求"""
        return await self.request('PATCH', endpoint, **kwargs) 