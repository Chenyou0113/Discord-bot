"""
修復 THSR 新聞中的格式問題
修復換行符問題並加入連結按鈕邏輯
"""

import re

file_path = r"c:\Users\xiaoy\OneDrive\桌面\Discord-bot hp\Discord-bot\cogs\info_commands_fixed_v4_clean.py"

print("=== 修復 THSR 新聞格式問題 ===\n")

# 讀取檔案
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 修復格式問題 - 找到有問題的 field_value 行
broken_pattern = r'field_value = f"{content}\n\n🕒 \*\*發布時間:\*\* {formatted_time}"'
fixed_replacement = r'field_value = f"{content}\\n\\n🕒 **發布時間:** {formatted_time}"'

if re.search(broken_pattern, content):
    print("✅ 找到有問題的格式")
    content = re.sub(broken_pattern, fixed_replacement, content)
    print("✅ 已修復格式問題")
else:
    print("⚠️ 未找到格式問題")

# 為 THSR 新聞加入連結按鈕邏輯
# 找到 embed.add_field 之後和 return embed 之前的位置
thsr_pattern = r'(class THSRNewsPaginationView.*?embed\.add_field\(\s*name=f"📌 第 {news_number} 則 - {title}",\s*value=field_value,\s*inline=False\s*\)\s*)\s*(# 設置頁腳)'

thsr_replacement = r'''\1
        
        # 清除舊的連結按鈕
        self.clear_link_buttons()
        
        # 如果有新聞連結,加入連結按鈕
        if hasattr(self, 'current_news_url') and self.current_news_url:
            link_button = Button(
                label=f"🔗 查看完整公告",
                url=self.current_news_url,
                style=discord.ButtonStyle.link
            )
            self.add_item(link_button)
        
        \2'''

if re.search(r'class THSRNewsPaginationView', content, re.DOTALL):
    print("✅ 找到 THSR 類別")
    if re.search(thsr_pattern, content, re.DOTALL):
        print("✅ 找到插入位置")
        content = re.sub(thsr_pattern, thsr_replacement, content, flags=re.DOTALL)
        print("✅ 已加入連結按鈕邏輯")
    else:
        print("⚠️ 未找到合適的插入位置")
        # 備用方案：在 return embed 前插入
        backup_pattern = r'(class THSRNewsPaginationView.*?)(\s*# 設置頁腳.*?return embed)'
        backup_replacement = r'''\1
        
        # 清除舊的連結按鈕
        self.clear_link_buttons()
        
        # 如果有新聞連結,加入連結按鈕
        if hasattr(self, 'current_news_url') and self.current_news_url:
            link_button = Button(
                label=f"🔗 查看完整公告",
                url=self.current_news_url,
                style=discord.ButtonStyle.link
            )
            self.add_item(link_button)
        
\2'''
        if re.search(backup_pattern, content, re.DOTALL):
            content = re.sub(backup_pattern, backup_replacement, content, flags=re.DOTALL)
            print("✅ 已使用備用方案加入連結按鈕邏輯")

# 為 TRA 新聞也加入相同的邏輯 (如果還沒有的話)
tra_pattern = r'(class TRANewsPaginationView.*?embed\.add_field\(\s*name=f"📌 第 {news_number} 則 - {title}",\s*value=field_value,\s*inline=False\s*\)\s*)\s*(# 設置頁腳)'

tra_replacement = r'''\1
        
        # 清除舊的連結按鈕
        self.clear_link_buttons()
        
        # 如果有新聞連結,加入連結按鈕
        if hasattr(self, 'current_news_url') and self.current_news_url:
            link_button = Button(
                label=f"🔗 查看完整公告",
                url=self.current_news_url,
                style=discord.ButtonStyle.link
            )
            self.add_item(link_button)
        
        \2'''

if re.search(r'class TRANewsPaginationView', content, re.DOTALL):
    print("✅ 找到 TRA 類別")
    if 'self.clear_link_buttons()' not in content or content.count('self.clear_link_buttons()') < 2:
        if re.search(tra_pattern, content, re.DOTALL):
            print("✅ 找到 TRA 插入位置")
            content = re.sub(tra_pattern, tra_replacement, content, flags=re.DOTALL)
            print("✅ 已為 TRA 加入連結按鈕邏輯")
        else:
            print("⚠️ 未找到 TRA 合適的插入位置")

# 寫回檔案
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 檔案修改完成!")
print("\n=== 修改摘要 ===")
print("1. 修復 field_value 格式問題")
print("2. 為 THSR 新聞加入連結按鈕邏輯")
print("3. 為 TRA 新聞加入連結按鈕邏輯(如需要)")