"""
驗證新聞連結按鈕修復
檢查 TRA 和 THSR 新聞是否已正確加入連結按鈕功能
"""

import re

file_path = r"c:\Users\xiaoy\OneDrive\桌面\Discord-bot hp\Discord-bot\cogs\info_commands_fixed_v4_clean.py"

print("=== 驗證新聞連結按鈕修復 ===\n")

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 檢查項目
checks = {
    "TRA 類別存在": r'class TRANewsPaginationView\(View\):',
    "THSR 類別存在": r'class THSRNewsPaginationView\(View\):',
    "clear_link_buttons 方法": r'def clear_link_buttons\(self\):',
    "移除純文字連結": r'🔗 \*\*公告連結:\*\*',
    "保存新聞URL": r'self\.current_news_url = news_url',
    "連結按鈕建立": r'Button\(\s*label=f"🔗 查看完整公告"',
    "按鈕樣式設定": r'style=discord\.ButtonStyle\.link',
    "按鈕加入視圖": r'self\.add_item\(link_button\)'
}

print("📋 檢查清單:")
results = {}

for check_name, pattern in checks.items():
    matches = len(re.findall(pattern, content))
    results[check_name] = matches
    
    if check_name == "移除純文字連結":
        # 這個應該是 0 (已移除)
        status = "✅" if matches == 0 else "❌"
        print(f"  {status} {check_name}: {matches} 個 (應為 0)")
    elif check_name in ["clear_link_buttons 方法", "保存新聞URL", "連結按鈕建立", "按鈕樣式設定", "按鈕加入視圖"]:
        # 這些應該有 2 個 (TRA + THSR)
        status = "✅" if matches >= 2 else "❌"
        print(f"  {status} {check_name}: {matches} 個 (應至少 2)")
    else:
        # TRA/THSR 類別各 1 個
        status = "✅" if matches >= 1 else "❌"
        print(f"  {status} {check_name}: {matches} 個")

print(f"\n📊 檢查摘要:")
passed = sum(1 for k, v in results.items() if 
             (k == "移除純文字連結" and v == 0) or
             (k in ["clear_link_buttons 方法", "保存新聞URL", "連結按鈕建立", "按鈕樣式設定", "按鈕加入視圖"] and v >= 2) or
             (k in ["TRA 類別存在", "THSR 類別存在"] and v >= 1))

total = len(checks)
print(f"通過: {passed}/{total} 項檢查")

if passed == total:
    print("🎉 所有檢查通過！")
else:
    print("⚠️ 部分檢查未通過，請檢查詳細結果")

print(f"\n🔍 詳細統計:")
print(f"  TRA 類別: {results['TRA 類別存在']} 個")
print(f"  THSR 類別: {results['THSR 類別存在']} 個")
print(f"  清理方法: {results['clear_link_buttons 方法']} 個")
print(f"  純文字連結: {results['移除純文字連結']} 個 (已移除)")
print(f"  URL 保存: {results['保存新聞URL']} 個")
print(f"  按鈕建立: {results['連結按鈕建立']} 個")
print(f"  按鈕樣式: {results['按鈕樣式設定']} 個")
print(f"  加入視圖: {results['按鈕加入視圖']} 個")

print(f"\n💡 預期行為:")
print("1. 使用者執行 /tra_news 或 /thsr_news")
print("2. Bot 顯示新聞列表 (分頁)")
print("3. 每則新聞下方有 '🔗 查看完整公告' 藍色按鈕")
print("4. 點擊按鈕在新分頁開啟官方公告網頁")
print("5. 換頁時按鈕會自動更新為當前新聞的連結")

print(f"\n🔧 使用說明:")
print("- 測試指令: /tra_news, /thsr_news")
print("- 確認按鈕顏色: 藍色 (外部連結)")
print("- 確認按鈕文字: '🔗 查看完整公告'")
print("- 確認點擊行為: 開啟新分頁到官方網站")