#!/usr/bin/env python3
"""
测试重试功能
"""
import requests
import json
import time


def test_retry_task():
    """测试重试任务功能"""
    print("🧪 测试重试任务功能")
    print("="*60)
    
    # 1. 创建一个简单的GET请求用于测试
    print("📤 创建测试请求...")
    
    request_payload = {
        "name": "重试测试请求",
        "description": "用于测试重试功能的HTTP请求",
        "method": "GET",
        "url": "https://httpbin.org/status/200",  # 总是返回200状态码
        "headers": {},
        "params": {},
        "body": ""
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/requests/",
            json=request_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                request_id = result['data']['id']
                print(f"✅ 测试请求创建成功: ID={request_id}")
            else:
                print(f"❌ 创建请求失败: {result.get('message')}")
                return
        else:
            print(f"❌ 请求创建失败: HTTP {response.status_code}")
            return
    
    except Exception as e:
        print(f"❌ 创建请求异常: {e}")
        return
    
    # 2. 创建重试任务
    print("⏰ 创建重试任务...")
    
    timestamp = int(time.time())
    task_payload = {
        "name": f"重试测试任务-{timestamp}",
        "description": "测试重试功能的任务",
        "request_id": request_id,
        "task_type": "retry",
        "schedule_config": {
            "type": "immediate",
            "timezone": "Asia/Shanghai"
        },
        "retry_config": {
            "max_attempts": 5,  # 5次尝试
            "interval_seconds": 1,  # 1秒间隔
            "success_condition": None,  # 不设置成功条件，让它重试完所有次数
            "stop_condition": None,
            "key_message": None
        },
        "proxy_config": {
            "enabled": False,
            "rotation": True,
            "timeout": 30
        },
        "thread_count": 1,
        "time_diff": 0
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/tasks",
            json=task_payload
        )
        
        print(f"📊 任务创建响应状态码: {response.status_code}")
        print(f"📄 任务创建响应内容: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                task_id = result['data']['id']
                print(f"✅ 重试任务创建成功: ID={task_id}")
                
                # 3. 启动任务
                print("🚀 启动重试任务...")
                response = requests.post(f"http://localhost:8000/api/tasks/{task_id}/start")
                
                if response.status_code == 200:
                    print("✅ 重试任务启动成功")
                    
                    # 4. 等待一段时间让任务执行
                    print("⏳ 等待任务执行完成...")
                    time.sleep(10)  # 等待10秒
                    
                    # 5. 查看执行记录
                    print("📊 查看执行记录...")
                    response = requests.get(f"http://localhost:8000/api/executions/?task_id={task_id}&limit=10")
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('code') == 0:
                            records = result['data']
                            print(f"📋 执行记录数量: {len(records)}")
                            
                            for i, record in enumerate(records, 1):
                                print(f"  记录 {i}: 尝试第{record['attempt_number']}次, 状态: {record['status']}, 状态码: {record.get('response_code', 'N/A')}")
                                
                            if len(records) == 5:
                                print("✅ 重试功能正常：执行了5次尝试")
                            else:
                                print(f"⚠️ 重试功能异常：期望5次尝试，实际{len(records)}次")
                        else:
                            print(f"❌ 获取执行记录失败: {result.get('message')}")
                    else:
                        print(f"❌ 获取执行记录失败: HTTP {response.status_code}")
                        
                    # 6. 查看任务状态
                    print("📊 查看任务状态...")
                    response = requests.get(f"http://localhost:8000/api/tasks/{task_id}")
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('code') == 0:
                            task_info = result['data']
                            print(f"📋 任务状态: {task_info['status']}")
                            print(f"📊 执行统计: 总计{task_info['execution_count']}, 成功{task_info['success_count']}, 失败{task_info['failure_count']}")
                else:
                    print(f"❌ 任务启动失败: HTTP {response.status_code}")
                    print(f"📝 错误详情: {response.text}")
            else:
                print(f"❌ 任务创建失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ 任务创建失败: HTTP {response.status_code}")
            print(f"📝 错误详情: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试过程异常: {e}")
        import traceback
        traceback.print_exc()


def test_zero_interval_retry():
    """测试0秒间隔重试"""
    print("\n🧪 测试0秒间隔重试功能")
    print("="*60)
    
    # 创建一个简单的GET请求
    request_payload = {
        "name": "0秒重试测试请求",
        "description": "用于测试0秒间隔重试功能",
        "method": "GET", 
        "url": "https://httpbin.org/status/200",
        "headers": {},
        "params": {},
        "body": ""
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/requests/",
            json=request_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                request_id = result['data']['id']
                print(f"✅ 测试请求创建成功: ID={request_id}")
            else:
                print(f"❌ 创建请求失败: {result.get('message')}")
                return
        else:
            print(f"❌ 请求创建失败: HTTP {response.status_code}")
            return
    
    except Exception as e:
        print(f"❌ 创建请求异常: {e}")
        return
    
    # 创建0秒间隔重试任务
    timestamp = int(time.time())
    task_payload = {
        "name": f"0秒重试任务-{timestamp}",
        "description": "测试0秒间隔重试功能",
        "request_id": request_id,
        "task_type": "retry",
        "schedule_config": {
            "type": "immediate",
            "timezone": "Asia/Shanghai"
        },
        "retry_config": {
            "max_attempts": 3,  # 3次尝试
            "interval_seconds": 0,  # 0秒间隔
            "success_condition": None,
            "stop_condition": None,
            "key_message": None
        },
        "proxy_config": {
            "enabled": False,
            "rotation": True,
            "timeout": 30
        },
        "thread_count": 1,
        "time_diff": 0
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/tasks",
            json=task_payload
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                task_id = result['data']['id']
                print(f"✅ 0秒重试任务创建成功: ID={task_id}")
                
                # 启动任务
                print("🚀 启动0秒重试任务...")
                start_time = time.time()
                response = requests.post(f"http://localhost:8000/api/tasks/{task_id}/start")
                
                if response.status_code == 200:
                    print("✅ 0秒重试任务启动成功")
                    
                    # 等待任务执行
                    time.sleep(3)  # 等待3秒应该足够
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    # 查看执行记录
                    response = requests.get(f"http://localhost:8000/api/executions/?task_id={task_id}&limit=10")
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('code') == 0:
                            records = result['data']
                            print(f"📋 执行记录数量: {len(records)}")
                            print(f"⏱️ 总执行时间: {execution_time:.2f}秒")
                            
                            if len(records) == 3:
                                print("✅ 0秒间隔重试功能正常：快速完成了3次尝试")
                            else:
                                print(f"⚠️ 0秒间隔重试功能异常：期望3次尝试，实际{len(records)}次")
                else:
                    print(f"❌ 任务启动失败: HTTP {response.status_code}")
            else:
                print(f"❌ 任务创建失败: {result.get('message', '未知错误')}")
        else:
            print(f"❌ 任务创建失败: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 0秒重试测试异常: {e}")


if __name__ == "__main__":
    print("🎯 RequestManager 重试功能测试")
    print("="*60)
    
    # 测试基本重试功能
    test_retry_task()
    
    # 测试0秒间隔重试
    test_zero_interval_retry()
    
    print("\n✅ 测试完成！")
    print("\n💡 提示：")
    print("  - 如果重试功能正常，应该看到多条执行记录")
    print("  - 每条记录的attempt_number应该递增")
    print("  - 0秒间隔重试应该快速完成") 