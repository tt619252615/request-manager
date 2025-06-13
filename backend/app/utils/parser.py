"""
HTTP 请求解析器
用于解析 Fiddler Raw 格式和 cURL 命令
"""

import re
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs

from ..models.request import HttpMethodEnum


class ParsedRequest:
    """解析后的请求对象"""
    
    def __init__(
        self,
        method: HttpMethodEnum,
        url: str,
        headers: Dict[str, str],
        body: Optional[str] = None,
        params: Optional[Dict[str, str]] = None
    ):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body
        self.params = params or {}


class FiddlerParser:
    """Fiddler Raw 格式解析器"""
    
    @staticmethod
    def parse(raw_data: str) -> ParsedRequest:
        """
        解析 Fiddler Raw 格式的 HTTP 请求
        
        Args:
            raw_data: Fiddler 导出的原始数据
            
        Returns:
            ParsedRequest: 解析后的请求对象
            
        Raises:
            ValueError: 当数据格式无效时
        """
        lines = raw_data.strip().split('\n')
        
        if not lines:
            raise ValueError("请求数据为空")
            
        # 解析请求行 (第一行)
        request_line = lines[0].strip()
        method, url, params = FiddlerParser._parse_request_line(request_line)
        
        # 解析请求头和请求体
        headers, body = FiddlerParser._parse_headers_and_body(lines[1:])
        
        # 构建完整URL
        full_url = FiddlerParser._build_full_url(url, headers)
        
        return ParsedRequest(
            method=method,
            url=full_url,
            headers=headers,
            body=body,
            params=params
        )
    
    @staticmethod
    def _parse_request_line(request_line: str) -> Tuple[HttpMethodEnum, str, Dict[str, str]]:
        """解析请求行"""
        # 匹配: METHOD URL HTTP/VERSION
        match = re.match(r'^(\w+)\s+(.+?)\s+HTTP\/[\d.]+$', request_line)
        if not match:
            raise ValueError(f"无效的请求行格式: {request_line}")
            
        method_str = match.group(1).upper()
        full_url = match.group(2)
        
        # 验证HTTP方法
        try:
            method = HttpMethodEnum(method_str)
        except ValueError:
            raise ValueError(f"不支持的HTTP方法: {method_str}")
            
        # 分离URL和查询参数
        if '?' in full_url:
            base_url, query_string = full_url.split('?', 1)
            params = FiddlerParser._parse_query_params(query_string)
        else:
            base_url = full_url
            params = {}
            
        return method, base_url, params
    
    @staticmethod
    def _parse_query_params(query_string: str) -> Dict[str, str]:
        """解析查询参数"""
        params = {}
        if query_string:
            try:
                # 使用标准库解析查询参数
                parsed = parse_qs(query_string, keep_blank_values=True)
                # 转换为简单的键值对（取第一个值）
                params = {k: v[0] if v else '' for k, v in parsed.items()}
            except Exception:
                # 如果标准解析失败，手动解析
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key] = value
                    else:
                        params[param] = ''
        return params
    
    @staticmethod
    def _parse_headers_and_body(lines: list) -> Tuple[Dict[str, str], Optional[str]]:
        """解析请求头和请求体"""
        headers = {}
        body_start_index = -1
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 空行表示头部结束，后面是请求体
            if line == '':
                body_start_index = i + 1
                break
                
            # 解析请求头
            if ':' in line:
                key, value = line.split(':', 1)
                headers[key.strip()] = value.strip()
        
        # 解析请求体
        body = None
        if body_start_index > 0 and body_start_index < len(lines):
            body_lines = lines[body_start_index:]
            if body_lines:
                body = '\n'.join(body_lines).strip()
                
        return headers, body
    
    @staticmethod
    def _build_full_url(base_url: str, headers: Dict[str, str]) -> str:
        """构建完整URL"""
        if base_url.startswith('http'):
            return base_url
            
        # 从请求头中获取host
        host = headers.get('host') or headers.get('Host')
        if not host:
            raise ValueError("无法确定请求的主机地址")
            
        # 判断是否使用HTTPS
        is_https = (
            headers.get('origin', '').startswith('https://') or
            headers.get('referer', '').startswith('https://') or
            ':443' in base_url
        )
        
        scheme = 'https' if is_https else 'http'
        return f"{scheme}://{host}{base_url}"


