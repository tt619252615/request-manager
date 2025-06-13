#!/usr/bin/env python3
"""
测试任务管理功能
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"


def test_create_request():
    """测试创建请求"""
    print("🔍 测试创建HTTP请求...")
    
    url = f"{BASE_URL}/api/requests/"
    data = {
        "name": "测试美团请求",
        "description": "美团抢购API测试",
        "method": "POST",
        "url": "https://rights-apigw.meituan.com/api/rights/activity/secKill/grab",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15"
        },
        "params": {
            "cType": "mtiphone",
            "fpPlatform": "5",
            "appVersion": "12.35.401"
        },
        "body": json.dumps({
            "activityId": "A1930104757016543294",
            "gdId": 601664,
            "pageId": 618337
        }),
        "tags": ["test", "meituan"]
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get("code") == 0:
            request_id = result["data"]["id"]
            print(f"✅ 请求创建成功，ID: {request_id}")
            return request_id
        else:
            print(f"❌ 请求创建失败: {result.get('message')}")
            return None
            
    except Exception as e:
        print(f"❌ 请求创建异常: {e}")
        return None


def test_create_task(request_id):
    """测试创建任务"""
    print("\n🔍 测试创建任务...")
    
    url = f"{BASE_URL}/api/tasks/"
    data = {
        "name": "美团抢购任务",
        "description": "自动抢购美团优惠券",
        "request_id": request_id,
        "task_type": "RETRY",
        "schedule_config": {
            "type": "IMMEDIATE",
            "start_time": None,
            "cron_expression": None,
            "interval_seconds": None
        },
        "retry_config": {
            "max_attempts": 10,
            "interval_seconds": 5,
            "success_condition": "response.text.contains('success')",
            "stop_condition": "response.text.contains('sold_out')"
        },
        "proxy_config": {
            "enabled": False,
            "proxy_url": None,
            "rotation": True
        },
        "thread_count": 3,
        "time_diff": 0.0
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get("code") == 0:
            task_id = result["data"]["id"]
            print(f"✅ 任务创建成功，ID: {task_id}")
            return task_id
        else:
            print(f"❌ 任务创建失败: {result.get('message')}")
            return None
            
    except Exception as e:
        print(f"❌ 任务创建异常: {e}")
        return None


def test_start_task(task_id):
    """测试启动任务"""
    print(f"\n🔍 测试启动任务 {task_id}...")
    
    url = f"{BASE_URL}/api/tasks/{task_id}/start"
    
    try:
        response = requests.post(url)
        result = response.json()
        
        if result.get("code") == 0:
            print("✅ 任务启动成功")
            return True
        else:
            print(f"❌ 任务启动失败: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ 任务启动异常: {e}")
        return False


def test_get_task_status(task_id):
    """测试获取任务状态"""
    print(f"\n🔍 获取任务 {task_id} 状态...")
    
    url = f"{BASE_URL}/api/tasks/{task_id}"
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if result.get("code") == 0:
            task = result["data"]
            print(f"✅ 任务状态: {task['status']}")
            print(f"   执行次数: {task['execution_count']}")
            print(f"   成功次数: {task['success_count']}")
            print(f"   失败次数: {task['failure_count']}")
            return task
        else:
            print(f"❌ 获取任务状态失败: {result.get('message')}")
            return None
            
    except Exception as e:
        print(f"❌ 获取任务状态异常: {e}")
        return None


def test_get_execution_records(task_id):
    """测试获取执行记录"""
    print(f"\n🔍 获取任务 {task_id} 的执行记录...")
    
    url = f"{BASE_URL}/api/executions/"
    params = {"task_id": task_id, "limit": 5}
    
    try:
        response = requests.get(url, params=params)
        result = response.json()
        
        if result.get("code") == 0:
            records = result["data"]
            print(f"✅ 获取到 {len(records)} 条执行记录")
            
            for record in records:
                print(f"   记录ID: {record['id']}, 状态: {record['status']}, 响应时间: {record['response_time']}ms")
            
            return records
        else:
            print(f"❌ 获取执行记录失败: {result.get('message')}")
            return []
            
    except Exception as e:
        print(f"❌ 获取执行记录异常: {e}")
        return []


def test_stop_task(task_id):
    """测试停止任务"""
    print(f"\n🔍 测试停止任务 {task_id}...")
    
    url = f"{BASE_URL}/api/tasks/{task_id}/stop"
    
    try:
        response = requests.post(url)
        result = response.json()
        
        if result.get("code") == 0:
            print("✅ 任务停止成功")
            return True
        else:
            print(f"❌ 任务停止失败: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ 任务停止异常: {e}")
        return False


def test_get_stats():
    """测试获取统计信息"""
    print("\n🔍 获取系统统计信息...")
    
    # 获取任务统计
    task_url = f"{BASE_URL}/api/tasks/stats/summary"
    execution_url = f"{BASE_URL}/api/executions/stats/summary"
    
    try:
        # 任务统计
        response = requests.get(task_url)
        result = response.json()
        
        if result.get("code") == 0:
            stats = result["data"]
            print("✅ 任务统计:")
            print(f"   总任务数: {stats['total']}")
            print(f"   运行中: {stats['running']}")
            print(f"   待执行: {stats['pending']}")
            print(f"   已完成: {stats['completed']}")
            print(f"   已失败: {stats['failed']}")
            print(f"   已停止: {stats['stopped']}")
        
        # 执行统计
        response = requests.get(execution_url)
        result = response.json()
        
        if result.get("code") == 0:
            stats = result["data"]
            print("✅ 执行统计:")
            print(f"   总执行次数: {stats['total_executions']}")
            print(f"   成功次数: {stats['success_count']}")
            print(f"   失败次数: {stats['failed_count']}")
            print(f"   超时次数: {stats['timeout_count']}")
            print(f"   成功率: {stats['success_rate']}%")
            print(f"   平均响应时间: {stats['average_response_time']}ms")
            
    except Exception as e:
        print(f"❌ 获取统计信息异常: {e}")


def main():
    """主函数"""
    print("🚀 RequestManager 任务管理测试")
    print("=" * 50)
    
    # 1. 创建请求
    request_id = test_create_request()
    if not request_id:
        return
    
    # 2. 创建任务
    task_id = test_create_task(request_id)
    if not task_id:
        return
    
    # 3. 启动任务
    if not test_start_task(task_id):
        return
    
    # 4. 等待一段时间，观察任务执行
    print("\n⏰ 等待15秒观察任务执行...")
    time.sleep(15)
    
    # 5. 获取任务状态
    test_get_task_status(task_id)
    
    # 6. 获取执行记录
    test_get_execution_records(task_id)
    
    # 7. 停止任务
    test_stop_task(task_id)
    
    # 8. 获取统计信息
    test_get_stats()
    
    print("\n" + "=" * 50)
    print("📊 测试完成!")


if __name__ == "__main__":
    main() 