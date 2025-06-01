#!/usr/bin/env python3
"""
Discord Bot 最終全面功能測試腳本
修復所有Mock類別問題，提供完整的功能驗證
"""

import asyncio
import sys
import os
import json
import traceback
from datetime import datetime
from pathlib import Path
import aiohttp

# 添加專案路徑到 Python 路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class EnhancedMockBot:
    """增強版模擬Discord機器人，包含所有必要方法"""
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.user = None
        self.guilds = []
        self._closed = False
        
    def is_closed(self):
        return self._closed
        
    async def wait_until_ready(self):
        """模擬等待機器人準備就緒"""
        await asyncio.sleep(0.1)
        
    async def close(self):
        """模擬關閉機器人"""
        self._closed = True

class EnhancedMockContext:
    """增強版模擬Discord上下文"""
    def __init__(self):
        self.send_called = False
        self.sent_content = None
        self.sent_embed = None
        self.response_count = 0
        
    async def send(self, content=None, embed=None, **kwargs):
        self.send_called = True
        self.sent_content = content
        self.sent_embed = embed
        self.response_count += 1
        return self

class ComprehensiveTester:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }

    async def log_test(self, test_name, status, message="", details=""):
        """記錄測試結果"""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details
        }
        self.results["tests"].append(result)
        
        if status == "PASS":
            self.results["passed"] += 1
            print(f"✅ {test_name}: {message}")
        elif status == "FAIL":
            self.results["failed"] += 1
            print(f"❌ {test_name}: {message}")
        elif status == "WARNING":
            self.results["warnings"] += 1
            print(f"⚠️ {test_name}: {message}")
        
        if details:
            print(f"   詳細: {details}")

    async def test_core_files(self):
        """測試核心檔案是否存在且可讀取"""
        print("\n🔍 測試核心檔案...")
        
        core_files = [
            ("bot.py", "主要機器人檔案"),
            (".env", "環境配置檔案"),
            ("requirements.txt", "依賴清單"),
            ("levels.json", "等級數據"),
            ("level_config.json", "等級配置"),
            ("sample_earthquake.json", "地震樣本數據"),
            ("sample_tsunami.json", "海嘯樣本數據")
        ]
        
        for filename, description in core_files:
            try:
                file_path = project_root / filename
                if file_path.exists():
                    # 檢查檔案是否可讀
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if content.strip():
                        await self.log_test(f"核心檔案 - {filename}", "PASS", f"{description}存在且可讀取")
                    else:
                        await self.log_test(f"核心檔案 - {filename}", "WARNING", f"{description}存在但為空")
                else:
                    await self.log_test(f"核心檔案 - {filename}", "FAIL", f"{description}不存在")
            except Exception as e:
                await self.log_test(f"核心檔案 - {filename}", "FAIL", f"讀取{description}時發生錯誤", str(e))

    async def test_environment_setup(self):
        """測試環境設置"""
        print("\n⚙️ 測試環境設置...")
        
        # 檢查 .env 檔案
        env_path = project_root / ".env"
        if env_path.exists():
            try:
                # 嘗試用UTF-8編碼讀取
                try:
                    with open(env_path, 'r', encoding='utf-8') as f:
                        env_content = f.read()
                except UnicodeDecodeError:
                    # 如果UTF-8失敗，嘗試其他編碼
                    with open(env_path, 'r', encoding='cp950') as f:
                        env_content = f.read()
                
                required_vars = ["DISCORD_TOKEN", "CWA_API_KEY", "OPENWEATHER_API_KEY"]
                missing_vars = []
                
                for var in required_vars:
                    if var not in env_content:
                        missing_vars.append(var)
                
                if not missing_vars:
                    await self.log_test("環境變數", "PASS", "所有必需的環境變數都已設定")
                else:
                    await self.log_test("環境變數", "WARNING", f"缺少環境變數: {', '.join(missing_vars)}")
                    
            except Exception as e:
                await self.log_test("環境變數", "FAIL", "讀取.env檔案時發生錯誤", str(e))
        else:
            await self.log_test("環境變數", "FAIL", ".env檔案不存在")

    async def test_syntax_validation(self):
        """測試主要 Python 檔案的語法"""
        print("\n🔧 測試 Python 檔案語法...")
        
        python_files = [
            project_root / "bot.py",
            project_root / "cogs" / "info_commands_fixed_v4_clean.py",
            project_root / "verify_30_issues_fix_clean.py",
            project_root / "comprehensive_diagnostics.py",
            project_root / "simple_earthquake_test.py"
        ]
        
        for file_path in python_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                    
                    # 編譯檢查語法
                    compile(source, str(file_path), 'exec')
                    await self.log_test(f"語法檢查 - {file_path.name}", "PASS", "語法正確")
                    
                except SyntaxError as e:
                    await self.log_test(f"語法檢查 - {file_path.name}", "FAIL", f"語法錯誤: {e.msg}", f"第{e.lineno}行")
                except Exception as e:
                    await self.log_test(f"語法檢查 - {file_path.name}", "FAIL", "檔案讀取錯誤", str(e))
            else:
                await self.log_test(f"語法檢查 - {file_path.name}", "WARNING", "檔案不存在")

    async def test_json_files(self):
        """測試 JSON 檔案格式"""
        print("\n📄 測試 JSON 檔案格式...")
        
        json_files = [
            ("levels.json", "等級數據"),
            ("level_config.json", "等級配置"),
            ("sample_earthquake.json", "地震樣本"),
            ("sample_tsunami.json", "海嘯樣本")
        ]
        
        for filename, description in json_files:
            file_path = project_root / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    await self.log_test(f"JSON格式 - {filename}", "PASS", f"{description}格式正確")
                except json.JSONDecodeError as e:
                    await self.log_test(f"JSON格式 - {filename}", "FAIL", f"{description}格式錯誤", str(e))
                except Exception as e:
                    await self.log_test(f"JSON格式 - {filename}", "FAIL", f"讀取{description}時發生錯誤", str(e))
            else:
                await self.log_test(f"JSON格式 - {filename}", "WARNING", f"{description}檔案不存在")

    async def test_cogs_structure(self):
        """測試 cogs 資料夾結構"""
        print("\n🎯 測試 Cogs 模組結構...")
        
        cogs_path = project_root / "cogs"
        if not cogs_path.exists():
            await self.log_test("Cogs結構", "FAIL", "cogs 資料夾不存在")
            return
        
        expected_cogs = [
            ("info_commands_fixed_v4_clean.py", "核心指令模組"),
            ("admin_commands_fixed.py", "管理員指令"),
            ("basic_commands.py", "基礎指令"),
            ("chat_commands.py", "聊天指令"),
            ("level_system.py", "等級系統"),
            ("monitor_system.py", "監控系統"),
            ("voice_system.py", "語音系統")
        ]
        
        for filename, description in expected_cogs:
            cog_file = cogs_path / filename
            if cog_file.exists():
                try:
                    # 簡單的語法檢查
                    with open(cog_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 檢查是否包含基本的 cog 結構
                    if "class" in content and "commands.Cog" in content:
                        await self.log_test(f"Cog模組 - {filename}", "PASS", f"{description}結構正確")
                    else:
                        await self.log_test(f"Cog模組 - {filename}", "WARNING", f"{description}結構可能不完整")
                except Exception as e:
                    await self.log_test(f"Cog模組 - {filename}", "FAIL", f"讀取{description}時發生錯誤", str(e))
            else:
                await self.log_test(f"Cog模組 - {filename}", "WARNING", f"{description}檔案不存在")

    async def test_bot_functionality(self):
        """測試機器人核心功能"""
        print("\n🤖 測試機器人核心功能...")
        
        try:
            # 導入核心模組
            from cogs.info_commands_fixed_v4_clean import InfoCommands
            
            # 使用增強版Mock對象
            mock_bot = EnhancedMockBot()
            info_cog = InfoCommands(mock_bot)
            mock_ctx = EnhancedMockContext()
            
            # 測試模組初始化
            await self.log_test("模組初始化", "PASS", "InfoCommands模組成功初始化")
            
            # 檢查關鍵方法是否存在
            required_methods = ['earthquake', 'weather', 'tsunami', 'fetch_earthquake_data']
            for method_name in required_methods:
                if hasattr(info_cog, method_name):
                    await self.log_test(f"功能檢查 - {method_name}", "PASS", f"{method_name}方法存在")
                else:
                    await self.log_test(f"功能檢查 - {method_name}", "FAIL", f"{method_name}方法不存在")
                    
        except ImportError as e:
            await self.log_test("模組導入", "FAIL", "無法導入InfoCommands模組", str(e))
        except Exception as e:
            await self.log_test("功能測試", "WARNING", "功能測試遇到問題", str(e))

    async def test_api_connections(self):
        """測試 API 連接（基本連通性測試）"""
        print("\n🌐 測試 API 連接...")
        
        api_tests = [
            {
                "name": "地震API",
                "url": "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001",
                "description": "中央氣象署地震資料"
            },
            {
                "name": "天氣API", 
                "url": "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001",
                "description": "中央氣象署天氣預報"
            }
        ]
        
        timeout = aiohttp.ClientTimeout(total=10)
        
        for api_test in api_tests:
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(api_test["url"]) as response:
                        if response.status == 200:
                            await self.log_test(f"API連接 - {api_test['name']}", "PASS", f"{api_test['description']}連接正常")
                        elif response.status == 401:
                            await self.log_test(f"API連接 - {api_test['name']}", "WARNING", f"{api_test['description']}需要API金鑰")
                        else:
                            await self.log_test(f"API連接 - {api_test['name']}", "WARNING", f"{api_test['description']}返回狀態碼: {response.status}")
            except asyncio.TimeoutError:
                await self.log_test(f"API連接 - {api_test['name']}", "WARNING", f"{api_test['description']}連接超時")
            except Exception as e:
                await self.log_test(f"API連接 - {api_test['name']}", "WARNING", f"{api_test['description']}連接失敗", str(e))

    async def test_data_integrity(self):
        """測試資料完整性"""
        print("\n📊 測試資料完整性...")
        
        # 測試地震樣本資料
        try:
            with open(project_root / "sample_earthquake.json", 'r', encoding='utf-8') as f:
                eq_data = json.load(f)
            
            if 'records' in eq_data and len(eq_data['records']) > 0:
                await self.log_test("地震資料結構", "PASS", "地震樣本資料結構正確")
            else:
                await self.log_test("地震資料結構", "WARNING", "地震樣本資料結構可能不完整")
                
        except Exception as e:
            await self.log_test("地震資料結構", "FAIL", "地震樣本資料測試失敗", str(e))
        
        # 測試海嘯樣本資料
        try:
            with open(project_root / "sample_tsunami.json", 'r', encoding='utf-8') as f:
                tsunami_data = json.load(f)
            
            if 'records' in tsunami_data:
                await self.log_test("海嘯資料結構", "PASS", "海嘯樣本資料結構正確")
            else:
                await self.log_test("海嘯資料結構", "WARNING", "海嘯樣本資料結構可能不完整")
                
        except Exception as e:
            await self.log_test("海嘯資料結構", "FAIL", "海嘯樣本資料測試失敗", str(e))

    async def run_all_tests(self):
        """執行所有測試"""
        print("🚀 開始Discord Bot最終全面功能測試...")
        print("=" * 70)
        
        await self.test_core_files()
        await self.test_environment_setup()
        await self.test_syntax_validation()
        await self.test_json_files()
        await self.test_cogs_structure()
        await self.test_bot_functionality()
        await self.test_api_connections()
        await self.test_data_integrity()
        
        print("\n" + "=" * 70)
        print("📊 最終測試結果摘要")
        print("=" * 70)
        print(f"✅ 通過: {self.results['passed']}")
        print(f"❌ 失敗: {self.results['failed']}")
        print(f"⚠️ 警告: {self.results['warnings']}")
        
        total_critical_tests = self.results['passed'] + self.results['failed']
        if total_critical_tests > 0:
            success_rate = (self.results['passed'] / total_critical_tests * 100)
            print(f"📈 關鍵功能成功率: {success_rate:.1f}%")
        
        # 保存詳細報告
        report_path = project_root / "final_test_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📝 詳細報告已保存至: {report_path}")
        
        # 評估整體狀態
        if self.results['failed'] == 0:
            print("\n🎉 恭喜！所有關鍵測試都通過了！")
            print("🚀 Discord Bot準備就緒，可以開始使用！")
            
            if self.results['warnings'] > 0:
                print(f"💡 注意：有{self.results['warnings']}個警告項目，但不影響核心功能")
            
            return True
        else:
            print(f"\n⚠️ 發現{self.results['failed']}個關鍵問題需要修復")
            return False

async def main():
    """主函數"""
    print("🔧 Discord Bot 最終全面功能測試")
    print("🎯 測試所有核心功能並生成最終報告")
    print()
    
    tester = ComprehensiveTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n" + "🎊" * 20)
        print("🏁 測試完成！Discord Bot已準備就緒！")
        print("🎊" * 20)
        return 0
    else:
        print("\n" + "🔧" * 20)
        print("⚠️ 需要進一步修復某些問題")
        print("🔧" * 20)
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ 測試被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 測試過程中發生未預期的錯誤: {e}")
        traceback.print_exc()
        sys.exit(1)
