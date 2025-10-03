"""
驗證程式碼改動
確認設施地圖按鈕實作已正確加入
"""

import re

file_path = r"c:\Users\xiaoy\OneDrive\桌面\Discord-bot hp\Discord-bot\cogs\info_commands_fixed_v4_clean.py"

print("=== 檢查程式碼改動 ===\n")

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 檢查 1: Button 匯入
if 'from discord.ui import Select, View, Button' in content:
    print("✅ 已匯入 Button 類別")
else:
    print("❌ 缺少 Button 匯入")

# 檢查 2: Button 建立邏輯
button_pattern = r'button = Button\('
if re.search(button_pattern, content):
    print("✅ 已加入 Button 建立邏輯")
    # 計算出現次數
    count = len(re.findall(button_pattern, content))
    print(f"   找到 {count} 處 Button 建立")
else:
    print("❌ 缺少 Button 建立邏輯")

# 檢查 3: ButtonStyle.link
if 'ButtonStyle.link' in content or 'discord.ButtonStyle.link' in content:
    print("✅ 使用 ButtonStyle.link (外部連結)")
else:
    print("❌ 缺少 ButtonStyle 設定")

# 檢查 4: button_view
if 'button_view = View(timeout=300)' in content:
    print("✅ 建立 button_view 物件")
else:
    print("❌ 缺少 button_view 物件")

# 檢查 5: 按鈕加入到 view
if 'button_view.add_item(button)' in content:
    print("✅ 按鈕加入到 view")
else:
    print("❌ 按鈕未加入到 view")

# 檢查 6: edit_message 使用 button_view
if 'view=button_view' in content:
    print("✅ edit_message 使用 button_view")
else:
    print("❌ edit_message 未使用 button_view")

# 檢查 7: 移除舊的 Markdown 連結 field
markdown_link_field = r'name="🗺️ 車站設施圖"'
old_pattern = r'value="\\n"\.join\(map_links\)'
if re.search(markdown_link_field, content):
    if re.search(old_pattern, content):
        print("⚠️  仍有舊的 Markdown 連結 field (應已移除)")
    else:
        print("✅ Markdown 連結 field 已移除")
else:
    print("✅ Markdown 連結 field 已移除")

print("\n=== 實作說明 ===")
print("舊版: 在 embed field 中使用 Markdown 連結 [文字](URL)")
print("      → Discord 不支援,顯示為純文字")
print()
print("新版: 使用 discord.ui.Button 組件")
print("      → 訊息下方顯示藍色按鈕")
print("      → 點擊後在新分頁開啟 PDF")
print("      → 最多可加入 5 個按鈕")
print()
print("使用者體驗:")
print("1. 選擇路線")
print("2. 選擇車站")
print("3. 查看車站資訊 embed")
print("4. 點擊下方的「🗺️ 車站資訊圖」按鈕")
print("5. 自動開啟 PDF 檔案")
