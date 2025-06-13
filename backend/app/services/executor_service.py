"""
HTTP 请求执行服务
"""

import time
import json
import traceback
from typing import Dict, Optional, Any
import requests
from urllib.parse import urlencode

from ..models.request import HttpRequest
from ..schemas.request import RequestTestData, RequestTestResult
from ..config import settings


class ExecutorService:
    """HTTP请求执行服务"""
    
    def __init__(self):
        self.session = requests.Session()
        # 设置默认超时
        self.session.timeout = settings.default_timeout
        
    def test_request(
        self, 
        request: HttpRequest, 
        test_data: Optional[RequestTestData] = None
    ) -> RequestTestResult:
        """
        测试HTTP请求
        
        Args:
            request: HTTP请求对象
            test_data: 测试数据（可覆盖原始请求参数）
            
        Returns:
            RequestTestResult: 测试结果
        """
        start_time = time.time()
        
        try:
            # 准备请求参数
            url, headers, params, body, timeout = self._prepare_request_params(request, test_data)
            
            # 发送请求
            response = self._send_request(
                method=request.method.value,
                url=url,
                headers=headers,
                params=params,
                data=body,
                timeout=timeout
            )
            
            # 计算响应时间
            response_time = (time.time() - start_time) * 1000
            
            # 处理响应
            return RequestTestResult(
                success=True,
                status_code=response.status_code,
                response_body=response.text,
                response_headers=dict(response.headers),
                response_time=response_time
            )
            
        except requests.exceptions.Timeout:
            return RequestTestResult(
                success=False,
                error_message="请求超时"
            )
        except requests.exceptions.ConnectionError:
            return RequestTestResult(
                success=False,
                error_message="连接失败"
            )
        except Exception as e:
            return RequestTestResult(
                success=False,
                error_message=f"请求失败: {str(e)}"
            )
    
    def execute_request(
        self,
        request: HttpRequest,
        override_params: Optional[Dict[str, Any]] = None,
        proxy: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行HTTP请求（用于任务调度）
        
        Args:
            request: HTTP请求对象
            override_params: 覆盖参数
            proxy: 代理设置
            
        Returns:
            Dict: 执行结果
        """
        start_time = time.time()
        result = {
            "success": False,
            "status_code": None,
            "response_body": None,
            "response_headers": None,
            "response_time": None,
            "error_message": None,
            "proxy_used": proxy
        }
        
        try:
            # 确保request对象不为None
            if not request:
                result["error_message"] = "请求对象为空"
                return result
            
            # 准备请求参数
            url = request.url
            headers = dict(request.headers) if request.headers else {}
            params = dict(request.params) if request.params else {}
            body = request.body
            
            # 应用覆盖参数
            if override_params:
                if "headers" in override_params:
                    headers.update(override_params["headers"])
                if "params" in override_params:
                    params.update(override_params["params"])
                if "body" in override_params:
                    body = override_params["body"]
            
            # 设置代理
            proxies = None
            if proxy:
                # 确保代理格式正确
                if not proxy.startswith('http://') and not proxy.startswith('https://'):
                    proxy = f"http://{proxy}"
                proxies = {"http": proxy, "https": proxy}
            
            # 发送请求
            response = self._send_request(
                method=request.method.value,
                url=url,
                headers=headers,
                params=params,
                data=body,
                proxies=proxies,
                timeout=settings.default_timeout
            )
            
            # 计算响应时间
            response_time = (time.time() - start_time) * 1000
            
            result.update({
                "success": True,
                "status_code": response.status_code,
                "response_body": response.text,
                "response_headers": dict(response.headers),
                "response_time": response_time
            })
            
        except requests.exceptions.Timeout:
            result.update({
                "error_message": "请求超时",
                "response_time": (time.time() - start_time) * 1000
            })
        except requests.exceptions.ConnectionError as e:
            result.update({
                "error_message": f"连接失败: {str(e)}",
                "response_time": (time.time() - start_time) * 1000
            })
        except requests.exceptions.ProxyError as e:
            result.update({
                "error_message": f"代理错误: {str(e)}",
                "response_time": (time.time() - start_time) * 1000
            })
        except Exception as e:
            result.update({
                "error_message": f"请求失败: {str(e)}",
                "response_time": (time.time() - start_time) * 1000
            })
            # 记录详细的异常信息
            traceback.print_exc()
        
        return result
    
    def _prepare_request_params(
        self, 
        request: HttpRequest, 
        test_data: Optional[RequestTestData]
    ) -> tuple:
        """准备请求参数"""
        # 基础参数
        url = request.url
        headers = dict(request.headers)
        params = dict(request.params)
        body = request.body
        timeout = settings.default_timeout
        
        # 应用测试数据覆盖
        if test_data:
            if test_data.override_headers:
                headers.update(test_data.override_headers)
            if test_data.override_params:
                params.update(test_data.override_params)
            if test_data.override_body is not None:
                body = test_data.override_body
            if test_data.timeout:
                timeout = test_data.timeout
        
        return url, headers, params, body, timeout
    
    def _send_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        data: Optional[str] = None,
        proxies: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ) -> requests.Response:
        """发送HTTP请求"""
        
        # 构建完整URL
        if params:
            param_string = urlencode(params)
            if param_string:
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}{param_string}"
        
        # 处理请求体
        request_data = None
        json_data = None
        
        if data and method.upper() in ["POST", "PUT", "PATCH"]:
            content_type = headers.get("content-type", "") if headers else ""
            
            if "application/json" in content_type.lower():
                try:
                    json_data = json.loads(data)
                except json.JSONDecodeError:
                    request_data = data
            else:
                request_data = data
        
        # 发送请求
        response = self.session.request(
            method=method.upper(),
            url=url,
            headers=headers,
            data=request_data,
            json=json_data,
            proxies=proxies,
            timeout=timeout,
            allow_redirects=True
        )
        
        return response
    
    def validate_response(
        self, 
        response_body: str, 
        success_condition: Optional[str] = None,
        stop_condition: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        验证响应内容
        
        Args:
            response_body: 响应体
            success_condition: 成功条件表达式
            stop_condition: 停止条件表达式
            
        Returns:
            Dict: {"is_success": bool, "should_stop": bool}
        """
        result = {"is_success": False, "should_stop": False}
        
        try:
            # 简单的条件检查
            if success_condition:
                if self._evaluate_condition(response_body, success_condition):
                    result["is_success"] = True
            
            if stop_condition:
                if self._evaluate_condition(response_body, stop_condition):
                    result["should_stop"] = True
                    
        except Exception:
            pass  # 忽略条件检查错误
        
        return result
    
    def _evaluate_condition(self, response_body: str, condition: str) -> bool:
        """评估条件表达式"""
        try:
            # 简单的字符串包含检查
            if "contains" in condition:
                # 格式: response.text.contains('success')
                match = condition.split("contains")
                if len(match) == 2:
                    search_text = match[1].strip().strip("()\"'")
                    return search_text in response_body
            
            # 状态码检查
            if "status_code" in condition:
                # 这里需要在调用时传入状态码
                return True  # 暂时简化处理
                
            return False
        except Exception:
            return False 