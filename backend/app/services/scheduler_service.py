"""
任务调度引擎
基于 demo.py 的核心逻辑实现
"""

import threading
import time
import random
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, Future
from sqlalchemy.orm import Session

from ..models.task import Task, TaskStatusEnum, TaskTypeEnum
from ..models.request import HttpRequest
from ..models.execution import ExecutionRecord, ExecutionStatusEnum
from ..services.task_service import TaskService
from ..services.executor_service import ExecutorService
from ..services.network_time_service import network_time_service
from ..database import get_db_context
from ..config import settings
from loguru import logger


class ProxyManager:
    """代理管理器 - 基于demo.py的代理管理逻辑"""
    
    def __init__(self):
        self.proxy_list: List[str] = []
        self.last_fetch_time = 0
        self.fetch_interval = 30  # 30秒获取一次代理
        self.fetch_failed = False  # 标记代理获取是否失败
    
    def get_proxy_list(self, proxy_url: str) -> List[str]:
        """从代理API获取代理列表 - 参考demo.py的get_proxy_ips逻辑"""
        try:
            logger.debug(f"正在从 {proxy_url} 获取代理列表...")
            response = requests.get(proxy_url, timeout=10)
            data = response.json()
            
            if data.get("success") and data.get("code") == 0:
                proxies = []
                # 参考demo.py的extract_ip_port方法
                for item in data.get("data", []):
                    ip = item.get("ip")
                    port = item.get("port")
                    if ip and port:
                        proxies.append(f"http://{ip}:{port}")
                
                logger.info(f"成功获取 {len(proxies)} 个代理")
                self.fetch_failed = False
                return proxies
            else:
                logger.error(f"代理API返回错误: {data.get('msg', '未知错误')}")
                self.fetch_failed = True
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"获取代理失败，网络错误: {e}")
            self.fetch_failed = True
        except Exception as e:
            logger.error(f"获取代理失败: {e}")
            self.fetch_failed = True
        
        return []
    
    def get_random_proxy(self, proxy_config: Dict[str, Any]) -> Optional[str]:
        """获取随机代理 - 基于demo.py的代理选择逻辑"""
        if not proxy_config.get("enabled"):
            logger.debug("代理未启用，使用本地IP")
            return None
        
        current_time = time.time()
        proxy_url = proxy_config.get("proxy_url")
        
        # 参考demo.py的代理刷新逻辑
        if (not self.proxy_list or 
            current_time - self.last_fetch_time > self.fetch_interval) and proxy_url and not self.fetch_failed:
            
            logger.debug("代理列表为空或需要刷新，尝试获取新的代理列表...")
            new_proxies = self.get_proxy_list(proxy_url)
            
            if new_proxies:
                self.proxy_list = new_proxies
                self.last_fetch_time = current_time
                logger.info(f"代理列表已更新，共 {len(self.proxy_list)} 个代理")
            else:
                logger.warning("获取代理列表失败，将使用本地IP")
                if not self.proxy_list:  # 如果之前没有代理，标记为失败
                    self.fetch_failed = True
        
        # 返回随机代理（如果启用了轮换）
        if self.proxy_list and proxy_config.get("rotation", True):
            selected_proxy = random.choice(self.proxy_list)
            logger.debug(f"选择代理: {selected_proxy}")
            return selected_proxy
        elif self.proxy_list and not proxy_config.get("rotation", True):
            # 如果不轮换，使用第一个代理
            return self.proxy_list[0]
        else:
            if self.fetch_failed:
                logger.debug("代理获取失败，使用本地IP")
            else:
                logger.debug("没有可用代理，使用本地IP")
        return None
    
    def reset_proxy_status(self) -> None:
        """重置代理状态，用于手动刷新"""
        self.fetch_failed = False
        self.last_fetch_time = 0
        logger.info("代理状态已重置")


