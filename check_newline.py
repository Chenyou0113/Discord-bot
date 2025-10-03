"""
確認設施地圖連結的換行符是否正確
"""

file_path = r"c:\Users\xiaoy\OneDrive\桌面\Discord-bot hp\Discord-bot\cogs\info_commands_fixed_v4_clean.py"

# 讀取文件
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 搜尋設施地圖部分
import re

# 找到設施地圖部分
pattern = r'if map_links:\s+embed\.add_field\(\s+name="🗺️ 車站設施圖",\s+value="(.+?)"\s*,'

matches = re.findall(pattern, content, re.DOTALL)

if matches:
    print("✅ 找到設施地圖代碼")
    for i, match in enumerate(matches):
        print(f"\n匹配 {i+1}:")
        print(f"Value 參數: {repr(match)}")
        
        if '\\\\n' in match:
            print("❌ 發現雙反斜線轉義問題: \\\\n")
        elif '\\n' in match and match != r'\n':
            print("⚠️ 發現反斜線n字符串")
        else:
            print("✅ 使用正確的換行符")
else:
    print("❌ 找不到設施地圖代碼")

# 檢查是否有錯誤的轉義
if '\\\\n".join(map_links)' in content:
    print("\n❌ 發現錯誤: 使用了 \\\\n 雙反斜線")
    print("需要修正為: \\n")
elif r'"\n".join(map_links)' in content:
    print("\n✅ 正確: 使用了 \\n 換行符")
else:
    print("\n⚠️ 無法確定換行符類型")

# 搜尋具體的那一行
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if 'value="\\n".join(map_links)' in line or 'value="\n".join(map_links)' in line:
        print(f"\n第 {i} 行: {line.strip()}")
