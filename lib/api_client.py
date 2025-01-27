import aiohttp
import asyncio
from typing import Dict, Any, Optional
from loguru import logger
import json

class APIClient:
    def __init__(self, base_urls: Dict[str, str], timeout: int = 30):
        """初始化API客户端
        
        Args:
            base_urls: 平台对应的基础URL字典
            timeout: 请求超时时间（秒）
        """
        self.base_urls = {k: v.rstrip('/') for k, v in base_urls.items()}
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session = None
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
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
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            platform: 平台标识符
            headers: 请求头
            data: 请求数据
            params: URL参数
            
        Returns:
            响应数据
        """
        if platform not in self.base_urls:
            raise ValueError(f"Unknown platform: {platform}")
            
        url = f"{self.base_urls[platform]}/{endpoint.lstrip('/')}"
        method = method.upper()
        
        try:
            logger.info(f"发送请求: {method} {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"请求数据: {data}")
            logger.debug(f"URL参数: {params}")
            
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if method in ['POST', 'PUT', 'PATCH'] else None,
                data=data if method not in ['POST', 'PUT', 'PATCH'] else None,
                params=params
            ) as response:
                status_code = response.status
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.text()
                    
                logger.info(f"响应状态码: {status_code}")
                logger.debug(f"响应数据: {response_data}")
                
                return {
                    'status_code': status_code,
                    'data': response_data
                }
                
        except aiohttp.ClientError as e:
            logger.error(f"请求失败: {str(e)}")
            raise
            
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