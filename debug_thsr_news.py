"""
檢查高鐵新聞按鈕問題
分析可能的原因並提供修復方案
"""

import re

file_path = r"c:\Users\xiaoy\OneDrive\桌面\Discord-bot hp\Discord-bot\cogs\info_commands_fixed_v4_clean.py"

print("=== 檢查高鐵新聞按鈕問題 ===\n")

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 找到 THSR 新聞的欄位提取邏輯
print("🔍 檢查高鐵新聞欄位提取邏輯:")
thsr_pattern = r'# 提取新聞資訊.*?news_url = news\.get\([^)]+\)'
matches = re.findall(thsr_pattern, content, re.DOTALL)

for i, match in enumerate(matches, 1):
    print(f"\n📰 新聞資料提取 {i}:")
    lines = match.split('\n')
    for line in lines:
        if 'news_url' in line or 'NewsURL' in line or 'Link' in line:
            print(f"  {line.strip()}")

# 2. 檢查按鈕建立邏輯
print(f"\n🔘 檢查按鈕建立邏輯:")
button_pattern = r'if hasattr\(self, \'current_news_url\'\).*?self\.add_item\(link_button\)'
button_matches = re.findall(button_pattern, content, re.DOTALL)

print(f"找到 {len(button_matches)} 個按鈕建立邏輯")

# 3. 檢查可能的問題
print(f"\n⚠️ 可能的問題:")
print("1. API 欄位名稱不正確")
print("2. news_url 為空值")
print("3. current_news_url 未正確設定")
print("4. 按鈕建立後未呼叫 edit_message")

# 4. 提供修復建議
print(f"\n🔧 修復建議:")
print("1. 加入更多 URL 欄位檢查:")
print("   news_url = news.get('NewsURL') or news.get('Link') or news.get('Url') or news.get('DetailURL') or ''")
print()
print("2. 加入除錯資訊:")
print("   print(f'News URL: {news_url}') # 除錯用")
print()
print("3. 檢查按鈕是否正確加入視圖:")
print("   print(f'Button added: {hasattr(self, \"current_news_url\") and self.current_news_url}') # 除錯用")

# 5. 檢查當前的 URL 提取邏輯
print(f"\n📋 當前 URL 提取邏輯:")
url_extraction_pattern = r"news_url = news\.get\([^)]+\)"
url_matches = re.findall(url_extraction_pattern, content)

for match in url_matches:
    print(f"  {match}")

# 檢查是否有除錯資訊
if 'print(' in content and 'news_url' in content:
    print(f"\n✅ 代碼中已包含除錯資訊")
else:
    print(f"\n❌ 代碼中缺少除錯資訊")