class CurlParser:
    """cURL 命令解析器"""
    
    @staticmethod
    def parse(curl_command: str) -> ParsedRequest:
        """
        解析 cURL 命令
        
        Args:
            curl_command: cURL 命令字符串
            
        Returns:
            ParsedRequest: 解析后的请求对象
            
        Raises:
            ValueError: 当命令格式无效时
        """
        # 清理命令字符串
        lines = curl_command.strip().split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            if line.endswith('\\'):
                line = line[:-1].strip()
            clean_lines.append(line)
            
        command = ' '.join(clean_lines)
        
        # 解析URL
        url = CurlParser._extract_url(command)
        if not url:
            raise ValueError("无法从 cURL 命令中提取 URL")
            
        # 解析HTTP方法
        method = CurlParser._extract_method(command)
        
        # 解析请求头
        headers = CurlParser._extract_headers(command)
        
        # 解析请求体
        body = CurlParser._extract_body(command)
        
        # 解析查询参数
        params = CurlParser._extract_params(url)
        
        # 清理URL（移除查询参数）
        clean_url = url.split('?')[0] if '?' in url else url
        
        return ParsedRequest(
            method=method,
            url=clean_url,
            headers=headers,
            body=body,
            params=params
        )
    
    @staticmethod
    def _extract_url(command: str) -> Optional[str]:
        """提取URL"""
        # 匹配 curl 后面的URL
        patterns = [
            r"curl\s+['\"]([^'\"]+)['\"]",  # 带引号的URL
            r"curl\s+([^\s]+)",           # 不带引号的URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def _extract_method(command: str) -> HttpMethodEnum:
        """提取HTTP方法"""
        # 匹配 -X 或 --request 参数
        patterns = [
            r'(?:-X|--request)\s+([A-Z]+)',
            r'(?:-X|--request)\s+[\'"]([A-Z]+)[\'"]'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                try:
                    return HttpMethodEnum(match.group(1))
                except ValueError:
                    pass
        
        # 默认为GET方法
        return HttpMethodEnum.GET
    
    @staticmethod
    def _extract_headers(command: str) -> Dict[str, str]:
        """提取请求头"""
        headers = {}
        
        # 匹配 -H 或 --header 参数
        patterns = [
            r'(?:-H|--header)\s+[\'"]([^\'"]+)[\'"]',
            r'(?:-H|--header)\s+([^\s]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, command)
            for match in matches:
                if ':' in match:
                    key, value = match.split(':', 1)
                    headers[key.strip()] = value.strip()
        
        return headers
    
    @staticmethod
    def _extract_body(command: str) -> Optional[str]:
        """提取请求体"""
        # 匹配 -d 或 --data 参数
        patterns = [
            r'(?:-d|--data)\s+[\'"]([^\'"]*)[\'"]',
            r'(?:-d|--data)\s+([^\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                return match.group(1)
        return None
    
    @staticmethod
    def _extract_params(url: str) -> Dict[str, str]:
        """从URL中提取查询参数"""
        if '?' not in url:
            return {}
            
        try:
            parsed = urlparse(url)
            return dict(parse_qs(parsed.query, keep_blank_values=True))
        except Exception:
            return {}


def validate_parsed_request(parsed: ParsedRequest) -> Tuple[bool, list]:
    """
    验证解析结果
    
    Args:
        parsed: 解析后的请求对象
        
    Returns:
        Tuple[bool, list]: (是否有效, 错误列表)
    """
    errors = []
    
    if not parsed.method:
        errors.append("缺少 HTTP 方法")
        
    if not parsed.url:
        errors.append("缺少请求 URL")
    else:
        try:
            result = urlparse(parsed.url)
            if not result.scheme or not result.netloc:
                errors.append("URL 格式无效")
        except Exception:
            errors.append("URL 格式无效")
            
    return len(errors) == 0, errors 