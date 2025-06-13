#!/usr/bin/env python3
"""
完整功能测试
"""
import requests
import json
import time

def test_full_workflow():
    """测试完整的工作流程"""
    timestamp = int(time.time())
    
    print("🎯 开始完整功能测试")
    print("=" * 60)
    
    # 1. 导入请求
    print("📥 1. 导入Fiddler请求...")
    
    raw_text = """POST https://rights-apigw.meituan.com/api/rights/activity/secKill/grab?cType=mtiphone&fpPlatform=5&wx_openid=&appVersion=12.35.401&gdBs=0000&pageVersion=1749257933402&yodaReady=h5&csecplatform=4&csecversion=3.2.0 HTTP/2
host: rights-apigw.meituan.com
content-type: application/json

{"activityId":"A1930104757016543294","gdId":601664,"pageId":618337}"""
    
    import_payload = {
        "raw_data": raw_text,
        "name": f"测试请求-{timestamp}",
        "description": "完整功能测试请求"
    }
    
    response = requests.post(
        "http://localhost:8000/api/requests/import/fiddler",
        json=import_payload
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 0:
            request_id = result['data']['id']
            print(f"✅ 请求导入成功: ID={request_id}")
        else:
            print(f"❌ 请求导入失败: {result.get('message')}")
            return
    else:
        print(f"❌ 请求导入失败: HTTP {response.status_code}")
        return
    
    # 2. 创建任务
    print("📋 2. 创建任务...")
    
    task_payload = {
        "name": f"测试任务-{timestamp}",
        "description": "完整功能测试任务",
        "request_id": request_id,
        "task_type": "single",
        "schedule_config": {
            "type": "immediate"
        }
    }
    
    response = requests.post(
        "http://localhost:8000/api/tasks/",
        json=task_payload
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 0:
            task_id = result['data']['id']
            print(f"✅ 任务创建成功: ID={task_id}")
        else:
            print(f"❌ 任务创建失败: {result.get('message')}")
            return
    else:
        print(f"❌ 任务创建失败: HTTP {response.status_code}")
        return
    
    # 3. 获取任务详情
    print("🔍 3. 获取任务详情...")
    
    response = requests.get(f"http://localhost:8000/api/tasks/{task_id}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 0:
            print(f"✅ 任务详情获取成功: {result['data']['name']}")
        else:
            print(f"❌ 获取任务详情失败: {result.get('message')}")
    else:
        print(f"❌ 获取任务详情失败: HTTP {response.status_code}")
    
    # 4. 获取任务列表
    print("📊 4. 获取任务列表...")
    
    response = requests.get("http://localhost:8000/api/tasks/")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 0:
            task_count = len(result['data'])
            print(f"✅ 任务列表获取成功: 共{task_count}个任务")
        else:
            print(f"❌ 获取任务列表失败: {result.get('message')}")
    else:
        print(f"❌ 获取任务列表失败: HTTP {response.status_code}")
    
    # 5. 启动任务
    print("🚀 5. 启动任务...")
    
    response = requests.post(f"http://localhost:8000/api/tasks/{task_id}/start")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 0:
            print(f"✅ 任务启动成功: {result['data']['status']}")
        else:
            print(f"❌ 任务启动失败: {result.get('message')}")
    else:
        print(f"❌ 任务启动失败: HTTP {response.status_code}")
    
    # 6. 停止任务
    print("⏹️ 6. 停止任务...")
    
    response = requests.post(f"http://localhost:8000/api/tasks/{task_id}/stop")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 0:
            print(f"✅ 任务停止成功: {result['data']['status']}")
        else:
            print(f"❌ 任务停止失败: {result.get('message')}")
    else:
        print(f"❌ 任务停止失败: HTTP {response.status_code}")
    
    # 7. 获取系统统计
    print("📈 7. 获取系统统计...")
    
    response = requests.get("http://localhost:8000/api/tasks/stats/summary")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 0:
            stats = result['data']
            print(f"✅ 系统统计: 总计{stats['total']}个任务")
        else:
            print(f"❌ 获取统计失败: {result.get('message')}")
    else:
        print(f"❌ 获取统计失败: HTTP {response.status_code}")
    
    print("=" * 60)
    print("🎉 完整功能测试完成！")

if __name__ == "__main__":
    test_full_workflow() 