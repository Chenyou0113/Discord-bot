#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜尋功能設定驗證腳本
檢查 Google Search API 配置是否正確
"""

import os
import sys
import asyncio
import aiohttp
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

def check_environment_variables():
    """檢查環境變數配置"""
    print("=== 檢查環境變數配置 ===")
    
    # 必需的環境變數
    required_vars = {
        'DISCORD_TOKEN': '❌ Discord Bot Token 未設定',
        'GOOGLE_API_KEY': '❌ Google AI API Key 未設定', 
        'GOOGLE_SEARCH_API_KEY': '❌ Google Search API Key 未設定',
        'GOOGLE_SEARCH_ENGINE_ID': '❌ Google Search Engine ID 未設定'
    }
    
    all_configured = True
    
    for var, error_msg in required_vars.items():
        value = os.getenv(var)
        if not value or value.strip() == '' or 'your_' in value.lower():
            print(f"❌ {var}: {error_msg}")
            all_configured = False
        else:
            # 隱藏敏感資訊
            if 'TOKEN' in var or 'KEY' in var:
                masked_value = value[:8] + '*' * (len(value) - 12) + value[-4:] if len(value) > 12 else '***masked***'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    return all_configured

async def test_google_search_api():
    """測試 Google Search API 連線"""
    print("\n=== 測試 Google Search API ===")
    
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    if not api_key or not search_engine_id or 'your_' in api_key.lower():
        print("❌ Google Search API 配置不完整，跳過測試")
        return False
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': 'test search',
        'num': 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'items' in data:
                        print("✅ Google Search API 連線成功")
                        print(f"✅ 搜尋結果數量: {len(data.get('items', []))}")
                        return True
                    else:
                        print("⚠️ API 回應正常但無搜尋結果")
                        return False
                elif response.status == 403:
                    error_data = await response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    print(f"❌ API 權限錯誤 (403): {error_msg}")
                    if 'quota' in error_msg.lower():
                        print("💡 提示: 可能是 API 配額已耗盡")
                    elif 'key' in error_msg.lower():
                        print("💡 提示: API 金鑰可能無效或未啟用 Custom Search API")
                    return False
                else:
                    print(f"❌ API 請求失敗: HTTP {response.status}")
                    return False
                    
    except asyncio.TimeoutError:
        print("❌ API 請求超時")
        return False
    except Exception as e:
        print(f"❌ API 測試失敗: {str(e)}")
        return False

def check_file_structure():
    """檢查檔案結構"""
    print("\n=== 檢查檔案結構 ===")
    
    required_files = {
        'cogs/search_commands.py': '搜尋功能模組',
        'SEARCH_SETUP_GUIDE.md': '搜尋設定指南',
        '.env': '環境變數配置檔案',
        'bot.py': '主程式檔案'
    }
    
    all_files_exist = True
    
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} (檔案不存在)")
            all_files_exist = False
    
    return all_files_exist

def check_bot_configuration():
    """檢查 bot.py 配置"""
    print("\n=== 檢查 Bot 配置 ===")
    
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        # 檢查是否有搜尋模組
        if "'cogs.search_commands'" in bot_content or '"cogs.search_commands"' in bot_content:
            print("✅ 搜尋模組已添加到 bot.py")
            return True
        else:
            print("❌ 搜尋模組未添加到 bot.py 的 initial_extensions")
            print("💡 請確保 'cogs.search_commands' 在 initial_extensions 列表中")
            return False
            
    except FileNotFoundError:
        print("❌ 找不到 bot.py 檔案")
        return False
    except Exception as e:
        print(f"❌ 檢查 bot.py 時發生錯誤: {str(e)}")
        return False

async def main():
    """主要檢查函數"""
    print("🔍 Discord Bot 搜尋功能設定檢查")
    print("=" * 50)
    
    checks = []
    
    # 檢查環境變數
    checks.append(check_environment_variables())
    
    # 檢查檔案結構
    checks.append(check_file_structure())
    
    # 檢查 Bot 配置
    checks.append(check_bot_configuration())
    
    # 測試 Google Search API
    api_result = await test_google_search_api()
    checks.append(api_result)
    
    print("\n" + "=" * 50)
    print("📊 檢查結果摘要")
    print("=" * 50)
    
    passed_checks = sum(checks)
    total_checks = len(checks)
    
    if passed_checks == total_checks:
        print("🎉 所有檢查都通過！搜尋功能已準備就緒")
        print("\n📝 下一步操作:")
        print("1. 啟動 Discord Bot")
        print("2. 使用 /search 指令測試搜尋功能")
        print("3. 使用 /search_settings view 查看設定")
    else:
        print(f"⚠️ {total_checks - passed_checks} 個檢查失敗")
        print("\n🔧 修復建議:")
        
        if not checks[0]:  # 環境變數檢查
            print("• 請參考 SEARCH_SETUP_GUIDE.md 配置 Google Search API")
            print("• 確保 .env 檔案中的設定正確")
        
        if not checks[1]:  # 檔案結構檢查
            print("• 請確保所有必要檔案都存在")
        
        if not checks[2]:  # Bot 配置檢查
            print("• 請將 'cogs.search_commands' 添加到 bot.py 的 initial_extensions")
        
        if not checks[3]:  # API 測試
            print("• 檢查 Google Search API 金鑰和搜尋引擎 ID")
            print("• 確認 API 配額未耗盡")
            print("• 驗證 Custom Search API 已啟用")
    
    print(f"\n✅ 通過: {passed_checks}/{total_checks}")
    print(f"❌ 失敗: {total_checks - passed_checks}/{total_checks}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 檢查已中止")
    except Exception as e:
        print(f"\n💥 檢查過程中發生錯誤: {str(e)}")
        sys.exit(1)
