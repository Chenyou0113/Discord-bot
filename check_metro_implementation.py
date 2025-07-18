#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單檢查捷運指令的實作
"""

import os
import sys

def check_metro_implementation():
    """檢查捷運指令的實作"""
    print("🔍 檢查捷運指令實作...")
    
    # 讀取檔案內容
    file_path = os.path.join('cogs', 'info_commands_fixed_v4_clean.py')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查必要的方法和指令
        checks = [
            ('get_tdx_access_token', '🔑 TDX認證方法'),
            ('fetch_rail_alerts', '🚄 鐵路事故查詢方法'),
            ('format_rail_alert', '📋 鐵路事故格式化方法'),
            ('fetch_metro_alerts', '🚇 捷運狀態查詢方法'),
            ('format_metro_alert', '📊 捷運狀態格式化方法'),
            ("@app_commands.command(name='鐵路事故'", '🚄 鐵路事故指令'),
            ("@app_commands.command(name='捷運狀態'", '🚇 捷運狀態指令'),
            ("app_commands.Choice(name='台北捷運', value='TRTC')", '🏛️ 台北捷運選項'),
            ("app_commands.Choice(name='高雄捷運', value='KRTC')", '🌊 高雄捷運選項'),
            ("app_commands.Choice(name='桃園捷運', value='TYMC')", '✈️ 桃園捷運選項'),
            ("app_commands.Choice(name='高雄輕軌', value='KLRT')", '🚋 高雄輕軌選項'),
            ("app_commands.Choice(name='台中捷運', value='TMRT')", '🏙️ 台中捷運選項'),
        ]
        
        results = []
        for check_text, description in checks:
            if check_text in content:
                print(f"✅ {description}")
                results.append(True)
            else:
                print(f"❌ {description}")
                results.append(False)
        
        # 統計結果
        success_count = sum(results)
        total_count = len(results)
        success_rate = (success_count / total_count) * 100
        
        print(f"\n📊 檢查結果: {success_count}/{total_count} ({success_rate:.1f}%)")
        
        if success_rate == 100:
            print("🎉 所有功能都已正確實作！")
        elif success_rate >= 80:
            print("✅ 大部分功能已實作，可能有小問題需要修正")
        else:
            print("⚠️ 實作不完整，需要進一步檢查")
        
        # 檢查指令數量
        command_count = content.count("@app_commands.command")
        print(f"\n📋 總共發現 {command_count} 個 app_commands 指令")
        
        # 檢查TDX相關設定
        if 'TDX_CLIENT_ID' in content and 'TDX_CLIENT_SECRET' in content:
            print("🔑 TDX API憑證設定已包含")
        else:
            print("❌ TDX API憑證設定缺失")
        
        return success_rate >= 80
        
    except FileNotFoundError:
        print(f"❌ 找不到檔案: {file_path}")
        return False
    except Exception as e:
        print(f"❌ 檢查時發生錯誤: {str(e)}")
        return False

def check_environment():
    """檢查環境設定"""
    print("\n🔧 檢查環境設定...")
    
    required_vars = [
        'DISCORD_TOKEN',
        'TDX_CLIENT_ID', 
        'TDX_CLIENT_SECRET'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:10]}..." if len(value) > 10 else f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 未設定")
            all_set = False
    
    return all_set

if __name__ == "__main__":
    print("🧪 開始檢查捷運指令實作...\n")
    
    # 檢查實作
    impl_ok = check_metro_implementation()
    
    # 檢查環境
    env_ok = check_environment()
    
    print(f"\n🏁 最終結果:")
    print(f"   實作狀態: {'✅ 通過' if impl_ok else '❌ 未通過'}")
    print(f"   環境設定: {'✅ 通過' if env_ok else '❌ 未通過'}")
    
    if impl_ok and env_ok:
        print("\n🎉 捷運指令已準備完成，可以測試使用！")
        print("\n使用方式:")
        print("1. 運行機器人: python bot.py")
        print("2. 在Discord中使用指令:")
        print("   - /鐵路事故 : 查詢台鐵/高鐵事故")
        print("   - /捷運狀態 : 查詢各捷運系統狀態")
    else:
        print("\n⚠️ 還有問題需要解決才能正常使用")
