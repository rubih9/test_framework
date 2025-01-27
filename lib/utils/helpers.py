from typing import Any, Dict, List
import json
from datetime import datetime
import re
from pathlib import Path

def deep_get(obj: Dict[str, Any], path: str, default: Any = None) -> Any:
    """从嵌套字典中获取值
    
    Args:
        obj: 字典对象
        path: 点分隔的路径 (例如: "data.user.id")
        default: 默认值
        
    Returns:
        找到的值或默认值
    """
    try:
        parts = path.split('.')
        for part in parts:
            if isinstance(obj, dict):
                obj = obj.get(part, default)
            elif isinstance(obj, list) and part.isdigit():
                obj = obj[int(part)]
            else:
                return default
        return obj
    except (KeyError, IndexError, TypeError):
        return default

def deep_compare(actual: Any, expected: Dict[str, Any]) -> bool:
    """深度比较实际值和预期值
    
    Args:
        actual: 实际值
        expected: 预期值
        
    Returns:
        是否匹配
    """
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False
        return all(
            key in actual and deep_compare(actual[key], value)
            for key, value in expected.items()
        )
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            return False
        return all(
            deep_compare(a, e) for a, e in zip(actual, expected)
        )
    else:
        return actual == expected

def format_json(obj: Any) -> str:
    """格式化JSON字符串
    
    Args:
        obj: 要格式化的对象
        
    Returns:
        格式化后的JSON字符串
    """
    return json.dumps(obj, ensure_ascii=False, indent=2)

def validate_variable_name(name: str) -> bool:
    """验证变量名是否合法
    
    Args:
        name: 变量名
        
    Returns:
        是否合法
    """
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, name))

def create_timestamp() -> str:
    """生成时间戳字符串
    
    Returns:
        时间戳字符串
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def ensure_directory(path: str) -> Path:
    """确保目录存在
    
    Args:
        path: 目录路径
        
    Returns:
        Path对象
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """递归合并两个字典
    
    Args:
        dict1: 第一个字典
        dict2: 第二个字典
        
    Returns:
        合并后的字典
    """
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result 