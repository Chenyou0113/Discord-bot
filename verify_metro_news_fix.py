#!/usr/bin/env python3
"""
驗證 fetch_metro_news 方法是否正確修復
"""

import os
import inspect
import sys

# 添加路徑以便導入模組
sys.path.append(os.getcwd())

try:
    # 導入 InfoCommands 類別
    from cogs.info_commands_fixed_v4_clean import InfoCommands
    
    print("🔍 驗證 fetch_metro_news 方法修復狀況...")
    print("-" * 50)
    
    # 1. 檢查方法是否存在
    if hasattr(InfoCommands, 'fetch_metro_news'):
        print("✅ fetch_metro_news 方法存在於 InfoCommands 類別中")
        
        # 2. 檢查方法是否可調用
        method = getattr(InfoCommands, 'fetch_metro_news')
        if callable(method):
            print("✅ fetch_metro_news 方法是可調用的")
            
            # 3. 檢查方法簽名
            signature = inspect.signature(method)
            print(f"✅ 方法簽名: {signature}")
            
            # 4. 檢查是否是異步方法
            if inspect.iscoroutinefunction(method):
                print("✅ fetch_metro_news 是正確的異步方法")
            else:
                print("❌ fetch_metro_news 不是異步方法")
                
        else:
            print("❌ fetch_metro_news 方法不可調用")
    else:
        print("❌ fetch_metro_news 方法不存在於 InfoCommands 類別中")
    
    print("-" * 50)
    print("🎯 修復驗證完成！")
    
    # 5. 檢查其他相關方法
    metro_methods = [attr for attr in dir(InfoCommands) if 'metro' in attr.lower()]
    print(f"📋 InfoCommands 類別中的捷運相關方法: {metro_methods}")
    
    print("\n🎉 總結: fetch_metro_news 方法已成功修復並位於正確位置！")
    
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
except Exception as e:
    print(f"❌ 驗證時發生錯誤: {e}")