class TaskRunner:
    """任务执行器"""
    
    def __init__(self, task_id: int, request_id: int):
        self.task_id = task_id
        self.request_id = request_id
        self.executor = ExecutorService()
        self.proxy_manager = ProxyManager()
        self.stop_flag = threading.Event()
        
    def run(self) -> None:
        """运行任务"""
        # 在执行线程中重新获取任务和请求对象，避免跨线程会话问题
        try:
            with get_db_context() as db:
                task = db.query(Task).filter(Task.id == self.task_id).first()
                request = db.query(HttpRequest).filter(HttpRequest.id == self.request_id).first()
                
                if not task or not request:
                    logger.error(f"任务 {self.task_id} 或请求 {self.request_id} 不存在")
                    return
                
                logger.info(f"[{task.name}] 任务开始执行")
                
                # 根据任务类型执行
                if task.task_type == TaskTypeEnum.SINGLE:
                    self._run_single(task, request)
                elif task.task_type == TaskTypeEnum.RETRY:
                    self._run_retry(task, request)
                else:
                    # 其他类型暂时按单次执行处理
                    self._run_single(task, request)
                    
        except Exception as e:
            logger.error(f"任务 {self.task_id} 执行异常: {e}")
            import traceback
            traceback.print_exc()
    
    def _run_single(self, task: Task, request: HttpRequest) -> None:
        """执行单次任务"""
        self._execute_request(task, request)
    
    def _run_retry(self, task: Task, request: HttpRequest) -> None:
        """执行重试任务 - 基于demo.py的智能重试逻辑"""
        
        retry_config = task.retry_config or {}
        schedule_config = task.schedule_config or {}
        
        max_attempts = retry_config.get("max_attempts", 10)
        interval_seconds = retry_config.get("interval_seconds", 5)
        success_condition = retry_config.get("success_condition")
        stop_condition = retry_config.get("stop_condition")
        key_message = retry_config.get("key_message")
        time_diff = task.time_diff or 0
        
        attempt = 0
        
        logger.info(f"[{task.name}] 开始重试任务，最大尝试次数: {max_attempts}, 间隔: {interval_seconds}秒")
        if success_condition:
            logger.info(f"[{task.name}] 成功条件: {success_condition}")
        if key_message:
            logger.info(f"[{task.name}] 关键消息: {key_message}")
        if stop_condition:
            logger.info(f"[{task.name}] 停止条件: {stop_condition}")
        
        # 判断是否有明确的停止条件
        has_explicit_stop_condition = bool(success_condition or key_message or stop_condition)
        if not has_explicit_stop_condition:
            logger.info(f"[{task.name}] 未设置成功/停止条件，将执行完所有 {max_attempts} 次重试")
        
        # 等待开始时间（如果设置了）
        if schedule_config.get("type") == "datetime" and schedule_config.get("start_time"):
            self._wait_for_start_time(schedule_config.get("start_time"), time_diff)
        
        while attempt < max_attempts and not self.stop_flag.is_set():
            attempt += 1
            logger.info(f"[{task.name}] 第 {attempt}/{max_attempts} 次尝试")
            
            # 执行请求
            success, result = self._execute_request_with_attempt(task, request, attempt)
            
            if success and result:
                response_body = result.get("response_body", "")
                response_code = result.get("status_code", 0)
                
                logger.debug(f"[{task.name}] 第 {attempt} 次请求成功，状态码: {response_code}")
                
                # 检查停止条件（优先级最高）
                if stop_condition and self._check_stop_condition(response_body, response_code, stop_condition):
                    logger.info(f"[{task.name}] 停止条件满足，任务终止 (尝试次数: {attempt})")
                    self._update_task_completed(task.id, False)
                    break
                    
                # 检查关键字（如果设置了）
                if key_message and key_message.lower() in response_body.lower():
                    logger.info(f"[{task.name}] 找到关键字 '{key_message}'，任务成功完成")
                    self._update_task_completed(task.id, True)
                    break
                
                # 检查成功条件
                if success_condition:
                    # 明确设置了成功条件，按条件判断
                    if self._check_success_condition(response_body, response_code, success_condition):
                        logger.info(f"[{task.name}] 成功条件满足，任务完成 (尝试次数: {attempt})")
                        self._update_task_completed(task.id, True)
                        break
                    else:
                        logger.debug(f"[{task.name}] 第 {attempt} 次请求完成，但未满足成功条件，继续重试")
                else:
                    # 没有设置明确的成功条件
                    if has_explicit_stop_condition:
                        # 有其他停止条件（如关键字），使用默认HTTP成功判断
                        if self._check_success_condition(response_body, response_code, None):
                            logger.info(f"[{task.name}] HTTP请求成功(状态码: {response_code})，任务完成 (尝试次数: {attempt})")
                            self._update_task_completed(task.id, True)
                            break
                        else:
                            logger.debug(f"[{task.name}] 第 {attempt} 次请求失败(状态码: {response_code})，继续重试")
                    else:
                        # 没有任何停止条件，记录执行但继续重试
                        logger.debug(f"[{task.name}] 第 {attempt} 次请求完成(状态码: {response_code})，继续重试直到完成所有尝试")
                        
            else:
                logger.warning(f"[{task.name}] 第 {attempt} 次尝试失败: {result.get('error_message', '未知错误') if result else '请求执行失败'}")
            
            # 如果不是最后一次尝试，等待间隔时间（参考demo.py的等待逻辑）
            if attempt < max_attempts and not self.stop_flag.is_set():
                if interval_seconds > 0:
                    logger.debug(f"[{task.name}] 等待 {interval_seconds} 秒后进行下次尝试...")
                    time.sleep(interval_seconds)
                else:
                    logger.debug(f"[{task.name}] 间隔为0秒，立即进行下次尝试")
        
        # 如果所有尝试都完成了
        if attempt >= max_attempts:
            if has_explicit_stop_condition:
                logger.error(f"[{task.name}] 已达到最大尝试次数 ({max_attempts})，任务失败")
                self._update_task_completed(task.id, False)
            else:
                logger.info(f"[{task.name}] 已完成所有 {max_attempts} 次重试，任务完成")
                self._update_task_completed(task.id, True)
    
    def _wait_for_start_time(self, start_time_str: str, time_diff: float = 0) -> None:
        """等待开始时间 - 参考demo.py的wait_for_start_time逻辑，使用网络时间"""
        try:
            # 解析目标时间（支持毫秒）
            target_time = network_time_service.parse_time_with_ms(start_time_str)
            
            # 如果只有时间没有日期，使用今天的日期
            if target_time.year == 1900:  # strptime默认年份
                today = datetime.now().date()
                target_time = datetime.combine(today, target_time.time())
            
            # 应用时间差调整
            if time_diff != 0:
                target_time = target_time + timedelta(seconds=time_diff)
                logger.info(f"任务 {self.task_id} 应用时间差调整: {time_diff}秒，目标时间: {network_time_service.format_time_with_ms(target_time)}")
            else:
                logger.info(f"任务 {self.task_id} 目标时间: {network_time_service.format_time_with_ms(target_time)}")
            
            # 同步网络时间
            logger.info("正在同步网络时间...")
            network_time_service.sync_time_diff()
            
            last_log_time = None
            
            while True:
                # 使用网络时间进行比较
                current_network_time = network_time_service.get_current_network_time()
                
                # 计算时间差（毫秒精度）
                time_diff_seconds = (target_time - current_network_time).total_seconds()
                
                # 每5秒打印一次等待信息
                now_timestamp = time.time()
                if last_log_time is None or now_timestamp - last_log_time >= 5:
                    if time_diff_seconds > 0:
                        logger.info(f"任务 {self.task_id} 等待中... 还需 {time_diff_seconds:.3f} 秒，当前网络时间: {network_time_service.format_time_with_ms(current_network_time)}")
                    last_log_time = now_timestamp
                
                # 检查是否到达目标时间（考虑毫秒精度）
                if time_diff_seconds <= 0.001:  # 1毫秒容错
                    logger.info(f"任务 {self.task_id} 开始时间到达！当前网络时间: {network_time_service.format_time_with_ms(current_network_time)}")
                    break
                
                # 动态调整睡眠时间
                if time_diff_seconds > 10:
                    # 还有很长时间，每秒检查一次
                    sleep_time = 1.0
                elif time_diff_seconds > 1:
                    # 还有几秒，每100毫秒检查一次
                    sleep_time = 0.1
                else:
                    # 最后1秒，每10毫秒检查一次
                    sleep_time = 0.01
                
                time.sleep(sleep_time)
                
                # 检查是否被停止
                if self.stop_flag.is_set():
                    logger.info(f"任务 {self.task_id} 在等待期间被停止")
                    return
                    
        except Exception as e:
            logger.error(f"任务 {self.task_id} 解析开始时间失败: {e}")
            logger.info(f"任务 {self.task_id} 跳过时间等待，立即开始执行")
    
    def _check_success_condition(self, response_body: str, response_code: int, success_condition: str) -> bool:
        """检查成功条件"""
        if not success_condition:
            # 默认成功条件：状态码为2xx（成功状态码）
            return 200 <= response_code < 300
            
        try:
            # 支持简单的条件表达式
            if "status_code" in success_condition:
                # 替换变量并计算条件
                condition = success_condition.replace("response.status_code", str(response_code))
                return eval(condition)
            elif "response_body" in success_condition:
                # 简单的字符串包含检查
                if "contains" in success_condition:
                    # 例如: response_body.contains('success')
                    match = success_condition.split("contains")
                    if len(match) == 2:
                        search_text = match[1].strip().strip("()\"'")
                        return search_text.lower() in response_body.lower()
                else:
                    # 直接文本替换和计算
                    condition = success_condition.replace("response_body", f"'{response_body}'")
                    return eval(condition)
            else:
                # 直接作为响应体关键字检查
                return success_condition.lower() in response_body.lower()
        except Exception as e:
            logger.error(f"评估成功条件失败: {e}, 条件: {success_condition}")
            # 评估失败时，回退到默认逻辑（HTTP状态码检查）
            return 200 <= response_code < 300
    
    def _check_stop_condition(self, response_body: str, response_code: int, stop_condition: str) -> bool:
        """检查停止条件"""
        if not stop_condition:
            return False
            
        try:
            if "status_code" in stop_condition:
                return eval(stop_condition.replace("response.status_code", str(response_code)))
            elif "response_body" in stop_condition:
                condition = stop_condition.replace("response_body", f"'{response_body}'")
                return eval(condition)
            else:
                return stop_condition.lower() in response_body.lower()
        except Exception as e:
            logger.error(f"评估停止条件失败: {e}")
            return False
    
    def _execute_request_with_attempt(self, task: Task, request: HttpRequest, attempt_number: int) -> tuple[bool, Optional[Dict[str, Any]]]:
        """执行HTTP请求并记录尝试次数"""
        try:
            # 获取代理（参考demo.py的代理轮换逻辑）
            proxy = self.proxy_manager.get_random_proxy(task.proxy_config)
            if proxy:
                logger.debug(f"[{task.name}] 使用代理: {proxy}")
            
            # 执行请求
            result = self.executor.execute_request(
                request=request,
                proxy=proxy
            )
            
            # 记录执行结果（包含尝试次数）
            self._record_execution(task, request, result, proxy, attempt_number)
            
            return result.get("success", False), result
            
        except Exception as e:
            logger.error(f"[{task.name}] 第 {attempt_number} 次请求执行失败: {e}")
            # 记录错误
            error_result = {
                "success": False,
                "error_message": str(e),
                "proxy_used": None
            }
            self._record_execution(task, request, error_result, None, attempt_number)
            return False, None
    
    def _update_task_completed(self, task_id: int, success: bool) -> None:
        """更新任务完成状态"""
        try:
            with get_db_context() as db:
                task_service = TaskService(db)
                new_status = TaskStatusEnum.COMPLETED if success else TaskStatusEnum.FAILED
                task_service.update_task_status(task_id, new_status)
                logger.info(f"任务 {task_id} 状态更新为: {new_status.value}")
        except Exception as e:
            logger.error(f"任务 {task_id} 更新任务状态失败: {e}")
    
    def _record_execution(self, task: Task, request: HttpRequest, result: Dict[str, Any], proxy: Optional[str] = None, attempt_number: int = 1) -> None:
        """记录执行结果到数据库"""
        try:
            with get_db_context() as db:
                # 确定执行状态
                if result.get("success"):
                    status = ExecutionStatusEnum.SUCCESS
                elif "timeout" in result.get("error_message", "").lower():
                    status = ExecutionStatusEnum.TIMEOUT
                else:
                    status = ExecutionStatusEnum.FAILED
                
                # 创建执行记录，使用基本数据而不是对象引用
                execution_record = ExecutionRecord(
                    task_id=task.id,
                    request_id=request.id,
                    status=status,
                    request_url=request.url,
                    request_headers=request.headers,
                    request_body=request.body,
                    proxy_used=proxy or result.get("proxy_used"),
                    response_code=result.get("status_code"),
                    response_headers=result.get("response_headers"),
                    response_body=result.get("response_body"),
                    response_time=result.get("response_time"),
                    error_message=result.get("error_message"),
                    thread_id=str(threading.current_thread().ident),
                    attempt_number=attempt_number,
                    execution_time=datetime.now()
                )
                
                db.add(execution_record)
                db.commit()
                
                # 更新任务统计
                task_service = TaskService(db)
                task_service.increment_execution_count(
                    task.id, 
                    success=result.get("success", False)
                )
                
        except Exception as e:
            logger.error(f"任务 {task.id} 记录执行结果失败: {e}")
            import traceback
            traceback.print_exc()
    
    def stop(self) -> None:
        """停止任务"""
        self.stop_flag.set()
    
    def _execute_request(self, task: Task, request: HttpRequest) -> None:
        """执行单次请求 - 基于demo.py的单次执行逻辑"""
        try:
            # 获取代理
            proxy = self.proxy_manager.get_random_proxy(task.proxy_config)
            if proxy:
                logger.debug(f"[{task.name}] 使用代理: {proxy}")
            
            # 执行请求
            result = self.executor.execute_request(
                request=request,
                proxy=proxy
            )
            
            # 记录执行结果
            self._record_execution(task, request, result, proxy, 1)
            
            # 根据执行结果更新任务状态
            success = result.get("success", False)
            self._update_task_completed(task.id, success)
            
            if success:
                logger.info(f"[{task.name}] 单次任务执行成功")
            else:
                logger.warning(f"[{task.name}] 单次任务执行失败: {result.get('error_message', '未知错误')}")
                
        except Exception as e:
            logger.error(f"[{task.name}] 单次任务执行异常: {e}")
            import traceback
            traceback.print_exc()
            # 记录错误
            error_result = {
                "success": False,
                "error_message": str(e),
                "proxy_used": None
            }
            self._record_execution(task, request, error_result, None, 1)
            self._update_task_completed(task.id, False)


