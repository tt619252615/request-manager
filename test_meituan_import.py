#!/usr/bin/env python3
"""
测试美团请求导入和任务创建
"""
import requests
import json
import time


def test_import_meituan_request():
    """测试导入美团秒杀请求"""
    
    # 美团秒杀请求的原始数据
    raw_text = """POST https://rights-apigw.meituan.com/api/rights/activity/secKill/grab?cType=mtiphone&fpPlatform=5&wx_openid=&appVersion=12.35.401&gdBs=0000&pageVersion=1749257933402&yodaReady=h5&csecplatform=4&csecversion=3.2.0 HTTP/2
host: rights-apigw.meituan.com
content-type: application/json
x-titans-user: 
accept: application/json, text/plain, */*
sec-fetch-site: same-site
dj-token: BUtNUwMAAABuBktNUwMaOQIAAAABO5rMWgAAACzIq5ReNmVH5ph4XvJNHjVNeL7qlASDaVLvLCCVdHSM9muxsq64z2Dj/NsOiiIsJAb9e/v6erv3fAMZDQLo6Z169pnTn9lGcSGC9hYOIxyItcHhrjaVE1vWsAsAAACFXTK443VCs2gytBxlG+OB4ACS6HqXlJoAv0qfILVCn3hrBagRVTa9EXG33JZGMf/0ZJksHSUcG5s26u0Gsev0zEo/RomvTONOboLrBv6+Jdoofojl0XS4Nrs32FWy1kAIrlu/gqCqV7/oSsi5zRWn+behiEJ8/XoaHBK5JVaCA2l3hir+EQ==
accept-language: zh-CN,zh-Hans;q=0.9
sec-fetch-mode: cors
accept-encoding: gzip, deflate, br
origin: https://market.waimai.meituan.com
user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 TitansX/20.0.1.old KNB/1.0 iOS/18.3.2 meituangroup/com.meituan.imeituan/12.35.401 meituangroup/12.35.401 App/10110/12.35.401 iPhone/iPhone16 WKWebView
referer: https://market.waimai.meituan.com/
content-length: 1642
mtgsig: {"a0":"3.0","a1":"6f50fb51-23ee-4173-ab33-6ee69ed0ef29","a3":24,"a4":1749354908,"a5":"xUNQJWH6MHXVI5ZWByij7Kt/Kfn0Z+yZzHlfYrp4VLNFizSUJrzLpRFTNUffLSYYMQGpTRm3mZHRhLZHzwZQdxRXKJC74xNVqkZvE0LHMUrtwh57lqVYVYJYCgyQypE5Ldul1cruD7tIfwCTlCDPxHSfcXJ2qmHN46sXFe4mFLudF/n0FWqRp+dJy0js53BcQLeEus70KC2JfZcS8ntkZpTiWtwFpQNZURcmTcHGy+T6AphiwC3YJhnTY1emYh6SEftWVd4Rm6t0oRm9Pe/eW8zjtuh+FPtisccJcAc2/IYc/FGOcqB8f9XSghHCh8bmhnzLOkStMPh5hGjhnLEZqCOhyRWEcXqH7prziaKiGOh6oF0RClDaAbYCnJPkpqK1qYCutY5mng==","a6":0,"a7":"2t7LFGpUkNd8aLiDQmjeUqj6BTQ0TFSZ749msFSOHjgq+UVbOIKFWw8Ifz9Kqk/sBdEwo92wsWBVvDVPq6w48HbQE/h0bt7eMLvppEQYNyY=","a8":"5d5fbb05bcba29aa8eaa80a9b6ed2e84fb34fc48d542c88a5f722705","a9":"8123fdadClG4FmnbEuYRT7ZFJUnG3XRERoONtiwT6sKL5MijDCIGSHUZR+v7WjlmHWRQ81PEIJCvLNFfZI+MqvWJEKnSuUYaViKSvF3X7VvXbJLQqpSfJoyYLUKTvX2g3C3ThVyRAKet7F/ngRORDCSySnTbpMwIevjHqiwBgDr2Ym3jLcYjCbCUSbPH/SZ5oaS02We6qw2SE2go63WykLYncGSSx60jyq+z7eJ9zLtCPG3hlMkYFEOK1kP7RrbeHjsrFQBb1+2Ktop5f+CFzAsdZY0B9NS9gibR3S5jqsVTS1cHRdoVOITzyIOVsQPSA/Pn1T4LhpN7jRZtdwM+To0R60TmrP+8n4C0bjbi+chVV9FEQVSTvr4woMT5mQ1/sAM1vpxjQ2XE9UXEYxzcnvFof3JAIzN7xcGfYzvJxbcUiVjqmLBt1KrJ29OgPzlpPRXYCyXb0u7McsOk8EFZdwu5rCSqc1H1xgJnAl+pg5Xso5vrxpBdyTmzEOWc4TBJ1gC18YVRxTKw3nwupgWT/PkV8ff5/GqapGxl5aXAq/AmtmIakSpFWBgkC1rF+P+W5g2qVzz1RASf9ZzmFwLjDQkhm5tYfPJisuMEYVrb0UewsIhiHvEc+DXHpcRRugH4lt7CXHt4GTT1OkqVfRQ7JiL9UcCR3Qm4/SvVyjjiOXJzxs7XBok=","a10":"5,107,1.1.6","x0":2,"a2":"4ea11c960a67c35018309a88037807a0"}
sec-fetch-dest: empty
cookie: WEBDFPID=00w1uxz2z50355wy0u538116yzwx5z83806vwz88u8787958vuy7z420-1749371701358-1734858579699IOUASUM868c0ee73ab28e1d0b03bc83148500064154; _lx_utm=utm_campaign%3DAgroupBgroupG%26utm_term%3D12.35.401%26utm_source%3DAppStore%26utm_content%3D0000000000000B8F7A5DB1B8A4D62B7C7C92BA09F7FC6A172889973849519258%26utm_medium%3Diphone; isUuidUnion=true; iuuid=0000000000000FB9BD0471D96498CB2FD7607B914CB4AA168291068747963772; network=5g; _utm_campaign=AgroupBgroupD100Ghomepage_category1_394__a1__c__eH0; _utm_content=0000000000000B8F7A5DB1B8A4D62B7C7C92BA09F7FC6A172889973849519258; _utm_medium=iphone; _utm_source=AppStore; _utm_term=12.35.401; cityid=59; dpid=; token=AgEOKC8U6Yj2cL4PYrRw7XUobN_lNiovZx3GI-63N5ayCPwcRfA9IA71pySJPy7XetpNimd0sfk4IBEAAACDKQAA31bCmX5nX4nxJbhyM1gyoxtfrmgSg_t814wciR-LWe2z5iIhaf25wXte5rd1TSubRhlWTpN2mBDfEgWIxgQZ8A; uuid=0000000000000B8F7A5DB1B8A4D62B7C7C92BA09F7FC6A172889973849519258; mt_c_token=AgEOKC8U6Yj2cL4PYrRw7XUobN_lNiovZx3GI-63N5ayCPwcRfA9IA71pySJPy7XetpNimd0sfk4IBEAAACDKQAA31bCmX5nX4nxJbhyM1gyoxtfrmgSg_t814wciR-LWe2z5iIhaf25wXte5rd1TSubRhlWTpN2mBDfEgWIxgQZ8A; _lxsdk_s=1974d931737-99f-b3b-745%7C747282237%7CNaN; _lxsdk=0000000000000B8F7A5DB1B8A4D62B7C7C92BA09F7FC6A172889973849519258; _pgy_wink_fd_fe_maidan={"config":{"delta":5000,"abSyncLayerId":"31824"},"report":{"31824":"k","31824_s":"true","31824_f":"ehc"}}; _pgy_wink_fe_expense={"report":{"25934":"a","33442":"strategy_a","25934_s":"true","25934_f":"ehc","33442_s":"true","33442_f":"ehc"}}; lt=AgEOKC8U6Yj2cL4PYrRw7XUobN_lNiovZx3GI-63N5ayCPwcRfA9IA71pySJPy7XetpNimd0sfk4IBEAAACDKQAA31bCmX5nX4nxJbhyM1gyoxtfrmgSg_t814wciR-LWe2z5iIhaf25wXte5rd1TSubRhlWTpN2mBDfEgWIxgQZ8A; n=DpI269379706; _hc.v=e3b88931-5544-7f74-8fe5-2a59b8deffa3.1740498858; fd_maidan_accessno=; fd_maidan_skipLandingAndResult=; fd_maidan_utm_source=creditpay_app-others-outerchannel_797836; fd_yuefu_open_type=H5; is_from_feed=; maidan_utm_source=creditpay_app-others-outerchannel_797836; userId=747282237; NDFPID=5d5fbb05bcba29aa8eaa80a9b6ed2e84fb34fc48d542c88a5f722705; ta.uuid=1870758587061035028; _lxsdk_cuid=193eda0c37cc8-08c421253fb5138-1a576908-51bf4-193eda0c37cc8; _lxsdk_dpid=b8f7a5db1b8a4d62b7c7c92ba09f7fc6a172889973849519258; _lxsdk_unoinid=e138d48699104a7092852dbd789c8af0a172889973879733960

{"activityId":"A1930104757016543294","gdId":601664,"pageId":618337,"instanceId":"17490090128760.4805414218792613","rightCode":"R1930108317557674036","roundCode":"ROUND1930109662054244380","grabToken":"13418068095eb56a01959315e202d69d","mtFingerprint":"i2HKpOmsirDPavelVfQBZMuuHn/EPK3O2hg5MxEB8dJ3I56a+QKRiTxwwQZzWBaAPPhR1dlTgeXl/t4luI4HNsfWZPNIz6xtM+7DYJuUveIgqNS/oM1Su8PJ4ELhOnvMwH8iqbe2oVXJjjds7DqoHsnhyRulfpEpROlOOTSRiPg21Oe1KD4UYDvlgrrZ1Is3/c+wxdV24TsUKXUyLRpf0kEbTBJQ2UqNrHyMAfh/5Uwdvg66dSpPqx2s/sgRuack5Idq+yfqTMjGglQGyIziLKGpIPjirjzR+mIH1s3mD05GVqxmZxKuzIpQujVGc6inZVI6lX/RR4043zxgR6jOa1AiYSJQZzefU8o+f6crgVLWAdvDhpeCiooc5zZaRRxNEft/ElUUteGe8FIcCZVZhK+pyfevMHXM2/IwqbCEi25kD9uAjWX3de4cnO8X2iiTtq6BWaSadOrivmG4bKY/M/iqxunIFa7tbk1DKXuauKKVzEeldXCg31HRZ7PBMy7Wdz+ZUL4Gv3lH/jEtqKXssMM16D8qkszPv9X+4M+g2ZmcruzJQSu/NvddCxc/G5mcQWKBvXa6Q+JM7OlsVBO6WpBzWcfcTfUtqx06+chwHBajsqRp1sXqmQ8hPWoJjVxuZUzzJ594rALNq9mfP7u7AzyLTWY1zO+cFvqpRXxTvQgU5JmoiuXXdWdMatGAA+bP/cVTWix/k8XU/q7iXq7a3NOVWM0+J+762l3K0IMPJK2Uu4xxupvOUDcl3YewnvvmWQYv9N1YRq9r7xuYSnD4Uq0+mNJaVL7Yt7B/lgOVqu/n8U8oIOFjUouKrbVAb2xxuw/lLk+t7jdBsjEB2wIEzd2KZcbYdHsAGb7o3Vy8lndTHhUQTMWWHdE1oGfMv+2kHw8tcTinY5v5VHEIOOSrhL9KRRrha5gbPBoR1id8aYmEt70JNQKyTDFwrU3tEVzEpILHzmUH6iZzlKkj9QG4OmUsMUOucO5VKVvaLIXFL9S7vl4VDI5Sl/HOZexz/8UaLUWyOKa9zSoiWmUPN2vCrgzu3DW1TpCPNoPj06NKz2LwOHKcYeBq7PTdVM2smetDZjGebUVJTVvGwx1eMpnppclIMn+GJm78W64Qov+j8Db0g5dkIGYfHL2wBorgI9nXI5ETbEy3hq+GCo6SMXf7abqx6SJT+SYeqC/4hHPM4/LDV0h3N49nwmg3ovRbb1rjsdNe83JAgN6Fa0JSsOVFJkfKHEZ1oeuUfZiCy1OV037iywrD9S48Ojl1PVyOdYLbYbFiciEVeeqqFVLzScAIYtqhDAiCkPC7mGESpcJY7ZE8Q23UrGfFKFNfsdueMbHNY3wPTpac5WX+8JTb9o/mgazRuyrvbZvmfxaTAkConRo="}"""
    
    # 1. 导入Fiddler请求
    print("📥 导入美团秒杀请求...")
    
    # 添加时间戳使名称唯一
    timestamp = int(time.time())
    
    import_payload = {
        "raw_data": raw_text,
        "name": f"美团秒杀接口-{timestamp}", 
        "description": "美团权益秒杀抢购接口"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/requests/import/fiddler",
            json=import_payload,
            timeout=10
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应内容: {response.text[:500]}...")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API调用成功")
            print(f"📋 响应结构: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 检查响应数据结构
            if 'data' in result and result['data'] is not None:
                request_id = result['data']['id']
                print(f"✅ 请求导入成功: ID={request_id}")
                
                # 2. 创建定时任务
                print("⏰ 创建定时任务...")
                
                task_payload = {
                    "name": f"美团秒杀任务-{timestamp}",
                    "description": "美团权益秒杀自动抢购",
                    "request_id": request_id,
                    "task_type": "single",
                    "schedule_config": {
                        "type": "immediate",
                        "timezone": "Asia/Shanghai"
                    },
                    "retry_config": {
                        "max_attempts": 10,
                        "interval_seconds": 5
                    },
                    "proxy_config": {
                        "enabled": False,
                        "rotation": True,
                        "timeout": 30
                    },
                    "thread_count": 1,
                    "time_diff": 0
                }
                
                response = requests.post(
                    "http://localhost:8000/api/tasks",
                    json=task_payload
                )
                
                print(f"📊 任务创建响应状态码: {response.status_code}")
                print(f"📄 任务创建响应内容: {response.text[:500]}...")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 0 and result.get('data'):
                        task_id = result['data']['id']
                        print(f"✅ 任务创建成功: ID={task_id}")
                        
                        # 3. 启动任务
                        print("🚀 启动任务...")
                        response = requests.post(f"http://localhost:8000/api/tasks/{task_id}/start")
                        
                        if response.status_code == 200:
                            print("✅ 任务启动成功")
                            
                            # 4. 查看任务状态
                            print("📊 查看任务状态...")
                            response = requests.get(f"http://localhost:8000/api/tasks/{task_id}")
                            if response.status_code == 200:
                                task_info = response.json()
                                print(f"📋 任务状态: {task_info['data']['status']}")
                                if 'next_execution_time' in task_info['data']:
                                    print(f"🔗 下次执行: {task_info['data']['next_execution_time']}")
                        
                        else:
                            print(f"❌ 任务启动失败: HTTP {response.status_code}")
                            print(f"📝 错误详情: {response.text}")
                    else:
                        print(f"❌ 任务创建失败: {result.get('message', '未知错误')}")
                        print(f"📋 错误详情: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                else:
                    print(f"❌ 任务创建失败: HTTP {response.status_code}")
                    print(f"📝 错误详情: {response.text}")
                    try:
                        error_data = response.json()
                        print(f"📋 错误结构: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
                    except:
                        print(f"📝 原始响应: {response.text}")
            else:
                print(f"❌ 响应数据异常: data字段为空或不存在")
                if 'message' in result:
                    print(f"📝 错误消息: {result['message']}")
        
        else:
            print(f"❌ 请求导入失败: HTTP {response.status_code}")
            print(f"📝 错误响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保后端服务正在运行 (http://localhost:8000)")
    except requests.exceptions.Timeout:
        print("❌ 请求超时: 后端服务响应过慢")
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()


def test_system_status():
    """测试系统状态"""
    print("\n" + "="*60)
    print("📊 系统状态检查")
    print("="*60)
    
    try:
        # 健康检查
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"🏥 系统健康: {health['data']['status']}")
            print(f"⚙️ 调度器运行: {health['data']['scheduler_running']}")
            print(f"📈 运行任务数: {health['data']['running_tasks']}")
            print(f"🗄️ 数据库类型: {health['data']['database_type']}")
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
        
        # 配置信息
        response = requests.get("http://localhost:8000/config", timeout=5)
        if response.status_code == 200:
            config = response.json()
            print(f"⚙️ 应用配置: {config['data']['app']['name']} v{config['data']['app']['version']}")
            print(f"🗄️ 数据库: {config['data']['database']['type']}://{config['data']['database']['host']}:{config['data']['database']['port']}")
        else:
            print(f"❌ 配置获取失败: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保后端服务正在运行 (http://localhost:8000)")
        return False
    except Exception as e:
        print(f"❌ 系统状态检查失败: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🎯 RequestManager 测试脚本")
    print("="*60)
    
    # 测试系统状态
    if test_system_status():
        # 测试美团请求导入
        print("\n" + "="*60)
        print("🧪 美团请求导入测试")  
        print("="*60)
        test_import_meituan_request()
    else:
        print("❌ 系统状态检查失败，跳过功能测试")
    
    print("\n✅ 测试完成！")
    print("\n💡 提示：")
    print("  - 访问 http://localhost:8000/docs 查看完整API文档")
    print("  - 访问 http://localhost:8000/health 查看系统状态")
    print("  - 访问 http://localhost:8000/config 查看配置信息") 