#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord 機器人權限與設定檢查工具
檢查機器人是否有足夠的權限來嵌入圖片
"""

import discord
from discord.ext import commands
import asyncio
import json
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BotPermissionChecker:
    """機器人權限檢查工具"""
    
    @staticmethod
    def check_required_permissions():
        """檢查機器人所需的權限列表"""
        required_permissions = {
            # 基本訊息權限
            'send_messages': '發送訊息',
            'embed_links': '嵌入連結 (圖片顯示必需)',
            'attach_files': '附加檔案',
            'read_message_history': '讀取訊息歷史',
            'use_external_emojis': '使用外部表情符號',
            
            # 進階功能權限
            'manage_messages': '管理訊息 (刪除/編輯)',
            'add_reactions': '新增反應',
            'use_application_commands': '使用應用程式指令 (Slash Commands)',
            
            # 可選權限
            'administrator': '管理員 (可選，但能解決大部分權限問題)',
        }
        
        return required_permissions
    
    @staticmethod
    def create_permission_check_embed():
        """創建權限檢查說明 embed"""
        embed = discord.Embed(
            title="🔐 Discord 機器人權限檢查",
            description="檢查機器人是否具備圖片嵌入所需的權限",
            color=discord.Color.blue()
        )
        
        required_perms = BotPermissionChecker.check_required_permissions()
        
        # 必要權限
        essential_perms = [
            'send_messages', 'embed_links', 'use_application_commands'
        ]
        
        essential_desc = "\n".join([
            f"• **{required_perms[perm]}** (`{perm}`)"
            for perm in essential_perms
        ])
        
        embed.add_field(
            name="🚨 必要權限",
            value=essential_desc,
            inline=False
        )
        
        # 建議權限
        recommended_perms = [
            'attach_files', 'read_message_history', 'use_external_emojis', 'add_reactions'
        ]
        
        recommended_desc = "\n".join([
            f"• **{required_perms[perm]}** (`{perm}`)"
            for perm in recommended_perms
        ])
        
        embed.add_field(
            name="💡 建議權限",
            value=recommended_desc,
            inline=False
        )
        
        # 解決方案
        embed.add_field(
            name="🔧 權限設定方法",
            value="""
1. **伺服器設定** → **角色**
2. 找到機器人的角色
3. 確保以下權限已啟用：
   • `嵌入連結` (Embed Links) ⭐ **最重要**
   • `發送訊息` (Send Messages)
   • `使用斜線指令` (Use Application Commands)
4. 或直接給予 `管理員` 權限
            """,
            inline=False
        )
        
        # 測試指令
        embed.add_field(
            name="🧪 測試方法",
            value="""
使用 `/water_cameras` 指令測試：
• 如果看到圖片 → 權限正常 ✅
• 如果看不到圖片 → 權限不足 ❌
• 如果指令無法使用 → 缺少指令權限 ⚠️
            """,
            inline=False
        )
        
        embed.set_footer(
            text="💡 提示：機器人權限問題是圖片無法顯示的最常見原因"
        )
        
        return embed

class PermissionTestBot(commands.Bot):
    """權限測試機器人"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
    
    async def on_ready(self):
        """機器人啟動時的事件"""
        print(f'🤖 {self.user} 已連線成功！')
        print(f'📡 機器人 ID: {self.user.id}')
        
        # 檢查機器人所在的伺服器
        guild_count = len(self.guilds)
        print(f'🏰 機器人已加入 {guild_count} 個伺服器')
        
        for guild in self.guilds:
            print(f'   • {guild.name} (ID: {guild.id})')
            await self.check_guild_permissions(guild)
    
    async def check_guild_permissions(self, guild):
        """檢查特定伺服器的權限"""
        try:
            bot_member = guild.get_member(self.user.id)
            if not bot_member:
                print(f'   ❌ 無法在 {guild.name} 中找到機器人成員資訊')
                return
            
            # 檢查機器人的權限
            permissions = bot_member.guild_permissions
            required_perms = BotPermissionChecker.check_required_permissions()
            
            print(f'\n🔍 檢查 {guild.name} 中的機器人權限:')
            
            essential_missing = []
            recommended_missing = []
            
            # 檢查必要權限
            essential_perms = ['send_messages', 'embed_links', 'use_application_commands']
            for perm in essential_perms:
                has_perm = getattr(permissions, perm, False)
                status = '✅' if has_perm else '❌'
                print(f'   {status} {required_perms[perm]}: {has_perm}')
                if not has_perm:
                    essential_missing.append(perm)
            
            # 檢查建議權限
            recommended_perms = ['attach_files', 'read_message_history', 'use_external_emojis', 'add_reactions']
            for perm in recommended_perms:
                has_perm = getattr(permissions, perm, False)
                status = '✅' if has_perm else '⚠️'
                print(f'   {status} {required_perms[perm]}: {has_perm}')
                if not has_perm:
                    recommended_missing.append(perm)
            
            # 特別檢查管理員權限
            is_admin = permissions.administrator
            print(f'   {"✅" if is_admin else "ℹ️"} 管理員權限: {is_admin}')
            
            # 總結
            if essential_missing:
                print(f'   🚨 缺少必要權限: {", ".join(essential_missing)}')
                print(f'   💡 圖片可能無法正常顯示！')
            elif recommended_missing:
                print(f'   ⚠️ 缺少建議權限: {", ".join(recommended_missing)}')
                print(f'   💡 部分功能可能受限')
            else:
                print(f'   ✅ 所有權限都已具備！')
            
        except Exception as e:
            print(f'   ❌ 檢查權限時發生錯誤: {str(e)}')

