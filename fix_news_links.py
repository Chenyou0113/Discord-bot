"""
修復高鐵和台鐵新聞連結顯示問題
將純文字連結改為可點擊的按鈕
"""

import re

file_path = r"c:\Users\xiaoy\OneDrive\桌面\Discord-bot hp\Discord-bot\cogs\info_commands_fixed_v4_clean.py"

print("=== 修復新聞連結按鈕 ===\n")

# 讀取檔案
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"📖 檔案大小: {len(content)} 字元")

# 修復策略: 找到兩個新聞類別並個別處理

# 1. 找到 TRANewsPaginationView 的 create_embed 方法
tra_class_match = re.search(r'class TRANewsPaginationView\(View\):(.*?)(?=class \w+|$)', content, re.DOTALL)
if tra_class_match:
    print("✅ 找到 TRANewsPaginationView 類別")
    
    # 在 TRA 類別中找到要替換的連結代碼塊
    tra_content = tra_class_match.group(1)
    
    # 找到 field_value 的設定部分
    tra_link_pattern = r'(\s+# 組合 field value\s+field_value = f"{content}\\n\\n🕒 \*\*發布時間:\*\* {formatted_time}"\s+if news_url:\s+field_value \+= f"\\n🔗 \*\*公告連結:\*\* {news_url}")'
    
    tra_replacement = '''
            # 組合 field value (移除純文字連結)
            field_value = f"{content}\\n\\n🕒 **發布時間:** {formatted_time}"
            
            # 保存當前新聞的 URL 用於建立按鈕
            if news_url:
                self.current_news_url = news_url
                self.current_news_title = title
            else:
                self.current_news_url = None
                self.current_news_title = None'''
    
    if re.search(tra_link_pattern, content):
        print("✅ 找到 TRA 新聞連結代碼")
        content = re.sub(tra_link_pattern, tra_replacement, content)
        print("✅ 已更新 TRA 新聞連結代碼")
    else:
        print("⚠️ 未找到 TRA 新聞連結代碼模式")

# 2. 找到 THSRNewsPaginationView 的 create_embed 方法
thsr_class_match = re.search(r'class THSRNewsPaginationView\(View\):(.*?)(?=class \w+|$)', content, re.DOTALL)
if thsr_class_match:
    print("✅ 找到 THSRNewsPaginationView 類別")
    
    # 類似的處理 THSR
    thsr_link_pattern = r'(\s+# 組合 field value\s+field_value = f"{content}\\n\\n🕒 \*\*發布時間:\*\* {formatted_time}"\s+if news_url:\s+field_value \+= f"\\n🔗 \*\*公告連結:\*\* {news_url}")'
    
    thsr_replacement = '''
            # 組合 field value (移除純文字連結)
            field_value = f"{content}\\n\\n🕒 **發布時間:** {formatted_time}"
            
            # 保存當前新聞的 URL 用於建立按鈕
            if news_url:
                self.current_news_url = news_url
                self.current_news_title = title
            else:
                self.current_news_url = None
                self.current_news_title = None'''
    
    if re.search(thsr_link_pattern, content):
        print("✅ 找到 THSR 新聞連結代碼")
        content = re.sub(thsr_link_pattern, thsr_replacement, content)
        print("✅ 已更新 THSR 新聞連結代碼")
    else:
        print("⚠️ 未找到 THSR 新聞連結代碼模式")

else:
    print("❌ 未找到 THSRNewsPaginationView 類別")

# 3. 為兩個類別加上 clear_link_buttons 方法和連結按鈕邏輯
# 先檢查是否已經有 clear_link_buttons 方法
if 'def clear_link_buttons(self)' not in content:
    print("➕ 加入 clear_link_buttons 方法")
    
    # 為 TRANewsPaginationView 加入方法
    tra_insert_pattern = r'(class TRANewsPaginationView\(View\):.*?def create_embed\(self\))'
    tra_methods = '''
    def clear_link_buttons(self):
        """清除所有連結按鈕"""
        # 移除所有 ButtonStyle.link 的按鈕
        items_to_remove = []
        for item in self.children:
            if hasattr(item, 'style') and item.style == discord.ButtonStyle.link:
                items_to_remove.append(item)
        for item in items_to_remove:
            self.remove_item(item)
    
    def create_embed(self)'''
    
    content = re.sub(tra_insert_pattern, lambda m: m.group(1).replace('def create_embed(self)', tra_methods), content)
    
    # 為 THSRNewsPaginationView 加入方法
    thsr_insert_pattern = r'(class THSRNewsPaginationView\(View\):.*?def create_embed\(self\))'
    thsr_methods = '''
    def clear_link_buttons(self):
        """清除所有連結按鈕"""
        # 移除所有 ButtonStyle.link 的按鈕
        items_to_remove = []
        for item in self.children:
            if hasattr(item, 'style') and item.style == discord.ButtonStyle.link:
                items_to_remove.append(item)
        for item in items_to_remove:
            self.remove_item(item)
    
    def create_embed(self)'''
    
    content = re.sub(thsr_insert_pattern, lambda m: m.group(1).replace('def create_embed(self)', thsr_methods), content)
    print("✅ 已加入 clear_link_buttons 方法")

print(f"\n📝 準備寫入檔案...")

# 寫回檔案
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 檔案修改完成!")
print("\n=== 修改摘要 ===")
print("1. 移除純文字連結顯示")
print("2. 保存新聞 URL 到實例變數")
print("3. 加入 clear_link_buttons 方法")
print("4. 準備在 create_embed 中動態加入連結按鈕")
print("\n注意: 還需要手動加入連結按鈕建立邏輯")