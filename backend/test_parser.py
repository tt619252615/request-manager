#!/usr/bin/env python3
"""
测试 Fiddler 和 cURL 解析器
"""

import json
from backend.app.utils.parser import FiddlerParser, CurlParser, validate_parsed_request

def test_fiddler_parser():
    """测试 Fiddler 解析器"""
    print("🔍 测试 Fiddler 解析器...")
    
    # 读取测试数据
    with open('./backend/test_fiddler_data.txt', 'r', encoding='utf-8') as f:
        raw_data = f.read()
    
    try:
        # 解析数据
        parsed = FiddlerParser.parse(raw_data)
        
        # 验证结果
        is_valid, errors = validate_parsed_request(parsed)
        
        print(f"✅ 解析成功!")
        print(f"   方法: {parsed.method}")
        print(f"   URL: {parsed.url}")
        print(f"   请求头数量: {len(parsed.headers)}")
        print(f"   查询参数数量: {len(parsed.params)}")
        print(f"   请求体长度: {len(parsed.body) if parsed.body else 0}")
        print(f"   验证结果: {'✅ 有效' if is_valid else '❌ 无效'}")
        
        if not is_valid:
            print(f"   错误: {', '.join(errors)}")
        
        # 显示部分解析结果
        print("\n📋 解析详情:")
        print(f"   主机: {parsed.headers.get('host', 'N/A')}")
        print(f"   内容类型: {parsed.headers.get('content-type', 'N/A')}")
        print(f"   用户代理: {parsed.headers.get('user-agent', 'N/A')[:50]}...")
        
        return parsed
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return None

def test_curl_parser():
    """测试 cURL 解析器"""
    print("\n🔍 测试 cURL 解析器...")
    
    # 测试 cURL 命令
    curl_command = """
    curl -X POST 'https://api.example.com/users' \
      -H 'Content-Type: application/json' \
      -H 'Authorization: Bearer token123' \
      -d '{"name": "test", "email": "test@example.com"}'
    """
    
    try:
        # 解析命令
        parsed = CurlParser.parse(curl_command)
        
        # 验证结果
        is_valid, errors = validate_parsed_request(parsed)
        
        print(f"✅ 解析成功!")
        print(f"   方法: {parsed.method}")
        print(f"   URL: {parsed.url}")
        print(f"   请求头数量: {len(parsed.headers)}")
        print(f"   请求体: {parsed.body}")
        print(f"   验证结果: {'✅ 有效' if is_valid else '❌ 无效'}")
        
        if not is_valid:
            print(f"   错误: {', '.join(errors)}")
        
        return parsed
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return None

def main():
    """主函数"""
    print("🚀 RequestManager 解析器测试")
    print("=" * 50)
    
    # 测试 Fiddler 解析器
    fiddler_result = test_fiddler_parser()
    
    # 测试 cURL 解析器  
    curl_result = test_curl_parser()
    
    print("\n" + "=" * 50)
    print("📊 测试总结:")
    print(f"   Fiddler 解析: {'✅ 成功' if fiddler_result else '❌ 失败'}")
    print(f"   cURL 解析: {'✅ 成功' if curl_result else '❌ 失败'}")

if __name__ == "__main__":
    main() 