def create_permission_setup_guide():
    """創建權限設定指南"""
    guide = """
🔐 Discord 機器人圖片嵌入權限設定指南
==========================================

如果機器人無法顯示圖片，請按照以下步驟檢查權限：

📋 必要權限清單：
1. ✅ 發送訊息 (Send Messages)
2. ⭐ 嵌入連結 (Embed Links) - 最重要！
3. ✅ 使用斜線指令 (Use Application Commands)

🔧 權限設定步驟：

方法一：透過伺服器設定
1. 開啟 Discord 桌面版或網頁版
2. 點擊伺服器名稱 → 「伺服器設定」
3. 在左側選單點擊「角色」
4. 找到機器人的角色（通常與機器人同名）
5. 確保以下權限已勾選：
   - ✅ 檢視頻道
   - ✅ 發送訊息
   - ⭐ 嵌入連結 (Embed Links)
   - ✅ 使用斜線指令
   - ✅ 附加檔案（建議）
   - ✅ 讀取訊息記錄（建議）

方法二：給予管理員權限（簡單但權限較大）
1. 同樣進入「角色」設定
2. 找到機器人角色
3. 勾選「管理員」權限
4. 這會給予機器人所有權限

🧪 測試方法：
1. 使用 `/water_cameras` 指令
2. 如果能看到監視器圖片 → 權限設定成功 ✅
3. 如果只看到文字沒有圖片 → 需要檢查「嵌入連結」權限 ❌

⚠️ 常見問題：
• 問題：指令無法使用
  解決：檢查「使用斜線指令」權限

• 問題：有文字但無圖片
  解決：檢查「嵌入連結」權限

• 問題：機器人無回應
  解決：檢查「發送訊息」和「檢視頻道」權限

📱 手機版設定：
由於手機版 Discord 功能限制，建議使用電腦版進行權限設定。

💡 提示：
- 權限變更後可能需要幾分鐘才會生效
- 如果仍有問題，嘗試重新邀請機器人並確保邀請時勾選了所需權限

🆘 如果問題持續：
請確認：
1. 機器人確實在線上（顯示綠色狀態）
2. 網路連線正常
3. Discord 應用程式是最新版本
4. 嘗試重新啟動 Discord 應用程式
"""
    
    # 保存指南
    with open('discord_permission_setup_guide.txt', 'w', encoding='utf-8') as f:
        f.write(guide)
    
    return guide

def main():
    """主函數"""
    print("🔐 Discord 機器人權限檢查工具")
    print("=" * 50)
    
    # 創建權限設定指南
    guide = create_permission_setup_guide()
    print("📋 權限設定指南已創建: discord_permission_setup_guide.txt")
    
    # 顯示簡化的檢查清單
    print("\n🔍 權限檢查清單：")
    print("1. ⭐ 嵌入連結 (Embed Links) - 圖片顯示必需")
    print("2. ✅ 發送訊息 (Send Messages)")
    print("3. ✅ 使用斜線指令 (Use Application Commands)")
    print("4. 💡 建議：直接給予管理員權限以避免權限問題")
    
    print("\n🧪 測試方法：")
    print("使用 /water_cameras 指令，如果能看到圖片就代表權限設定正確")
    
    print("\n📖 完整的設定指南請參考：discord_permission_setup_guide.txt")

if __name__ == "__main__":
    main()
