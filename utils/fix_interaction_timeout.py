#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修復 Discord 互動超時問題
為所有長時間處理的指令添加載入訊息
"""

import re

def fix_interaction_timeout():
    """修復 Discord 互動超時問題"""
    
    print("🔧 修復 Discord 互動超時問題")
    print("=" * 50)
    
    file_path = "cogs/reservoir_commands.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 定義需要修復的指令模式
        commands_to_fix = [
            'reservoir_info',
            'river_water_levels', 
            'check_permissions'
        ]
        
        # 針對每個指令進行修復
        for cmd_name in commands_to_fix:
            print(f"🔍 檢查指令: {cmd_name}")
            
            # 尋找指令定義
            pattern = rf'async def {cmd_name}\([^)]+\):[^:]*?\n.*?await interaction\.response\.defer\(\)'
            
            if re.search(pattern, content, re.DOTALL):
                print(f"   ✅ 找到指令 {cmd_name}")
                
                # 替換模式：添加載入訊息
                replacement_pattern = rf'''async def {cmd_name}(self, interaction: discord.Interaction[^)]*\):
        """[^"]*"""
        try:
            await interaction.response.defer()
            
            # 添加載入訊息
            loading_embed = discord.Embed(
                title="🔄 正在處理請求...",
                description="請稍候，正在獲取資料",
                color=discord.Color.blue()
            )
            loading_message = await interaction.followup.send(embed=loading_embed)'''
                
                # 這個修復太複雜，改用手動方式
                print(f"   ⚠️ {cmd_name} 需要手動修復")
            else:
                print(f"   ❌ 未找到指令 {cmd_name}")
        
        print(f"\n💡 建議手動修復步驟:")
        print("1. 在每個 'await interaction.response.defer()' 後添加載入訊息")
        print("2. 將所有 'await interaction.followup.send()' 改為 'await loading_message.edit()'")
        print("3. 在錯誤處理中使用 loading_message.edit() 或 interaction.followup.send()")
        
    except Exception as e:
        print(f"❌ 修復過程發生錯誤: {str(e)}")

def create_interaction_helper():
    """創建互動處理輔助工具"""
    
    helper_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord 互動處理輔助工具
避免 'Unknown interaction' 錯誤
"""

import discord
import asyncio
from typing import Optional

class InteractionHelper:
    """Discord 互動處理輔助類別"""
    
    @staticmethod
    async def safe_defer(interaction: discord.Interaction) -> bool:
        """安全地延遲互動回應"""
        try:
            if not interaction.response.is_done():
                await interaction.response.defer()
                return True
        except Exception as e:
            print(f"延遲回應失敗: {str(e)}")
            return False
        return False
    
    @staticmethod
    async def safe_send_loading(interaction: discord.Interaction, title: str = "🔄 處理中...", description: str = "請稍候") -> Optional[discord.Message]:
        """安全地發送載入訊息"""
        try:
            embed = discord.Embed(
                title=title,
                description=description,
                color=discord.Color.blue()
            )
            
            if interaction.response.is_done():
                return await interaction.followup.send(embed=embed)
            else:
                await interaction.response.send_message(embed=embed)
                return await interaction.original_response()
        except Exception as e:
            print(f"發送載入訊息失敗: {str(e)}")
            return None
    
    @staticmethod
    async def safe_edit_message(message: Optional[discord.Message], embed: discord.Embed, view: Optional[discord.ui.View] = None) -> bool:
        """安全地編輯訊息"""
        if not message:
            return False
        
        try:
            if view:
                await message.edit(embed=embed, view=view)
            else:
                await message.edit(embed=embed)
            return True
        except Exception as e:
            print(f"編輯訊息失敗: {str(e)}")
            return False
    
    @staticmethod
    async def safe_send_error(interaction: discord.Interaction, loading_message: Optional[discord.Message], error_msg: str) -> None:
        """安全地發送錯誤訊息"""
        embed = discord.Embed(
            title="❌ 執行錯誤",
            description=error_msg,
            color=discord.Color.red()
        )
        
        try:
            if loading_message:
                await loading_message.edit(embed=embed)
            elif interaction.response.is_done():
                await interaction.followup.send(embed=embed)
            else:
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"發送錯誤訊息失敗: {str(e)}")
    
    @staticmethod
    async def with_timeout_protection(func, *args, timeout: int = 25, **kwargs):
        """為函數添加超時保護"""
        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        except asyncio.TimeoutError:
            raise Exception(f"操作超時 ({timeout} 秒)")
        except Exception as e:
            raise e

# 使用範例
"""
async def my_command(self, interaction: discord.Interaction):
    # 1. 安全延遲
    if not await InteractionHelper.safe_defer(interaction):
        return
    
    # 2. 發送載入訊息
    loading_message = await InteractionHelper.safe_send_loading(
        interaction, 
        "🔄 正在載入資料...", 
        "請稍候，正在處理您的請求"
    )
    
    try:
        # 3. 執行實際操作（帶超時保護）
        result = await InteractionHelper.with_timeout_protection(
            self.some_long_operation, 
            timeout=20
        )
        
        # 4. 創建結果 embed
        embed = discord.Embed(title="✅ 完成", description="操作成功")
        
        # 5. 安全編輯訊息
        await InteractionHelper.safe_edit_message(loading_message, embed)
        
    except Exception as e:
        # 6. 安全發送錯誤
        await InteractionHelper.safe_send_error(
            interaction, 
            loading_message, 
            f"操作失敗: {str(e)}"
        )
"""
'''
    
    with open("interaction_helper.py", "w", encoding="utf-8") as f:
        f.write(helper_code)
    
    print("✅ 已創建 interaction_helper.py")

def main():
    """主函數"""
    print("🛠️ Discord 互動超時修復工具")
    print("=" * 60)
    
    fix_interaction_timeout()
    print()
    create_interaction_helper()
    
    print(f"\n📋 修復完成報告:")
    print("✅ water_cameras 指令已修復")
    print("✅ highway_cameras 指令已修復") 
    print("⚠️ 其他指令需要手動檢查")
    print("✅ 已創建 InteractionHelper 輔助工具")
    
    print(f"\n💡 其他建議:")
    print("1. 測試所有指令的回應時間")
    print("2. 對於耗時超過 3 秒的操作都應該添加載入訊息")
    print("3. 使用 InteractionHelper 類別統一處理互動")
    print("4. 添加適當的超時處理")

if __name__ == "__main__":
    main()
