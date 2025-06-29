#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整功能驗證 - 包含新的公路監視器功能
"""

import sys
import os
import logging

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設定日誌
logging.basicConfig(level=logging.INFO)

def verify_all_commands():
    """驗證所有指令功能"""
    print("🎯 Discord 機器人完整功能驗證")
    print("=" * 60)
    
    results = {
        "success": [],
        "failed": [],
        "warnings": []
    }
    
    try:
        # 測試各個 Cog 匯入
        cogs_to_test = [
            ('cogs.reservoir_commands', 'ReservoirCommands'),
            ('cogs.weather_commands', 'WeatherCommands'),
            ('cogs.info_commands_fixed_v4_clean', 'InfoCommands')
        ]
        
        print("📦 測試 Cog 匯入:")
        
        for module_name, class_name in cogs_to_test:
            try:
                module = __import__(module_name, fromlist=[class_name])
                cog_class = getattr(module, class_name)
                cog_instance = cog_class(None)
                
                print(f"   ✅ {class_name} - 匯入成功")
                results["success"].append(f"{class_name} 匯入")
                
                # 檢查指令
                if class_name == 'ReservoirCommands':
                    commands = [
                        'reservoir_list',
                        'water_disaster_cameras', 
                        'highway_cameras'  # 新增的指令
                    ]
                    
                    print(f"      🔍 檢查 ReservoirCommands 指令:")
                    for cmd in commands:
                        if hasattr(cog_instance, cmd):
                            print(f"         ✅ {cmd}")
                            results["success"].append(f"指令 {cmd}")
                        else:
                            print(f"         ❌ {cmd}")
                            results["failed"].append(f"指令 {cmd}")
                
                elif class_name == 'WeatherCommands':
                    if hasattr(cog_instance, 'weather'):
                        print(f"      ✅ weather 指令存在")
                        results["success"].append("weather 指令")
                    else:
                        print(f"      ❌ weather 指令不存在")
                        results["failed"].append("weather 指令")
                
                elif class_name == 'InfoCommands':
                    # 檢查是否已移除 weather 指令衝突
                    if hasattr(cog_instance, 'weather'):
                        print(f"      ⚠️ InfoCommands 仍有 weather 指令 (可能衝突)")
                        results["warnings"].append("InfoCommands weather 指令衝突")
                    else:
                        print(f"      ✅ InfoCommands 已移除 weather 指令")
                        results["success"].append("weather 指令衝突解決")
                
            except Exception as e:
                print(f"   ❌ {class_name} - 匯入失敗: {str(e)}")
                results["failed"].append(f"{class_name} 匯入")
        
        print(f"\n🚀 功能特性檢查:")
        
        # 檢查公路監視器功能
        try:
            from cogs.reservoir_commands import HighwayCameraView, HighwayCameraInfoModal
            print(f"   ✅ 公路監視器 View 類別")
            results["success"].append("公路監視器 View 類別")
        except ImportError:
            print(f"   ❌ 公路監視器 View 類別")
            results["failed"].append("公路監視器 View 類別")
        
        # 檢查主程式
        try:
            print(f"\n🤖 檢查主程式:")
            with open('bot.py', 'r', encoding='utf-8') as f:
                bot_content = f.read()
                
            if 'reservoir_commands' in bot_content:
                print(f"   ✅ ReservoirCommands 已載入")
                results["success"].append("ReservoirCommands 載入")
            else:
                print(f"   ❌ ReservoirCommands 未載入")
                results["failed"].append("ReservoirCommands 載入")
                
            if 'weather_commands' in bot_content:
                print(f"   ✅ WeatherCommands 已載入")
                results["success"].append("WeatherCommands 載入")
            else:
                print(f"   ❌ WeatherCommands 未載入")
                results["failed"].append("WeatherCommands 載入")
        
        except Exception as e:
            print(f"   ❌ 主程式檢查失敗: {str(e)}")
            results["failed"].append("主程式檢查")
        
        print(f"\n" + "=" * 60)
        print("📊 驗證結果")
        print("=" * 60)
        
        print(f"✅ 成功項目 ({len(results['success'])}):")
        for item in results["success"]:
            print(f"   • {item}")
        
        if results["warnings"]:
            print(f"\n⚠️ 警告項目 ({len(results['warnings'])}):")
            for item in results["warnings"]:
                print(f"   • {item}")
        
        if results["failed"]:
            print(f"\n❌ 失敗項目 ({len(results['failed'])}):")
            for item in results["failed"]:
                print(f"   • {item}")
        
        print(f"\n🎯 指令清單:")
        commands_list = [
            "/reservoir_list - 水庫查詢",
            "/water_cameras - 水利監視器", 
            "/highway_cameras - 公路監視器 (新增)",
            "/weather - 天氣查詢",
            "/river_levels - 河川水位",
            "/check_permissions - 權限檢查"
        ]
        
        for cmd in commands_list:
            print(f"   🎯 {cmd}")
        
        print(f"\n💡 使用提示:")
        print(f"   1. 確保機器人有 '嵌入連結' 權限")
        print(f"   2. 使用 /check_permissions 檢查權限狀態")
        print(f"   3. 新的公路監視器功能：/highway_cameras location:台62線")
        
        # 計算成功率
        total_items = len(results["success"]) + len(results["failed"])
        success_rate = (len(results["success"]) / total_items * 100) if total_items > 0 else 0
        
        print(f"\n📈 整體成功率: {success_rate:.1f}% ({len(results['success'])}/{total_items})")
        
        if len(results["failed"]) == 0:
            print(f"\n🎉 所有功能驗證通過！機器人已準備就緒。")
            return True
        else:
            print(f"\n⚠️ 有 {len(results['failed'])} 項功能需要修復。")
            return False
            
    except Exception as e:
        print(f"❌ 驗證過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    success = verify_all_commands()
    
    print(f"\n" + "=" * 60)
    if success:
        print("🚀 Discord 機器人已準備就緒！")
        print("💡 執行 'python bot.py' 啟動機器人")
    else:
        print("🔧 請修復上述問題後重新驗證")
    print("=" * 60)

if __name__ == "__main__":
    main()
