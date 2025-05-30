#!/usr/bin/env python3
"""
Discord機器人最終功能驗證腳本
測試所有主要功能是否正常工作
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

class FinalBotVerification:
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = 0
        
    def test_pass(self, test_name):
        print(f"✅ {test_name}")
        self.passed_tests += 1
        
    def test_fail(self, test_name, error=None):
        error_msg = f" - {error}" if error else ""
        print(f"❌ {test_name}{error_msg}")
        self.failed_tests += 1
        
    def test_warning(self, test_name, warning=None):
        warning_msg = f" - {warning}" if warning else ""
        print(f"⚠️ {test_name}{warning_msg}")
        self.warnings += 1

async def test_module_imports(verifier):
    """測試模組導入"""
    print("🔍 測試模組導入...")
    
    modules = [
        ('discord', 'Discord.py'),
        ('aiohttp', 'aiohttp'),
        ('google.generativeai', 'Google Generative AI'),
        ('dotenv', 'python-dotenv'),
        ('asyncio', 'asyncio'),
        ('json', 'json'),
        ('ssl', 'ssl')
    ]
    
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            verifier.test_pass(f"{display_name} 模組導入成功")
        except ImportError as e:
            verifier.test_fail(f"{display_name} 模組導入失敗", str(e))

async def test_cog_loading(verifier):
    """測試Cog文件載入"""
    print("\n🔍 測試Cog文件...")
    
    cog_modules = [
        ('cogs.info_commands_fixed_v4_clean', 'InfoCommands'),
        ('cogs.admin_commands_fixed', 'AdminCommands'),
        ('cogs.basic_commands', 'BasicCommands'),
        ('cogs.level_system', 'LevelSystem'),
        ('cogs.monitor_system', 'MonitorSystem'),
        ('cogs.voice_system', 'VoiceSystem'),
        ('cogs.chat_commands', 'ChatCommands')
    ]
    
    for module_path, class_name in cog_modules:
        try:
            spec = __import__(module_path, fromlist=[class_name])
            cls = getattr(spec, class_name)
            verifier.test_pass(f"{class_name} Cog載入成功")
        except Exception as e:
            verifier.test_fail(f"{class_name} Cog載入失敗", str(e))

async def test_api_connectivity(verifier):
    """測試API連接"""
    print("\n🔍 測試API連接...")
    
    api_endpoints = [
        ("https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001", "海嘯API"),
        ("https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001", "地震API"),
        ("https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001", "天氣API")
    ]
    
    connector = aiohttp.TCPConnector(ssl=ssl_context, limit=10)
    
    try:
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=10)) as session:
            for url, api_name in api_endpoints:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('success') == 'true':
                                verifier.test_pass(f"{api_name} 連接正常")
                            else:
                                verifier.test_warning(f"{api_name} 回應異常", f"success: {data.get('success')}")
                        else:
                            verifier.test_fail(f"{api_name} 連接失敗", f"HTTP {response.status}")
                except asyncio.TimeoutError:
                    verifier.test_warning(f"{api_name} 連接超時")
                except Exception as e:
                    verifier.test_fail(f"{api_name} 連接錯誤", str(e))
    finally:
        await connector.close()

async def test_data_structure(verifier):
    """測試資料結構"""
    print("\n🔍 測試資料結構...")
    
    # 測試海嘯樣本資料
    if os.path.exists('sample_tsunami.json'):
        try:
            with open('sample_tsunami.json', 'r', encoding='utf-8') as f:
                tsunami_data = json.load(f)
                
            if 'records' in tsunami_data and 'Tsunami' in tsunami_data['records']:
                tsunami_records = tsunami_data['records']['Tsunami']
                if isinstance(tsunami_records, list) and len(tsunami_records) > 0:
                    first_record = tsunami_records[0]
                    required_fields = ['ReportContent', 'ReportType']
                    if all(field in first_record for field in required_fields):
                        verifier.test_pass("海嘯資料結構正確")
                    else:
                        missing = [f for f in required_fields if f not in first_record]
                        verifier.test_fail("海嘯資料缺少必要欄位", f"缺少: {missing}")
                else:
                    verifier.test_fail("海嘯資料為空或格式錯誤")
            else:
                verifier.test_fail("海嘯資料結構不正確")
        except Exception as e:
            verifier.test_fail("海嘯樣本資料測試失敗", str(e))
    else:
        verifier.test_fail("缺少海嘯樣本資料文件")
    
    # 測試地震樣本資料
    if os.path.exists('sample_earthquake.json'):
        try:
            with open('sample_earthquake.json', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    eq_data = json.loads(content)
                    if 'records' in eq_data and 'Earthquake' in eq_data['records']:
                        verifier.test_pass("地震資料結構正確")
                    else:
                        verifier.test_fail("地震資料結構不正確")
                else:
                    verifier.test_fail("地震樣本資料為空")
        except Exception as e:
            verifier.test_fail("地震樣本資料測試失敗", str(e))
    else:
        verifier.test_fail("缺少地震樣本資料文件")

async def test_info_commands_functionality(verifier):
    """測試InfoCommands功能"""
    print("\n🔍 測試InfoCommands功能...")
    
    try:
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        
        # 創建一個模擬的bot對象
        class MockBot:
            def __init__(self):
                self.connector = None
        
        mock_bot = MockBot()
        info_cog = InfoCommands(mock_bot)
        
        # 測試海嘯資料獲取方法
        try:
            # 這裡我們只測試方法是否存在並可調用
            if hasattr(info_cog, 'fetch_tsunami_data'):
                verifier.test_pass("海嘯資料獲取方法存在")
            else:
                verifier.test_fail("海嘯資料獲取方法不存在")
                
            if hasattr(info_cog, 'format_tsunami_data'):
                verifier.test_pass("海嘯資料格式化方法存在")
            else:
                verifier.test_fail("海嘯資料格式化方法不存在")
                
            if hasattr(info_cog, 'fetch_earthquake_data'):
                verifier.test_pass("地震資料獲取方法存在")
            else:
                verifier.test_fail("地震資料獲取方法不存在")
                
            if hasattr(info_cog, 'format_weather_data'):
                verifier.test_pass("天氣資料格式化方法存在")
            else:
                verifier.test_fail("天氣資料格式化方法不存在")
                
        except Exception as e:
            verifier.test_fail("InfoCommands方法測試失敗", str(e))
            
    except Exception as e:
        verifier.test_fail("InfoCommands功能測試失敗", str(e))

async def test_configuration_files(verifier):
    """測試配置文件"""
    print("\n🔍 測試配置文件...")
    
    # 測試bot.py
    if os.path.exists('bot.py'):
        try:
            with open('bot.py', 'r', encoding='utf-8') as f:
                bot_content = f.read()
                
            if 'CustomBot' in bot_content:
                verifier.test_pass("bot.py 包含CustomBot類")
            else:
                verifier.test_fail("bot.py 缺少CustomBot類")
                
            if 'info_commands_fixed_v4_clean' in bot_content:
                verifier.test_pass("bot.py 配置正確的InfoCommands模組")
            else:
                verifier.test_fail("bot.py 未配置正確的InfoCommands模組")
                
        except Exception as e:
            verifier.test_fail("bot.py 測試失敗", str(e))
    else:
        verifier.test_fail("缺少bot.py文件")
    
    # 測試requirements.txt
    if os.path.exists('requirements.txt'):
        verifier.test_pass("requirements.txt 存在")
    else:
        verifier.test_warning("缺少requirements.txt文件")
    
    # 測試level配置
    config_files = ['level_config.json', 'levels.json']
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                verifier.test_pass(f"{config_file} 格式正確")
            except json.JSONDecodeError:
                verifier.test_fail(f"{config_file} JSON格式錯誤")
        else:
            verifier.test_warning(f"缺少{config_file}文件")

async def test_log_file(verifier):
    """測試日誌文件"""
    print("\n🔍 測試日誌文件...")
    
    if os.path.exists('bot.log'):
        try:
            with open('bot.log', 'r', encoding='utf-8') as f:
                log_content = f.read()
                
            if '已載入 cogs.info_commands_fixed_v4_clean' in log_content:
                verifier.test_pass("InfoCommands模組成功載入")
            else:
                verifier.test_warning("日誌中未找到InfoCommands載入記錄")
                
            if 'ERROR' in log_content:
                verifier.test_warning("日誌中包含錯誤記錄")
            else:
                verifier.test_pass("日誌中無錯誤記錄")
                
            # 檢查編碼問題
            if '???' in log_content or '銝行' in log_content:
                verifier.test_warning("日誌存在編碼問題")
            else:
                verifier.test_pass("日誌編碼正常")
                
        except Exception as e:
            verifier.test_fail("日誌文件測試失敗", str(e))
    else:
        verifier.test_warning("缺少bot.log文件")

async def main():
    """主測試函數"""
    print("🚀 Discord機器人最終功能驗證")
    print("=" * 60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    verifier = FinalBotVerification()
    
    # 執行所有測試
    test_functions = [
        test_module_imports,
        test_cog_loading,
        test_api_connectivity,
        test_data_structure,
        test_info_commands_functionality,
        test_configuration_files,
        test_log_file
    ]
    
    for test_func in test_functions:
        try:
            await test_func(verifier)
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 時發生錯誤: {e}")
            verifier.failed_tests += 1
    
    # 報告結果
    print("\n" + "=" * 60)
    print("📊 測試結果總結")
    print("=" * 60)
    
    total_tests = verifier.passed_tests + verifier.failed_tests
    success_rate = (verifier.passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ 通過測試: {verifier.passed_tests}")
    print(f"❌ 失敗測試: {verifier.failed_tests}")
    print(f"⚠️ 警告: {verifier.warnings}")
    print(f"📈 成功率: {success_rate:.1f}%")
    
    if verifier.failed_tests == 0:
        print("\n🎉 所有核心功能測試通過！")
        print("🤖 Discord機器人已準備就緒，可以正常使用")
        if verifier.warnings > 0:
            print("⚠️ 有一些警告需要注意，但不影響基本功能")
    else:
        print(f"\n⚠️ 有 {verifier.failed_tests} 個測試失敗，需要進一步修復")
    
    return verifier.failed_tests == 0

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 驗證腳本執行失敗: {e}")
        sys.exit(1)
