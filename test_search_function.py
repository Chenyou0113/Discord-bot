#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
搜尋功能測試腳本
測試搜尋功能的各個組件是否正常工作
"""

import os
import sys
import asyncio
import aiohttp
from dotenv import load_dotenv
import google.generativeai as genai

# 載入環境變數
load_dotenv()

def test_environment_variables():
    """測試環境變數配置"""
    print("=== 測試環境變數配置 ===")
    
    # 檢查必需的環境變數
    vars_to_check = [
        'DISCORD_TOKEN',
        'GOOGLE_API_KEY',
        'GOOGLE_SEARCH_API_KEY', 
        'GOOGLE_SEARCH_ENGINE_ID'
    ]
    
    all_good = True
    for var in vars_to_check:
        value = os.getenv(var)
        if value and value.strip():
            if 'TOKEN' in var or 'KEY' in var:
                masked = value[:8] + '*' * (len(value) - 12) + value[-4:] if len(value) > 12 else '***'
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 未設定或為空")
            all_good = False
    
    return all_good

async def test_google_search():
    """測試Google搜尋API"""
    print("\n=== 測試Google搜尋API ===")
    
    api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
    engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
    
    if not api_key or not engine_id:
        print("❌ Google搜尋API配置不完整")
        return False
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": engine_id,
        "q": "test search",
        "num": 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'items' in data:
                        print("✅ Google搜尋API測試成功")
                        print(f"   找到 {len(data['items'])} 個結果")
                        return True
                    else:
                        print("⚠️ API回應正常但無搜尋結果")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Google搜尋API測試失敗: HTTP {response.status}")
                    print(f"   錯誤詳情: {error_text[:200]}...")
                    return False
    except Exception as e:
        print(f"❌ Google搜尋API測試錯誤: {str(e)}")
        return False

def test_gemini_ai():
    """測試Gemini AI"""
    print("\n=== 測試Gemini AI ===")
    
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("❌ Gemini AI API金鑰未設定")
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # 測試簡單的文字生成
        response = model.generate_content("Hello, please respond with 'AI test successful'")
        
        if response and response.text:
            print("✅ Gemini AI測試成功")
            print(f"   回應: {response.text[:100]}...")
            return True
        else:
            print("❌ Gemini AI無回應")
            return False
            
    except Exception as e:
        print(f"❌ Gemini AI測試錯誤: {str(e)}")
        return False

def test_search_module_import():
    """測試搜尋模組導入"""
    print("\n=== 測試搜尋模組導入 ===")
    
    try:
        # 嘗試導入搜尋模組
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from cogs.search_commands import SearchCommands
        print("✅ 搜尋模組導入成功")
        
        # 檢查模組的主要方法
        methods_to_check = ['_google_search', '_generate_search_summary', '_format_search_results']
        for method in methods_to_check:
            if hasattr(SearchCommands, method):
                print(f"   ✅ {method} 方法存在")
            else:
                print(f"   ❌ {method} 方法不存在")
        
        return True
        
    except ImportError as e:
        print(f"❌ 搜尋模組導入失敗: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 搜尋模組測試錯誤: {str(e)}")
        return False

async def main():
    """主測試函數"""
    print("Discord Bot 搜尋功能測試")
    print("=" * 40)
    
    # 執行所有測試
    env_test = test_environment_variables()
    module_test = test_search_module_import()
    search_test = await test_google_search()
    ai_test = test_gemini_ai()
    
    # 總結結果
    print("\n" + "=" * 40)
    print("測試結果總結:")
    print(f"環境變數配置: {'✅ 通過' if env_test else '❌ 失敗'}")
    print(f"模組導入測試: {'✅ 通過' if module_test else '❌ 失敗'}")
    print(f"Google搜尋API: {'✅ 通過' if search_test else '❌ 失敗'}")
    print(f"Gemini AI: {'✅ 通過' if ai_test else '❌ 失敗'}")
    
    all_passed = env_test and module_test and search_test and ai_test
    
    if all_passed:
        print("\n🎉 所有測試通過！搜尋功能已準備就緒。")
        print("您可以啟動Discord Bot並使用 /search 指令了。")
    else:
        print("\n⚠️ 部分測試失敗，請檢查上述錯誤信息。")
    
    return all_passed

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n測試被用戶中斷")
    except Exception as e:
        print(f"\n測試過程中發生未預期的錯誤: {str(e)}")
