#!/usr/bin/env python3
"""
Discord機器人最終功能驗證腳本 (簡化版)
"""
import asyncio
import aiohttp
import json
import sys
import os
import ssl
from datetime import datetime

# 設定SSL上下文
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

class SimpleVerifier:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        
    def pass_test(self, name):
        print(f"[PASS] {name}")
        self.passed += 1
        
    def fail_test(self, name, error=None):
        msg = f"[FAIL] {name}"
        if error:
            msg += f" - {error}"
        print(msg)
        self.failed += 1
        
    def warn_test(self, name, warning=None):
        msg = f"[WARN] {name}"
        if warning:
            msg += f" - {warning}"
        print(msg)
        self.warnings += 1

async def verify_modules(v):
    """驗證模組導入"""
    print("\n=== 模組導入測試 ===")
    
    modules = [
        'discord', 'aiohttp', 'google.generativeai', 
        'dotenv', 'asyncio', 'json', 'ssl'
    ]
    
    for module in modules:
        try:
            __import__(module)
            v.pass_test(f"{module} 模組")
        except ImportError as e:
            v.fail_test(f"{module} 模組", str(e))

async def verify_cogs(v):
    """驗證Cog文件"""
    print("\n=== Cog文件測試 ===")
    
    cogs = [
        ('cogs.info_commands_fixed_v4_clean', 'InfoCommands'),
        ('cogs.admin_commands_fixed', 'AdminCommands'),
        ('cogs.basic_commands', 'BasicCommands'),
        ('cogs.level_system', 'LevelSystem'),
        ('cogs.monitor_system', 'MonitorSystem'),
        ('cogs.voice_system', 'VoiceSystem'),
        ('cogs.chat_commands', 'ChatCommands')
    ]
    
    for module_path, class_name in cogs:
        try:
            spec = __import__(module_path, fromlist=[class_name])
            cls = getattr(spec, class_name)
            v.pass_test(f"{class_name} Cog")
        except Exception as e:
            v.fail_test(f"{class_name} Cog", str(e))

async def verify_apis(v):
    """驗證API連接"""
    print("\n=== API連接測試 ===")
    
    apis = [
        ("https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001", "海嘯API"),
        ("https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001", "地震API"),
        ("https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001", "天氣API")
    ]
    
    connector = aiohttp.TCPConnector(ssl=ssl_context, limit=10)
    
    try:
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=8)) as session:
            for url, name in apis:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('success') == 'true':
                                v.pass_test(f"{name} 連接")
                            else:
                                v.warn_test(f"{name} 回應", f"success: {data.get('success')}")
                        else:
                            v.fail_test(f"{name} 連接", f"HTTP {response.status}")
                except asyncio.TimeoutError:
                    v.warn_test(f"{name} 連接", "超時")
                except Exception as e:
                    v.fail_test(f"{name} 連接", str(e))
    finally:
        await connector.close()

async def verify_data_files(v):
    """驗證資料文件"""
    print("\n=== 資料文件測試 ===")
    
    # 海嘯資料
    if os.path.exists('sample_tsunami.json'):
        try:
            with open('sample_tsunami.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'records' in data and 'Tsunami' in data['records']:
                v.pass_test("海嘯樣本資料結構")
            else:
                v.fail_test("海嘯樣本資料結構")
        except Exception as e:
            v.fail_test("海嘯樣本資料", str(e))
    else:
        v.fail_test("海嘯樣本資料", "文件不存在")
    
    # 地震資料
    if os.path.exists('sample_earthquake.json'):
        try:
            with open('sample_earthquake.json', 'r', encoding='utf-8') as f:
                content = f.read().strip()
            if content:
                data = json.loads(content)
                if 'records' in data and 'Earthquake' in data['records']:
                    v.pass_test("地震樣本資料結構")
                else:
                    v.fail_test("地震樣本資料結構")
            else:
                v.fail_test("地震樣本資料", "文件為空")
        except Exception as e:
            v.fail_test("地震樣本資料", str(e))
    else:
        v.fail_test("地震樣本資料", "文件不存在")

async def verify_bot_config(v):
    """驗證機器人配置"""
    print("\n=== 機器人配置測試 ===")
    
    # bot.py
    if os.path.exists('bot.py'):
        try:
            with open('bot.py', 'r', encoding='utf-8') as f:
                content = f.read()
            if 'info_commands_fixed_v4_clean' in content:
                v.pass_test("bot.py 配置正確")
            else:
                v.fail_test("bot.py 配置", "未使用正確的InfoCommands模組")
        except Exception as e:
            v.fail_test("bot.py 配置", str(e))
    else:
        v.fail_test("bot.py", "文件不存在")
    
    # 環境變數文件
    if os.path.exists('.env'):
        v.pass_test(".env 文件存在")
    else:
        v.warn_test(".env 文件", "不存在")

async def verify_info_commands(v):
    """驗證InfoCommands功能"""
    print("\n=== InfoCommands功能測試 ===")
    
    try:
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        
        class MockBot:
            def __init__(self):
                self.connector = None
        
        info_cog = InfoCommands(MockBot())
        
        methods = [
            'fetch_tsunami_data',
            'format_tsunami_data', 
            'fetch_earthquake_data',
            'format_weather_data'
        ]
        
        for method_name in methods:
            if hasattr(info_cog, method_name):
                v.pass_test(f"InfoCommands.{method_name} 方法")
            else:
                v.fail_test(f"InfoCommands.{method_name} 方法", "方法不存在")
                
    except Exception as e:
        v.fail_test("InfoCommands功能", str(e))

async def main():
    """主函數"""
    print("Discord機器人最終功能驗證")
    print("=" * 50)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    v = SimpleVerifier()
    
    # 執行測試
    tests = [
        verify_modules,
        verify_cogs,
        verify_apis,
        verify_data_files,
        verify_bot_config,
        verify_info_commands
    ]
    
    for test in tests:
        try:
            await test(v)
        except Exception as e:
            v.fail_test(f"測試 {test.__name__}", str(e))
    
    # 結果
    print("\n" + "=" * 50)
    print("測試結果")
    print("=" * 50)
    
    total = v.passed + v.failed
    success_rate = (v.passed / total * 100) if total > 0 else 0
    
    print(f"通過: {v.passed}")
    print(f"失敗: {v.failed}")
    print(f"警告: {v.warnings}")
    print(f"成功率: {success_rate:.1f}%")
    
    if v.failed == 0:
        print("\n所有核心功能測試通過!")
        print("Discord機器人已準備就緒")
    else:
        print(f"\n有 {v.failed} 個測試失敗，需要修復")
    
    return v.failed == 0

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"驗證失敗: {e}")
        sys.exit(1)
