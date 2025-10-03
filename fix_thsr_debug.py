"""
精確修復高鐵新聞連結按鈕
加入除錯資訊和更多 URL 欄位檢查
"""

import re

file_path = r"c:\Users\xiaoy\OneDrive\桌面\Discord-bot hp\Discord-bot\cogs\info_commands_fixed_v4_clean.py"

print("=== 精確修復高鐵新聞連結按鈕 ===\n")

# 讀取檔案
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修復 1: 在高鐵新聞按鈕建立邏輯中加入除錯資訊
# 找到高鐵類別中的按鈕建立邏輯
thsr_pattern = r'(class THSRNewsPaginationView.*?# 如果有新聞連結,加入連結按鈕\s+if hasattr\(self, \'current_news_url\'\) and self\.current_news_url:\s+)(link_button = Button\(.*?self\.add_item\(link_button\))(.*?# 設置頁腳)'

def thsr_replacement(match):
    before = match.group(1)
    button_code = match.group(2)
    after = match.group(3)
    
    new_button_code = '''print(f"✅ THSR 正在建立連結按鈕: {self.current_news_url[:50]}...")
            link_button = Button(
                label=f"🔗 查看完整公告",
                url=self.current_news_url,
                style=discord.ButtonStyle.link
            )
            self.add_item(link_button)
            print(f"✅ THSR 按鈕已加入視圖，當前按鈕數量: {len(self.children)}")
        else:
            print(f"❌ THSR 未建立連結按鈕，current_news_url: {getattr(self, 'current_news_url', 'NOT_SET')}")
        '''
    
    return before + new_button_code + after

if re.search(thsr_pattern, content, re.DOTALL):
    print("✅ 找到高鐵新聞按鈕建立邏輯")
    content = re.sub(thsr_pattern, thsr_replacement, content, flags=re.DOTALL)
    print("✅ 已加入高鐵新聞按鈕除錯資訊")
else:
    print("❌ 未找到高鐵新聞按鈕建立邏輯")

# 修復 2: 為台鐵新聞也加入類似的除錯 (如果還沒有的話)
tra_pattern = r'(class TRANewsPaginationView.*?# 如果有新聞連結,加入連結按鈕\s+if hasattr\(self, \'current_news_url\'\) and self\.current_news_url:\s+)(link_button = Button\(.*?self\.add_item\(link_button\))(.*?# 設置頁腳)'

def tra_replacement(match):
    before = match.group(1)
    button_code = match.group(2)
    after = match.group(3)
    
    if "print(" in button_code:
        # 已經有除錯資訊
        return match.group(0)
    
    new_button_code = '''print(f"✅ TRA 正在建立連結按鈕: {self.current_news_url[:50]}...")
            link_button = Button(
                label=f"🔗 查看完整公告",
                url=self.current_news_url,
                style=discord.ButtonStyle.link
            )
            self.add_item(link_button)
            print(f"✅ TRA 按鈕已加入視圖，當前按鈕數量: {len(self.children)}")
        else:
            print(f"❌ TRA 未建立連結按鈕，current_news_url: {getattr(self, 'current_news_url', 'NOT_SET')}")
        '''
    
    return before + new_button_code + after

if re.search(tra_pattern, content, re.DOTALL):
    print("✅ 找到台鐵新聞按鈕建立邏輯")
    content = re.sub(tra_pattern, tra_replacement, content, flags=re.DOTALL)
    print("✅ 已加入台鐵新聞按鈕除錯資訊")
else:
    print("⚠️ 未找到台鐵新聞按鈕建立邏輯或已有除錯資訊")

# 寫回檔案
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 檔案修改完成!")
print("\n📝 修改內容:")
print("1. 在高鐵新聞中加入連結按鈕除錯資訊")
print("2. 增強 URL 欄位檢查 (已在之前完成)")
print("3. 加入按鈕建立狀態顯示")
print("\n🔧 接下來需要:")
print("1. 重新啟動 bot")
print("2. 執行 /thsr_news 指令")
print("3. 查看終端機輸出的除錯資訊")