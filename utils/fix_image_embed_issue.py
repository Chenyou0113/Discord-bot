#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水利監視器圖片嵌入修復
解決圖片不顯示的問題
"""

import asyncio
import aiohttp
import sys

async def test_image_accessibility():
    """測試圖片 URL 的可存取性"""
    
    print("🔍 測試圖片 URL 可存取性")
    print("=" * 60)
    
    # 測試一些實際的圖片 URL
    test_urls = [
        "https://alerts.ncdr.nat.gov.tw/HPWRI/2024/202409/20240904/10550011_20240904_0816.jpg",
        "https://fhy.wra.gov.tw/RealtimeRainfall_WRA.aspx",
        "https://www.wra.gov.tw/cp.aspx?n=9017",
        "https://httpbin.org/image/jpeg",  # 測試 URL
        "https://picsum.photos/400/300"   # 測試圖片服務
    ]
    
    async with aiohttp.ClientSession() as session:
        for i, url in enumerate(test_urls, 1):
            print(f"\n{i}. 測試: {url}")
            try:
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    print(f"   狀態碼: {response.status}")
                    content_type = response.headers.get('content-type', 'unknown')
                    print(f"   內容類型: {content_type}")
                    
                    if response.status == 200:
                        if 'image' in content_type:
                            print(f"   ✅ 可存取的圖片")
                        else:
                            print(f"   ⚠️ 可存取但不是圖片")
                    else:
                        print(f"   ❌ 無法存取")
                        
            except asyncio.TimeoutError:
                print(f"   ⏰ 連線超時")
            except Exception as e:
                print(f"   ❌ 錯誤: {e}")

def create_image_fallback_solution():
    """創建圖片顯示的備用方案"""
    
    print("\n💡 創建圖片顯示備用方案")
    print("=" * 60)
    
    fallback_code = '''
    async def _create_water_camera_embed_with_fallback(self, camera_data):
        """創建水利防災監視器 Embed（附備用方案）"""
        info = self._format_water_image_info(camera_data)
        
        embed = discord.Embed(
            title=f"📸 {self.search_term} 地區監控點" if self.search_term else "📸 水利防災監控點",
            description=f"**{info['station_name']}**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📍 位置資訊",
            value=f"🏙️ 縣市：{info['county']}\\n"
                  f"🏘️ 區域：{info['district']}\\n"
                  f"📍 詳細：{info['address']}",
            inline=True
        )
        
        embed.add_field(
            name="📊 技術資訊",
            value=f"🆔 ID：{info['station_id']}\\n"
                  f"📡 來源：{info['source']}\\n"
                  f"📸 狀態：{'✅ 有影像' if info['image_url'] != 'N/A' else '❌ 無影像'}",
            inline=True
        )
        
        # 嘗試添加影像，如果失敗則提供替代方案
        image_added = False
        if info['image_url'] and info['image_url'] != 'N/A':
            processed_url = self._process_and_validate_image_url(info['image_url'])
            if processed_url and processed_url != 'N/A':
                try:
                    embed.set_image(url=processed_url)
                    image_added = True
                except Exception as e:
                    print(f"設定圖片失敗: {e}")
        
        # 如果圖片無法嵌入，提供替代資訊
        if not image_added:
            if info['image_url'] and info['image_url'] != 'N/A':
                processed_url = self._process_and_validate_image_url(info['image_url'])
                embed.add_field(
                    name="🔗 影像連結",
                    value=f"[點擊查看監控影像]({processed_url})",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📷 影像狀態",
                    value="目前暫無可用影像",
                    inline=False
                )
        
        embed.set_footer(text=f"監控點 {self.current_index + 1}/{self.total_cameras} | 使用按鈕切換")
        
        return embed
    '''
    
    print("建議的修復代碼:")
    print(fallback_code)

async def main():
    """主函數"""
    
    print("🚀 水利監視器圖片嵌入問題修復")
    print("=" * 80)
    
    # 測試圖片可存取性
    await test_image_accessibility()
    
    # 提供備用方案
    create_image_fallback_solution()
    
    print("\n" + "=" * 80)
    print("📋 修復建議:")
    print("1. 圖片 URL 可能已過期或需要認證")
    print("2. Discord 可能無法存取某些政府網站的圖片")
    print("3. 建議實作備用方案：")
    print("   • 當圖片無法嵌入時，提供連結讓用戶點擊查看")
    print("   • 顯示 '目前暫無可用影像' 訊息")
    print("   • 保持按鈕功能正常運作")
    
    return True

if __name__ == "__main__":
    asyncio.run(main())
