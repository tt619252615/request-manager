"""
网络时间服务
基于 demo.py 的 get_network_time 方法实现
"""

import requests
from datetime import datetime, timedelta
from typing import Optional
from loguru import logger


class NetworkTimeService:
    """网络时间服务类"""
    
    def __init__(self):
        # 美团时间API - 参考demo.py
        self.time_apis = [
            "https://cube.meituan.com/ipromotion/cube/toc/component/base/getServerCurrentTime",
            "http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp"  # 备用API
        ]
        self._cached_time_diff = None  # 缓存的时间差（网络时间 - 本地时间）
        self._last_sync_time = None    # 上次同步时间
        self._sync_interval = 300      # 同步间隔（秒）
    
    def get_network_time(self) -> datetime:
        """
        获取网络时间 - 基于demo.py的get_network_time方法
        返回包含毫秒的精确时间
        """
        for api_url in self.time_apis:
            try:
                logger.debug(f"正在获取网络时间: {api_url}")
                
                response = requests.get(
                    api_url,
                    timeout=5,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 美团API格式: {"data":1749736490539,"message":"成功","status":0}
                    if "data" in data and data.get("status") == 0:
                        timestamp_ms = int(data["data"])
                        network_time = datetime.fromtimestamp(timestamp_ms / 1000.0)
                        logger.info(f"网络时间获取成功: {network_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                        return network_time
                    
                    # 淘宝API格式（如果需要的话）
                    elif "data" in data and "t" in data["data"]:
                        timestamp_ms = int(data["data"]["t"])
                        network_time = datetime.fromtimestamp(timestamp_ms / 1000.0)
                        logger.info(f"网络时间获取成功: {network_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                        return network_time
                        
                logger.warning(f"网络时间API返回格式不符合预期: {data}")
                        
            except requests.exceptions.RequestException as e:
                logger.warning(f"网络时间API请求失败 {api_url}: {e}")
            except Exception as e:
                logger.warning(f"解析网络时间失败 {api_url}: {e}")
        
        # 所有API都失败，使用本地时间
        logger.error("所有网络时间API都失败，使用本地时间")
        return datetime.now()
    
    def sync_time_diff(self) -> Optional[float]:
        """
        同步时间差（网络时间 - 本地时间）
        返回时间差（秒，包含毫秒精度）
        """
        try:
            local_time_before = datetime.now()
            network_time = self.get_network_time()
            local_time_after = datetime.now()
            
            # 使用请求前后的平均本地时间来减少网络延迟影响
            avg_local_time = local_time_before + (local_time_after - local_time_before) / 2
            
            # 计算时间差（秒）
            time_diff = (network_time - avg_local_time).total_seconds()
            
            self._cached_time_diff = time_diff
            self._last_sync_time = datetime.now()
            
            logger.info(f"时间同步完成: 网络时间差为 {time_diff:.3f} 秒")
            return time_diff
            
        except Exception as e:
            logger.error(f"时间同步失败: {e}")
            return None
    
    def get_current_network_time(self) -> datetime:
        """
        获取当前网络时间（使用缓存的时间差进行计算）
        这比每次都请求API更高效
        """
        # 检查是否需要重新同步
        now = datetime.now()
        if (self._cached_time_diff is None or 
            self._last_sync_time is None or 
            (now - self._last_sync_time).total_seconds() > self._sync_interval):
            
            logger.debug("时间差缓存过期，重新同步...")
            self.sync_time_diff()
        
        # 使用缓存的时间差计算网络时间
        if self._cached_time_diff is not None:
            network_time = now + timedelta(seconds=self._cached_time_diff)
            return network_time
        else:
            # 同步失败，直接请求网络时间
            return self.get_network_time()
    
    def format_time_with_ms(self, dt: datetime) -> str:
        """格式化时间，包含毫秒"""
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    def parse_time_with_ms(self, time_str: str) -> datetime:
        """解析包含毫秒的时间字符串"""
        try:
            # 支持多种格式
            formats = [
                '%Y-%m-%d %H:%M:%S.%f',  # 完整格式
                '%Y-%m-%d %H:%M:%S',     # 不含毫秒
                '%H:%M:%S.%f',           # 只有时间含毫秒
                '%H:%M:%S',              # 只有时间不含毫秒
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(time_str, fmt)
                except ValueError:
                    continue
            
            raise ValueError(f"无法解析时间格式: {time_str}")
            
        except Exception as e:
            logger.error(f"时间解析失败: {e}")
            raise
    
    def get_time_diff(self) -> float:
        """获取当前的时间差"""
        if self._cached_time_diff is None:
            self.sync_time_diff()
        return self._cached_time_diff or 0.0


# 全局网络时间服务实例
network_time_service = NetworkTimeService() 