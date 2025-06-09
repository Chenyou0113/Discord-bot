#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動搜尋功能驗證腳本
確保所有功能都正常工作
"""

import os
import sys
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoSearchVerification:
    def __init__(self):
        self.results = {
            'environment': False,
            'module_import': False,
            'bot_creation': False,
            'cog_loading': False,
            'keyword_detection': False,
            'query_extraction': False,
            'permission_check': False,
            'overall': False
        }
    
    async def check_environment(self):
        """檢查環境變數"""
        print("🔍 檢查環境變數...")
        
        required_vars = [
            'DISCORD_TOKEN',
            'GOOGLE_API_KEY', 
            'GOOGLE_SEARCH_API_KEY',
            'GOOGLE_SEARCH_ENGINE_ID'
        ]
        
        all_set = True
        for var in required_vars:
            if os.getenv(var):
                print(f"  ✅ {var}: 已設定")
            else:
                print(f"  ❌ {var}: 未設定")
                all_set = False
        
        self.results['environment'] = all_set
        return all_set
    
    async def check_module_import(self):
        """檢查模組導入"""
        print("\n📦 檢查模組導入...")
        
        try:
            from cogs.search_commands import SearchCommands
            print("  ✅ SearchCommands 模組導入成功")
            self.results['module_import'] = True
            return True
        except Exception as e:
            print(f"  ❌ 模組導入失敗: {e}")
            return False
    
    async def check_bot_creation(self):
        """檢查 Bot 創建"""
        print("\n🤖 檢查 Bot 創建...")
        
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            bot = commands.Bot(command_prefix='!', intents=intents)
            print("  ✅ Bot 創建成功")
            print(f"  ✅ Message Content Intent: {intents.message_content}")
            self.results['bot_creation'] = True
            return bot
        except Exception as e:
            print(f"  ❌ Bot 創建失敗: {e}")
            return None
    
    async def check_cog_loading(self, bot):
        """檢查 Cog 載入"""
        print("\n⚙️ 檢查 Cog 載入...")
        
        try:
            from cogs.search_commands import SearchCommands
            search_cog = SearchCommands(bot)
            print("  ✅ SearchCommands Cog 載入成功")
            print(f"  ✅ 預設觸發關鍵字: {search_cog.auto_search_keywords}")
            print(f"  ✅ 自動搜尋設定: {search_cog.auto_search_enabled}")
            self.results['cog_loading'] = True
            return search_cog
        except Exception as e:
            print(f"  ❌ Cog 載入失敗: {e}")
            return None
    
    async def check_keyword_detection(self, search_cog):
        """檢查關鍵字檢測"""
        print("\n🔑 檢查關鍵字檢測...")
        
        test_messages = [
            ("搜尋 Python 教學", True),
            ("我想搜索 Discord Bot", True), 
            ("幫我查找資料", True),
            ("今天天氣真好", False),
            ("普通訊息", False),
        ]
        
        all_correct = True
        for message, should_trigger in test_messages:
            detected = any(keyword in message for keyword in search_cog.auto_search_keywords)
            if detected == should_trigger:
                status = "✅"
            else:
                status = "❌"
                all_correct = False
            
            print(f"  {status} '{message}' -> {'會觸發' if detected else '不會觸發'}")
        
        self.results['keyword_detection'] = all_correct
        return all_correct
    
    async def check_query_extraction(self, search_cog):
        """檢查查詢提取"""
        print("\n🎯 檢查查詢提取...")
        
        test_cases = [
            ("搜尋 Python 程式設計", "Python 程式設計"),
            ("我想搜索 Discord Bot 開發", "Discord Bot 開發"),
            ("查找機器學習資料", "機器學習資料"),
        ]
        
        all_correct = True
        for content, expected in test_cases:
            try:
                # 模擬查詢提取邏輯
                query = ""
                for keyword in search_cog.auto_search_keywords:
                    if keyword in content:
                        parts = content.split(keyword, 1)
                        if len(parts) > 1:
                            potential_query = parts[1].strip()
                            if potential_query:
                                query = potential_query
                                break
                
                if not query:
                    # 嘗試替代方法
                    query = content
                    for keyword in search_cog.auto_search_keywords:
                        query = query.replace(keyword, "").strip()
                
                query = query.strip("，。！？；：\"'()（）[]【】{}").strip()
                
                if query.strip() == expected.strip():
                    print(f"  ✅ '{content}' -> '{query}'")
                else:
                    print(f"  ❌ '{content}' -> '{query}' (預期: '{expected}')")
                    all_correct = False
                    
            except Exception as e:
                print(f"  ❌ 查詢提取錯誤: {e}")
                all_correct = False
        
        self.results['query_extraction'] = all_correct
        return all_correct
    
    async def check_permission_functions(self, search_cog):
        """檢查權限檢查函數"""
        print("\n🛡️ 檢查權限檢查函數...")
        
        try:
            # 測試管理員檢查
            admin_check = hasattr(search_cog, '_is_admin')
            print(f"  ✅ 管理員檢查函數: {'存在' if admin_check else '不存在'}")
            
            # 測試冷卻檢查
            cooldown_check = hasattr(search_cog, '_check_cooldown')
            print(f"  ✅ 冷卻檢查函數: {'存在' if cooldown_check else '不存在'}")
            
            # 測試每日限制檢查
            daily_check = hasattr(search_cog, '_check_daily_limit')
            print(f"  ✅ 每日限制檢查函數: {'存在' if daily_check else '不存在'}")
            
            # 測試 on_message 監聽器
            listener_check = hasattr(search_cog, 'on_message')
            print(f"  ✅ 訊息監聽器: {'存在' if listener_check else '不存在'}")
            
            # 測試管理命令
            auto_search_cmd = hasattr(search_cog, 'auto_search_settings')
            print(f"  ✅ 自動搜尋設定命令: {'存在' if auto_search_cmd else '不存在'}")
            
            all_functions = all([admin_check, cooldown_check, daily_check, listener_check, auto_search_cmd])
            self.results['permission_check'] = all_functions
            return all_functions
            
        except Exception as e:
            print(f"  ❌ 權限檢查失敗: {e}")
            return False
    
    async def run_verification(self):
        """執行完整驗證"""
        print("🚀 Discord Bot 自動搜尋功能驗證")
        print("=" * 50)
        
        # 檢查環境
        if not await self.check_environment():
            print("\n❌ 環境變數檢查失敗")
            return False
        
        # 檢查模組
        if not await self.check_module_import():
            print("\n❌ 模組導入檢查失敗")
            return False
        
        # 創建 Bot
        bot = await self.check_bot_creation()
        if not bot:
            print("\n❌ Bot 創建檢查失敗")
            return False
        
        # 載入 Cog
        search_cog = await self.check_cog_loading(bot)
        if not search_cog:
            print("\n❌ Cog 載入檢查失敗")
            return False
        
        # 檢查關鍵字檢測
        if not await self.check_keyword_detection(search_cog):
            print("\n❌ 關鍵字檢測檢查失敗")
            return False
        
        # 檢查查詢提取
        if not await self.check_query_extraction(search_cog):
            print("\n❌ 查詢提取檢查失敗")
            return False
        
        # 檢查權限函數
        if not await self.check_permission_functions(search_cog):
            print("\n❌ 權限函數檢查失敗")
            return False
        
        self.results['overall'] = True
        return True
    
    def print_summary(self):
        """打印總結"""
        print("\n" + "=" * 50)
        print("📊 驗證結果總結")
        print("=" * 50)
        
        for test, result in self.results.items():
            if test == 'overall':
                continue
            status = "✅ 通過" if result else "❌ 失敗"
            test_name = {
                'environment': '環境變數檢查',
                'module_import': '模組導入檢查', 
                'bot_creation': 'Bot 創建檢查',
                'cog_loading': 'Cog 載入檢查',
                'keyword_detection': '關鍵字檢測檢查',
                'query_extraction': '查詢提取檢查', 
                'permission_check': '權限函數檢查'
            }.get(test, test)
            
            print(f"{status} {test_name}")
        
        if self.results['overall']:
            print("\n🎉 所有檢查通過！自動搜尋功能準備就緒")
            print("\n📋 下一步驟:")
            print("1. 重啟 Discord Bot")
            print("2. 在 Discord 伺服器中使用 /auto_search enable:True 啟用功能")
            print("3. 測試發送包含 '搜尋' 的訊息")
        else:
            print("\n❌ 部分檢查失敗，請修復問題後重新測試")

async def main():
    verification = AutoSearchVerification()
    
    try:
        success = await verification.run_verification()
        verification.print_summary()
        return success
    except Exception as e:
        print(f"\n💥 驗證過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 驗證中斷")
        sys.exit(1)
