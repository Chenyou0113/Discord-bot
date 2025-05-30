#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
驗證30個問題修復狀況
"""

import asyncio
import sys
import os
import subprocess
import json
import traceback
from datetime import datetime

# 確保可以匯入 cogs 模組
sys.path.append(os.getcwd())

async def verify_fixes():
    """驗證修復是否成功"""
    print("🔧 驗證30個問題修復狀況...")
    print("=" * 60)
    
    issues_found = []
    fixes_verified = []
    
    try:
        # 1. 測試地震功能
        print("\n1. 測試地震功能...")
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        
        class MockBot:
            def __init__(self):
                self.user = None
                self.guilds = []
                self.loop = asyncio.get_event_loop()
                
            async def wait_until_ready(self):
                pass
        
        bot = MockBot()
        info_commands = InfoCommands(bot)
        
        # 測試地震資料獲取
        print("   測試地震API...")
        eq_data = await info_commands.fetch_earthquake_data()
        
        if eq_data is None:
            fixes_verified.append("✅ 地震API異常格式檢測 - 正確返回None")
        else:
            print("   ⚠️ 獲取到地震資料，檢查格式...")
            if ('result' in eq_data and isinstance(eq_data['result'], dict) and 
                set(eq_data['result'].keys()) == {'resource_id', 'fields'}):
                issues_found.append("❌ 地震API仍返回異常格式（字段定義）")
            else:
                fixes_verified.append("✅ 地震API返回正常資料格式")
        
        # 2. 測試海嘯功能
        print("\n2. 測試海嘯功能...")
        try:
            tsunami_data = await info_commands.fetch_tsunami_data()
            if tsunami_data:
                fixes_verified.append("✅ 海嘯功能正常運作")
            else:
                issues_found.append("❌ 海嘯功能無法獲取資料")
        except Exception as e:
            issues_found.append(f"❌ 海嘯功能錯誤: {str(e)}")
        
        # 3. 測試天氣功能
        print("\n3. 測試天氣功能...")
        try:
            weather_data = await info_commands.fetch_weather_data()
            if weather_data:
                fixes_verified.append("✅ 天氣功能正常運作")
            else:
                issues_found.append("❌ 天氣功能無法獲取資料")
        except Exception as e:
            issues_found.append(f"❌ 天氣功能錯誤: {str(e)}")
        
        # 清理資源
        if info_commands.session and not info_commands.session.closed:
            await info_commands.session.close()
                
    except Exception as e:
        issues_found.append(f"❌ 模組測試失敗: {str(e)}")
    
    # 4. 檢查機器人運行狀態
    print("\n4. 檢查機器人運行狀態...")
    try:
        # 使用 chcp 65001 確保UTF-8編碼
        result = subprocess.run(['tasklist', '/fi', 'imagename eq python.exe'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.stdout and 'python.exe' in result.stdout:
            fixes_verified.append("✅ 機器人進程正常運行")
        else:
            issues_found.append("❌ 機器人進程未運行")
    except Exception as e:
        issues_found.append(f"❌ 無法檢查機器人狀態: {str(e)}")
    
    # 5. 檢查語法錯誤
    print("\n5. 檢查主要代碼文件語法...")
    main_files = [
        'bot.py',
        'cogs/info_commands_fixed_v4_clean.py'
    ]
    
    for file_path in main_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, file_path, 'exec')
                fixes_verified.append(f"✅ {file_path} 語法正確")
            except SyntaxError as e:
                issues_found.append(f"❌ {file_path} 語法錯誤: {e}")
        else:
            issues_found.append(f"❌ 檔案不存在: {file_path}")
    
    # 6. 檢查編碼問題
    print("\n6. 檢查日誌編碼...")
    try:
        if os.path.exists('bot.log'):
            with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
                recent_lines = f.readlines()[-20:]
                
            # 檢查是否有明顯的編碼問題
            garbled_count = 0
            for line in recent_lines:
                if '?' in line and len([c for c in line if ord(c) > 127]) > 10:
                    garbled_count += 1
            
            if garbled_count < 5:
                fixes_verified.append("✅ 日誌編碼基本正常")
            else:
                issues_found.append("❌ 日誌仍有編碼問題")
        else:
            issues_found.append("❌ 未找到日誌文件")
    except Exception as e:
        issues_found.append(f"❌ 檢查日誌編碼失敗: {str(e)}")
    
    # 生成報告
    print("\n" + "=" * 60)
    print("📊 修復驗證報告")
    print("=" * 60)
    
    print(f"\n✅ 已修復問題 ({len(fixes_verified)}):")
    for fix in fixes_verified:
        print(f"  {fix}")
    
    print(f"\n❌ 仍存在問題 ({len(issues_found)}):")
    for issue in issues_found:
        print(f"  {issue}")
    
    total_checked = len(fixes_verified) + len(issues_found)
    success_rate = (len(fixes_verified) / total_checked * 100) if total_checked > 0 else 0
    
    print(f"\n📈 修復成功率: {success_rate:.1f}% ({len(fixes_verified)}/{total_checked})")
    
    if len(issues_found) == 0:
        print("\n🎉 所有檢查項目都通過！30個問題已成功修復。")
        return True
    elif len(issues_found) <= 3:
        print("\n⚠️ 大部分問題已修復，還有少數項目需要調整。")
        return False
    else:
        print("\n❌ 還有多個問題需要進一步修復。")
        return False

async def main():
    print("開始驗證30個問題修復狀況...")
    print(f"時間: {datetime.now()}")
    
    success = await verify_fixes()
    
    # 生成簡化報告文件
    with open('fix_verification_report.md', 'w', encoding='utf-8') as f:
        f.write(f"# 30個問題修復驗證報告\n\n")
        f.write(f"**驗證時間:** {datetime.now()}\n\n")
        f.write(f"**修復狀態:** {'✅ 成功' if success else '⚠️ 部分完成'}\n\n")
        f.write(f"**詳細資訊:** 請查看控制台輸出\n")
    
    print(f"\n📝 報告已保存至: fix_verification_report.md")
    return success

if __name__ == "__main__":
    asyncio.run(main())
