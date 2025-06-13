#!/usr/bin/env python3
"""
简单的任务创建测试
"""
import requests
import json
import time

def test_create_task():
    # 使用已有的请求ID（从前面的测试知道ID=9存在）
    timestamp = int(time.time())
    
    task_payload = {
        "name": f"测试任务-{timestamp}",
        "description": "简单测试任务",
        "request_id": 9,  # 使用已知存在的请求ID
        "task_type": "single",
        "schedule_config": {
            "type": "immediate"
        }
    }
    
    print("🔍 创建简单任务...")
    print(f"📋 任务数据: {json.dumps(task_payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/tasks/",
            json=task_payload,
            timeout=30
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        print(f"📝 响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 任务创建成功")
            print(f"📋 返回数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 任务创建失败")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_create_task() 