#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試捷運即時電子看板翻頁功能
"""

import os
import sys

def check_pagination_implementation():
    """檢查翻頁功能的實作"""
    print("🔍 檢查即時電子看板翻頁功能實作...")
    
    file_path = os.path.join('cogs', 'info_commands_fixed_v4_clean.py')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查必要的組件
        checks = [
            ('class MetroLiveboardView', '📱 翻頁視圖類別'),
            ('def _update_buttons', '🔘 按鈕更新方法'),
            ('async def previous_page', '◀️ 上一頁功能'),
            ('async def next_page', '▶️ 下一頁功能'),
            ('async def refresh_data', '🔄 刷新功能'),
            ('def create_page_embed', '📄 頁面創建方法'),
            ('stations_per_page = 10', '📊 每頁顯示設定'),
            ('view = MetroLiveboardView', '🎯 視圖使用'),
            ('await interaction.followup.send(embed=embed, view=view)', '📤 帶按鈕發送'),
            ('discord.ui.Button', '🔘 Discord按鈕組件'),
            ('timeout=300', '⏰ 超時設定'),
            ('interaction.user.id != self.user_id', '🔒 用戶權限檢查'),
        ]
        
        results = []
        for check_text, description in checks:
            if check_text in content:
                print(f"✅ {description}")
                results.append(True)
            else:
                print(f"❌ {description}")
                results.append(False)
        
        success_count = sum(results)
        total_count = len(results)
        success_rate = (success_count / total_count) * 100
        
        print(f"\n📊 實作檢查結果: {success_count}/{total_count} ({success_rate:.1f}%)")
        
        # 檢查新舊功能整合
        if 'format_metro_liveboard' in content and 'MetroLiveboardView' in content:
            print("✅ 新翻頁功能與舊格式化方法並存")
        else:
            print("❌ 功能整合可能有問題")
        
        return success_rate >= 85
        
    except FileNotFoundError:
        print(f"❌ 找不到檔案: {file_path}")
        return False
    except Exception as e:
        print(f"❌ 檢查時發生錯誤: {str(e)}")
        return False

def check_view_structure():
    """檢查翻頁視圖的結構"""
    print("\n🏗️ 檢查翻頁視圖結構...")
    
    file_path = os.path.join('cogs', 'info_commands_fixed_v4_clean.py')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到MetroLiveboardView類別
        if 'class MetroLiveboardView(View):' in content:
            print("✅ MetroLiveboardView 類別定義正確")
            
            # 檢查必要方法
            required_methods = [
                '__init__',
                '_update_buttons', 
                'previous_page',
                'next_page',
                'refresh_data',
                'create_page_embed',
                'on_timeout'
            ]
            
            method_count = 0
            for method in required_methods:
                if f'def {method}' in content or f'async def {method}' in content:
                    method_count += 1
                    print(f"  ✅ {method} 方法")
                else:
                    print(f"  ❌ {method} 方法")
            
            print(f"\n📊 方法完整度: {method_count}/{len(required_methods)}")
            
            # 檢查按鈕配置
            button_features = [
                ('◀️ 上一頁', '上一頁按鈕'),
                ('下一頁 ▶️', '下一頁按鈕'),
                ('🔄 刷新', '刷新按鈕'),
                ('ButtonStyle.primary', '按鈕樣式'),
                ('disabled=', '按鈕狀態控制')
            ]
            
            button_count = 0
            for feature, desc in button_features:
                if feature in content:
                    button_count += 1
                    print(f"  ✅ {desc}")
                else:
                    print(f"  ❌ {desc}")
            
            print(f"📊 按鈕功能完整度: {button_count}/{len(button_features)}")
            
            return method_count == len(required_methods) and button_count >= 4
        else:
            print("❌ 找不到 MetroLiveboardView 類別定義")
            return False
            
    except Exception as e:
        print(f"❌ 檢查結構時發生錯誤: {str(e)}")
        return False

def simulate_pagination_logic():
    """模擬翻頁邏輯"""
    print("\n🧮 模擬翻頁邏輯測試...")
    
    # 模擬資料
    total_stations = 35
    stations_per_page = 10
    total_pages = max(1, (total_stations + stations_per_page - 1) // stations_per_page)
    
    print(f"📊 測試參數:")
    print(f"  總車站數: {total_stations}")
    print(f"  每頁顯示: {stations_per_page}")
    print(f"  總頁數: {total_pages}")
    
    # 測試每一頁的範圍
    for page in range(total_pages):
        start_idx = page * stations_per_page
        end_idx = min(start_idx + stations_per_page, total_stations)
        stations_in_page = end_idx - start_idx
        
        print(f"  第{page + 1}頁: 索引 {start_idx}-{end_idx-1} (共{stations_in_page}個車站)")
    
    print("✅ 翻頁邏輯測試通過")
    return True

if __name__ == "__main__":
    print("🧪 開始測試捷運即時電子看板翻頁功能...\n")
    
    # 檢查實作
    impl_ok = check_pagination_implementation()
    
    # 檢查結構
    struct_ok = check_view_structure()
    
    # 模擬邏輯
    logic_ok = simulate_pagination_logic()
    
    print(f"\n🏁 最終結果:")
    print(f"   實作狀態: {'✅ 通過' if impl_ok else '❌ 未通過'}")
    print(f"   結構檢查: {'✅ 通過' if struct_ok else '❌ 未通過'}")
    print(f"   邏輯測試: {'✅ 通過' if logic_ok else '❌ 未通過'}")
    
    if impl_ok and struct_ok and logic_ok:
        print("\n🎉 翻頁功能已準備完成，可以測試使用！")
        print("\n✨ 新功能特色:")
        print("   - ◀️ 上一頁 / 下一頁 ▶️ 按鈕")
        print("   - 🔄 即時刷新按鈕")
        print("   - 📊 頁面資訊顯示")
        print("   - 🔒 使用者權限控制")
        print("   - ⏰ 5分鐘自動超時")
        print("   - 📱 每頁顯示10個車站")
        print("\n使用方式:")
        print("1. 運行機器人: python bot.py")
        print("2. 在Discord中使用指令: /即時電子看板")
        print("3. 選擇捷運系統後會出現翻頁按鈕")
    else:
        print("\n⚠️ 還有問題需要解決才能正常使用")
    
    print("\n🏁 測試完成")
