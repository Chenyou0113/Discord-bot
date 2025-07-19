#!/usr/bin/env python3
"""
測試台鐵功能修復
檢查 TRALiveboardView 和 TRADelayView 是否正確修復了 'Interaction' object has no attribute 'cog' 錯誤
"""

import sys
import ast
import re

def check_tra_view_classes(file_path):
    """檢查台鐵 View 類別是否正確修復"""
    print("🔍 檢查台鐵 View 類別修復狀況...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 檢查 TRALiveboardView 類別
    print("\n📋 檢查 TRALiveboardView:")
    
    # 檢查初始化方法
    if "def __init__(self, interaction, county, station_name, station_id):" in content:
        print("  ✅ __init__ 方法參數正確 (使用 interaction)")
    else:
        print("  ❌ __init__ 方法參數有問題")
        issues.append("TRALiveboardView.__init__ 參數問題")
    
    # 檢查 cog 屬性設定
    if "self.cog = interaction.client.get_cog('InfoCommands')" in content:
        print("  ✅ 正確設定 cog 屬性")
    else:
        print("  ❌ cog 屬性設定有問題")
        issues.append("TRALiveboardView cog 屬性設定問題")
    
    # 檢查是否還有 self.ctx.cog 的使用
    tra_liveboard_section = content[content.find("class TRALiveboardView"):content.find("class TRADelayView")]
    if "self.ctx.cog" in tra_liveboard_section:
        print("  ❌ 仍然使用 self.ctx.cog")
        issues.append("TRALiveboardView 仍使用 self.ctx.cog")
    else:
        print("  ✅ 已移除所有 self.ctx.cog 使用")
    
    # 檢查按鈕方法中的用戶檢查
    if "if interaction.user != self.interaction.user:" in tra_liveboard_section:
        print("  ✅ 按鈕方法中正確使用 self.interaction.user")
    else:
        print("  ❌ 按鈕方法中用戶檢查有問題")
        issues.append("TRALiveboardView 按鈕用戶檢查問題")
    
    # 檢查 TRADelayView 類別
    print("\n📋 檢查 TRADelayView:")
    
    # 檢查初始化方法
    if "def __init__(self, interaction, county):" in content:
        print("  ✅ __init__ 方法參數正確 (使用 interaction)")
    else:
        print("  ❌ __init__ 方法參數有問題")
        issues.append("TRADelayView.__init__ 參數問題")
    
    # 檢查是否還有 self.ctx.cog 的使用
    tra_delay_section = content[content.find("class TRADelayView"):content.find("async def setup(bot)")]
    if "self.ctx.cog" in tra_delay_section:
        print("  ❌ 仍然使用 self.ctx.cog")
        issues.append("TRADelayView 仍使用 self.ctx.cog")
    else:
        print("  ✅ 已移除所有 self.ctx.cog 使用")
    
    return issues

def check_metro_api_updates(file_path):
    """檢查捷運 API 更新"""
    print("\n🚇 檢查捷運 API 端點更新...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issues = []
    
    # 檢查台北捷運 API
    if "%24top=117" in content and "Rail/Metro/LiveBoard/TRTC" in content:
        print("  ✅ 台北捷運 API 已更新為 117 筆資料")
    else:
        print("  ❌ 台北捷運 API 更新有問題")
        issues.append("台北捷運 API 未正確更新")
    
    # 檢查高雄捷運 API
    if "%24top=77" in content and "Rail/Metro/LiveBoard/KRTC" in content:
        print("  ✅ 高雄捷運 API 已更新為 77 筆資料")
    else:
        print("  ❌ 高雄捷運 API 更新有問題")
        issues.append("高雄捷運 API 未正確更新")
    
    # 檢查高雄輕軌 API
    if "%24top=33" in content and "Rail/Metro/LiveBoard/KLRT" in content:
        print("  ✅ 高雄輕軌 API 已更新為 33 筆資料")
    else:
        print("  ❌ 高雄輕軌 API 更新有問題")
        issues.append("高雄輕軌 API 未正確更新")
    
    return issues

def main():
    file_path = "cogs/info_commands_fixed_v4_clean.py"
    
    print("🔧 台鐵功能修復驗證報告")
    print("=" * 50)
    
    # 檢查 View 類別修復
    view_issues = check_tra_view_classes(file_path)
    
    # 檢查捷運 API 更新
    api_issues = check_metro_api_updates(file_path)
    
    # 彙總結果
    all_issues = view_issues + api_issues
    
    print("\n" + "=" * 50)
    print("📊 修復結果彙總:")
    
    if not all_issues:
        print("🎉 所有修復都已完成！")
        print("✅ 台鐵 View 類別已修復 'Interaction' object has no attribute 'cog' 錯誤")
        print("✅ 捷運 API 端點已按要求更新")
        print("\n🚀 修復摘要:")
        print("  - TRALiveboardView: 修復 interaction.cog 錯誤")
        print("  - TRADelayView: 修復 interaction.cog 錯誤")
        print("  - 台北捷運: 更新為 117 筆資料")
        print("  - 高雄捷運: 更新為 77 筆資料")
        print("  - 高雄輕軌: 更新為 33 筆資料")
        return True
    else:
        print("❌ 發現以下問題:")
        for issue in all_issues:
            print(f"  - {issue}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