class SchedulerService:
    """调度服务"""
    
    def __init__(self):
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=settings.default_thread_count)
        self.task_futures: Dict[int, Future] = {}  # 任务ID -> Future
        self.check_interval = 10  # 检查间隔（秒）
        
    def start(self) -> None:
        """启动调度服务"""
        if self.running:
            logger.warning("调度服务已在运行")
            return
        
        self.running = True
        logger.info("调度服务启动")
        
        # 启动调度线程
        scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        scheduler_thread.start()
    
    def stop(self) -> None:
        """停止调度服务"""
        if not self.running:
            return
        
        self.running = False
        
        # 停止所有正在运行的任务
        for task_id, future in self.task_futures.items():
            logger.info(f"停止任务 {task_id}")
            future.cancel()
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        logger.info("调度服务已停止")
    
    def _scheduler_loop(self) -> None:
        """调度循环"""
        while self.running:
            try:
                with get_db_context() as db:
                    task_service = TaskService(db)
                    
                    # 获取待执行的任务
                    pending_tasks = task_service.get_pending_tasks()
                    
                    for task in pending_tasks:
                        if task.id not in self.task_futures:
                            self._execute_task(task, db)
                    
                    # 清理已完成的任务
                    self._cleanup_completed_tasks()
                    
            except Exception as e:
                logger.error(f"调度循环异常: {e}")
            
            # 等待下次检查
            time.sleep(self.check_interval)
    
    def _execute_task(self, task: Task, db: Session) -> None:
        """执行任务"""
        try:
            # 获取关联的请求
            request = db.query(HttpRequest).filter(HttpRequest.id == task.request_id).first()
            if not request:
                logger.error(f"任务 {task.name} 关联的请求不存在")
                return
            
            # 更新任务状态为运行中
            task_service = TaskService(db)
            task_service.update_task_status(task.id, TaskStatusEnum.RUNNING)
            
            # 创建任务执行器，传递ID而不是对象来避免跨线程会话问题
            task_runner = TaskRunner(task.id, request.id)
            
            # 根据线程数配置执行
            thread_count = task.thread_count or 1
            
            if thread_count == 1:
                # 单线程执行
                future = self.executor.submit(task_runner.run)
                self.task_futures[task.id] = future
            else:
                # 多线程执行
                futures = []
                for i in range(thread_count):
                    # 为每个线程创建独立的TaskRunner实例
                    runner = TaskRunner(task.id, request.id)
                    future = self.executor.submit(runner.run)
                    futures.append(future)
                
                # 使用第一个future作为主要跟踪对象
                self.task_futures[task.id] = futures[0]
            
            logger.info(f"任务 {task.name} 开始执行，线程数: {thread_count}")
            
        except Exception as e:
            logger.error(f"执行任务 {task.name} 失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _cleanup_completed_tasks(self) -> None:
        """清理已完成的任务"""
        completed_task_ids = []
        
        for task_id, future in self.task_futures.items():
            if future.done():
                completed_task_ids.append(task_id)
                
                try:
                    # 检查任务是否有异常
                    result = future.result()
                except Exception as e:
                    logger.error(f"任务 {task_id} 执行异常: {e}")
                    
                    # 更新任务状态为失败
                    try:
                        with get_db_context() as db:
                            task_service = TaskService(db)
                            task_service.update_task_status(task_id, TaskStatusEnum.FAILED)
                    except Exception:
                        pass
        
        # 从跟踪列表中移除已完成的任务
        for task_id in completed_task_ids:
            del self.task_futures[task_id]
    
    def stop_task(self, task_id: int) -> bool:
        """停止指定任务"""
        logger.info(f"尝试停止任务 {task_id}")
        
        # 检查任务是否在执行队列中
        if task_id in self.task_futures:
            future = self.task_futures[task_id]
            success = future.cancel()
            
            logger.info(f"任务 {task_id} Future.cancel() 结果: {success}")
            
            if success:
                # 成功取消，从跟踪列表中移除
                del self.task_futures[task_id]
                logger.info(f"任务 {task_id} 已从执行队列中移除")
            else:
                # 取消失败，可能任务已经在执行中，强制移除并设置停止标志
                logger.warning(f"任务 {task_id} 无法取消，可能已在执行中，尝试强制停止")
                del self.task_futures[task_id]
                success = True  # 认为停止成功
                
                # 更新数据库中的任务状态
                try:
                    with get_db_context() as db:
                        task_service = TaskService(db)
                        task_service.update_task_status(task_id, TaskStatusEnum.STOPPED)
                    logger.info(f"任务 {task_id} 状态已更新为 STOPPED")
                except Exception as e:
                    logger.error(f"更新任务 {task_id} 状态失败: {e}")
                    return False
            
            return success
        else:
            # 任务不在执行队列中，可能是pending状态还未被调度器执行
            logger.info(f"任务 {task_id} 不在执行队列中，检查数据库状态")
            
            try:
                with get_db_context() as db:
                    task_service = TaskService(db)
                    task = task_service.get_task(task_id)
                    
                    if not task:
                        logger.error(f"任务 {task_id} 不存在")
                        return False
                    
                    if task.status in [TaskStatusEnum.PENDING, TaskStatusEnum.RUNNING]:
                        # 直接更新状态为停止
                        task_service.update_task_status(task_id, TaskStatusEnum.STOPPED)
                        logger.info(f"任务 {task_id} 状态从 {task.status} 更新为 STOPPED")
                        return True
                    else:
                        logger.warning(f"任务 {task_id} 状态为 {task.status}，无需停止")
                        return False
                        
            except Exception as e:
                logger.error(f"停止任务 {task_id} 时发生异常: {e}")
            return False
    
    def get_running_task_count(self) -> int:
        """获取正在运行的任务数量"""
        return len(self.task_futures)


# 全局调度服务实例
scheduler_service = SchedulerService() 