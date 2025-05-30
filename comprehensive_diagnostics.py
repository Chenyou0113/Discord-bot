#!/usr/bin/env python3
"""
Discord機器人問題診斷腳本
識別並報告所有潛在問題
"""
import asyncio
import json
import os
import sys
import logging
import importlib.util
from pathlib import Path

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotDiagnostics:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.suggestions = []
        
    def add_issue(self, category, description, severity="ERROR"):
        self.issues.append({
            "category": category,
            "description": description,
            "severity": severity
        })
        
    def add_warning(self, category, description):
        self.warnings.append({
            "category": category,
            "description": description
        })
        
    def add_suggestion(self, category, description):
        self.suggestions.append({
            "category": category,
            "description": description
        })

async def check_environment():
    """檢查環境配置"""
    diag = BotDiagnostics()
      # 檢查 .env 文件
    if not os.path.exists('.env'):
        diag.add_issue("ENV", "缺少 .env 文件")
    else:
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                env_content = f.read()
                if 'DISCORD_TOKEN' not in env_content:
                    diag.add_issue("ENV", "DISCORD_TOKEN 未在 .env 中設定")
                if 'GOOGLE_API_KEY' not in env_content:
                    diag.add_issue("ENV", "GOOGLE_API_KEY 未在 .env 中設定")
        except UnicodeDecodeError:
            try:
                with open('.env', 'r', encoding='cp950') as f:
                    env_content = f.read()
                    if 'DISCORD_TOKEN' not in env_content:
                        diag.add_issue("ENV", "DISCORD_TOKEN 未在 .env 中設定")
                    if 'GOOGLE_API_KEY' not in env_content:
                        diag.add_issue("ENV", "GOOGLE_API_KEY 未在 .env 中設定")
            except Exception as e:
                diag.add_warning("ENV", f"無法讀取 .env 文件: {e}")
                
    # 檢查必要文件
    required_files = [
        'bot.py',
        'requirements.txt',
        'cogs/info_commands_fixed_v4_clean.py',
        'cogs/admin_commands_fixed.py',
        'cogs/basic_commands.py',
        'cogs/level_system.py',
        'cogs/monitor_system.py',
        'cogs/voice_system.py',
        'cogs/chat_commands.py'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            diag.add_issue("FILES", f"缺少必要文件: {file_path}")
            
    return diag

async def check_module_imports():
    """檢查模組導入"""
    diag = BotDiagnostics()
    
    modules_to_test = [
        ('discord', 'Discord.py'),
        ('aiohttp', 'aiohttp'),
        ('google.generativeai', 'Google Generative AI'),
        ('dotenv', 'python-dotenv')
    ]
    
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
        except ImportError:
            diag.add_issue("IMPORTS", f"缺少必要模組: {display_name}")
            
    return diag

async def check_cog_files():
    """檢查 Cog 文件"""
    diag = BotDiagnostics()
    
    cog_files = [
        'cogs/admin_commands_fixed.py',
        'cogs/basic_commands.py',
        'cogs/chat_commands.py',
        'cogs/info_commands_fixed_v4_clean.py',
        'cogs/level_system.py',
        'cogs/monitor_system.py',
        'cogs/voice_system.py'
    ]
    
    for cog_file in cog_files:
        if os.path.exists(cog_file):
            try:
                # 嘗試編譯文件檢查語法
                with open(cog_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    compile(content, cog_file, 'exec')
            except SyntaxError as e:
                diag.add_issue("SYNTAX", f"{cog_file} 語法錯誤: {e}")
            except Exception as e:
                diag.add_warning("SYNTAX", f"{cog_file} 可能有問題: {e}")
        else:
            diag.add_issue("FILES", f"Cog 文件不存在: {cog_file}")
            
    return diag

async def check_api_data_structure():
    """檢查 API 資料結構"""
    diag = BotDiagnostics()
    
    # 檢查海嘯樣本資料
    if os.path.exists('sample_tsunami.json'):
        try:
            with open('sample_tsunami.json', 'r', encoding='utf-8') as f:
                tsunami_data = json.load(f)
                
            if 'records' not in tsunami_data:
                diag.add_issue("DATA", "海嘯樣本資料缺少 'records' 欄位")
            elif 'Tsunami' not in tsunami_data['records']:
                diag.add_issue("DATA", "海嘯樣本資料 records 中缺少 'Tsunami' 欄位")
            else:
                tsunami_records = tsunami_data['records']['Tsunami']
                if not isinstance(tsunami_records, list) or len(tsunami_records) == 0:
                    diag.add_warning("DATA", "海嘯樣本資料為空或格式不正確")
                else:
                    # 檢查必要欄位
                    first_record = tsunami_records[0]
                    required_fields = ['ReportContent', 'ReportType']
                    for field in required_fields:
                        if field not in first_record:
                            diag.add_warning("DATA", f"海嘯資料缺少欄位: {field}")
                            
        except json.JSONDecodeError:
            diag.add_issue("DATA", "sample_tsunami.json 格式錯誤")
        except Exception as e:
            diag.add_warning("DATA", f"讀取海嘯樣本資料時發生錯誤: {e}")
    else:
        diag.add_warning("DATA", "缺少 sample_tsunami.json 文件")
        
    # 檢查地震樣本資料
    if os.path.exists('sample_earthquake.json'):
        try:
            with open('sample_earthquake.json', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    diag.add_warning("DATA", "sample_earthquake.json 文件為空")
                else:
                    earthquake_data = json.loads(content)
                    # 進行基本結構檢查
                    
        except json.JSONDecodeError:
            diag.add_warning("DATA", "sample_earthquake.json 格式錯誤")
        except Exception as e:
            diag.add_warning("DATA", f"讀取地震樣本資料時發生錯誤: {e}")
    else:
        diag.add_warning("DATA", "缺少 sample_earthquake.json 文件")
        
    return diag

async def check_logging_issues():
    """檢查日誌問題"""
    diag = BotDiagnostics()
    
    if os.path.exists('bot.log'):
        try:
            with open('bot.log', 'r', encoding='utf-8') as f:
                log_content = f.read()
                
            # 檢查常見錯誤模式
            error_patterns = [
                'ERROR',
                'Exception',
                'Traceback',
                'Failed',
                'ConnectionError',
                'TimeoutError'
            ]
            
            for pattern in error_patterns:
                if pattern in log_content:
                    diag.add_warning("LOGGING", f"日誌中發現 {pattern}")
                    
            # 檢查編碼問題
            if '???' in log_content or '銝行' in log_content:
                diag.add_issue("LOGGING", "日誌存在中文字符編碼問題")
                
        except Exception as e:
            diag.add_warning("LOGGING", f"讀取日誌文件時發生錯誤: {e}")
    else:
        diag.add_warning("LOGGING", "缺少 bot.log 文件")
        
    return diag

async def check_discord_permissions():
    """檢查 Discord 權限設定"""
    diag = BotDiagnostics()
    
    # 檢查 bot.py 中的權限設定
    if os.path.exists('bot.py'):
        try:
            with open('bot.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
            required_permissions = [
                'send_messages',
                'read_messages',
                'embed_links',
                'use_application_commands'
            ]
            
            for perm in required_permissions:
                if perm not in content:
                    diag.add_warning("PERMISSIONS", f"可能缺少權限設定: {perm}")
                    
        except Exception as e:
            diag.add_warning("PERMISSIONS", f"檢查權限設定時發生錯誤: {e}")
            
    return diag

async def check_command_synchronization():
    """檢查命令同步問題"""
    diag = BotDiagnostics()
    
    # 檢查是否有命令同步相關的函數
    if os.path.exists('bot.py'):
        try:
            with open('bot.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 檢查是否有同步命令的邏輯
            if 'tree.sync' not in content:
                diag.add_warning("COMMANDS", "可能缺少命令同步邏輯")
                
            # 檢查是否有重複的命令定義
            command_count = content.count('@app_commands.command')
            if command_count == 0:
                diag.add_warning("COMMANDS", "bot.py 中沒有找到應用程式命令")
                
        except Exception as e:
            diag.add_warning("COMMANDS", f"檢查命令同步時發生錯誤: {e}")
            
    return diag

async def main():
    """主診斷函數"""
    print("🔍 開始 Discord 機器人問題診斷...")
    print("=" * 60)
    
    # 執行所有檢查
    checks = [
        ("環境配置", check_environment),
        ("模組導入", check_module_imports),
        ("Cog 文件", check_cog_files),
        ("API 資料結構", check_api_data_structure),
        ("日誌問題", check_logging_issues),
        ("Discord 權限", check_discord_permissions),
        ("命令同步", check_command_synchronization)
    ]
    
    all_issues = []
    all_warnings = []
    all_suggestions = []
    
    for check_name, check_func in checks:
        print(f"🔎 檢查 {check_name}...")
        try:
            result = await check_func()
            all_issues.extend(result.issues)
            all_warnings.extend(result.warnings)
            all_suggestions.extend(result.suggestions)
        except Exception as e:
            print(f"❌ 檢查 {check_name} 時發生錯誤: {e}")
    
    # 報告結果
    print("=" * 60)
    print("📋 診斷結果")
    print("=" * 60)
    
    if all_issues:
        print(f"\n❌ 發現 {len(all_issues)} 個問題:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i:2d}. [{issue['category']}] {issue['description']} ({issue['severity']})")
    
    if all_warnings:
        print(f"\n⚠️ 發現 {len(all_warnings)} 個警告:")
        for i, warning in enumerate(all_warnings, 1):
            print(f"{i:2d}. [{warning['category']}] {warning['description']}")
    
    if all_suggestions:
        print(f"\n💡 建議:")
        for i, suggestion in enumerate(all_suggestions, 1):
            print(f"{i:2d}. [{suggestion['category']}] {suggestion['description']}")
    
    if not all_issues and not all_warnings:
        print("\n✅ 沒有發現明顯問題！機器人應該運行正常。")
    else:
        print(f"\n📊 總計: {len(all_issues)} 個問題, {len(all_warnings)} 個警告")
        
    return len(all_issues), len(all_warnings)

if __name__ == "__main__":
    try:
        issues, warnings = asyncio.run(main())
        if issues > 0:
            print(f"\n🚨 需要修復 {issues} 個問題")
            sys.exit(1)
        elif warnings > 0:
            print(f"\n⚠️ 有 {warnings} 個警告需要注意")
            sys.exit(0)
        else:
            print("\n🎉 所有檢查通過！")
            sys.exit(0)
    except Exception as e:
        print(f"❌ 診斷腳本執行失敗: {e}")
        sys.exit(1)
