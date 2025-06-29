#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord 圖片嵌入實戰測試
模擬實際的 Discord 機器人環境測試圖片嵌入
"""

import asyncio
import aiohttp
import json
import ssl
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiscordImageEmbedTest:
    """Discord 圖片嵌入測試工具"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        # 忽略 SSL 證書驗證
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_water_disaster_images(self):
        """取得水利防災影像資料"""
        try:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
            
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    # 處理 UTF-8 BOM 問題
                    text = await response.text()
                    if text.startswith('\ufeff'):
                        text = text[1:]
                    
                    try:
                        data = json.loads(text)
                        return data
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON 解析錯誤: {str(e)}")
                        return None
                else:
                    logger.error(f"API 請求失敗: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"獲取水利防災影像資料失敗: {str(e)}")
            return None

    def format_water_image_info(self, data):
        """格式化水利影像資訊 (與機器人相同邏輯)"""
        try:
            # 提取水利防災影像的各個欄位
            station_name = data.get('StationName', '未知監控點')
            location = data.get('StationLocation', '未知位置')
            
            # 提取河川名稱
            river_name = data.get('RiverName', '')
            if not river_name or river_name == '':
                river_name = '未指定河川'
            
            # 提取影像相關資訊
            image_url = data.get('ImageURL', '')
            
            # 狀態判斷
            status = "🟢 正常運作" if image_url and image_url != '' else "🔴 影像異常"
            
            return {
                'station_name': station_name,
                'location': location,
                'river': river_name,
                'image_url': image_url,
                'status': status,
                'camera_name': data.get('CameraName', '主攝影機')
            }
        except Exception as e:
            logger.error(f"格式化水利影像資訊時發生錯誤: {str(e)}")
            return None

    def _process_image_url(self, url):
        """處理圖片 URL (與機器人相同邏輯)"""
        if not url or url == 'N/A':
            return None
        
        processed_url = url.strip()
        
        # 多重 URL 格式處理
        if not processed_url.startswith(('http://', 'https://')):
            if processed_url.startswith('//'):
                processed_url = 'https:' + processed_url
            elif processed_url.startswith('/'):
                processed_url = 'https://opendata.wra.gov.tw' + processed_url
            else:
                # 嘗試不同的基礎 URL
                possible_bases = [
                    'https://opendata.wra.gov.tw/',
                    'https://fhy.wra.gov.tw/',
                    'https://www.wra.gov.tw/'
                ]
                for base in possible_bases:
                    test_url = base + processed_url
                    if self._is_valid_url_format(test_url):
                        processed_url = test_url
                        break
        
        # 確保 URL 格式正確
        if self._is_valid_url_format(processed_url):
            return processed_url
        
        return None

    def _is_valid_url_format(self, url):
        """檢查 URL 格式是否有效"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

    def create_mock_discord_embed(self, index: int, cameras: list, location: str):
        """創建模擬 Discord embed (與機器人相同邏輯)"""
        if not (0 <= index < len(cameras)):
            return None
        
        data = cameras[index]
        info = self.format_water_image_info(data)
        
        if not info:
            return None
        
        # 模擬 Discord Embed 結構
        embed_data = {
            'title': f"📸 {info['station_name']}",
            'description': f"📍 **位置**: {info['location']}\n"
                          f"🌊 **河川**: {info['river']}\n"
                          f"📡 **狀態**: {info['status']}",
            'color': 3447003,  # Discord.Color.blue()
            'fields': [],
            'image': None,
            'thumbnail': None,
            'footer': {
                'text': f"🌊 {location}地區水利監視器 • 經濟部水利署 • 即時監控影像",
                'icon_url': None
            }
        }
        
        # 增強的圖片嵌入邏輯
        image_url = info.get('image_url', '')
        image_embedded = False
        
        if image_url and image_url != 'N/A' and image_url.strip():
            try:
                # 多重 URL 格式修復
                processed_url = self._process_image_url(image_url)
                
                if processed_url:
                    # 嵌入圖片到 embed 中
                    embed_data['image'] = {'url': processed_url}
                    image_embedded = True
                    
                    # 添加圖片資訊和預覽
                    embed_data['fields'].append({
                        'name': "📸 即時影像",
                        'value': f"🎥 **監控點**: {info['station_name']}\n"
                                f"📷 **攝影機**: {info.get('camera_name', '主攝影機')}\n"
                                f"🔗 [原始影像連結]({processed_url})\n"
                                f"🕐 **更新**: 即時監控",
                        'inline': False
                    })
                    
                    # 添加縮圖預覽 (如果主圖無法顯示)
                    embed_data['thumbnail'] = {'url': processed_url}
                    embed_data['footer']['icon_url'] = "https://opendata.wra.gov.tw/favicon.ico"
                    
                    logger.info(f"成功嵌入監視器圖片: {info['station_name']} - {processed_url}")
                    
            except Exception as e:
                logger.error(f"嵌入影像時發生錯誤: {str(e)}")
        
        if not image_embedded:
            # 如果沒有可用影像，顯示相關訊息
            embed_data['fields'].append({
                'name': "⚠️ 影像狀態",
                'value': "目前暫無可用的即時影像\n請稍後重新查詢或選擇其他監控點",
                'inline': False
            })
        
        return embed_data, image_embedded

    async def test_discord_embed_functionality(self):
        """測試 Discord embed 功能"""
        print("🧪 測試 Discord 圖片嵌入功能...")
        
        # 獲取水利監視器資料
        cameras = await self.get_water_disaster_images()
        if not cameras:
            print("❌ 無法獲取監視器資料")
            return
        
        print(f"✅ 成功獲取 {len(cameras)} 筆監視器資料")
        
        # 測試前 5 個監視器的 embed 創建
        test_results = []
        
        for i in range(min(5, len(cameras))):
            camera = cameras[i]
            station_name = camera.get('StationName', f'監視器_{i+1}')
            
            print(f"\n🧪 測試 {i+1}: {station_name}")
            
            try:
                embed_data, image_embedded = self.create_mock_discord_embed(i, cameras, "測試地區")
                
                if embed_data:
                    # 檢查 embed 結構
                    has_title = bool(embed_data.get('title'))
                    has_description = bool(embed_data.get('description'))
                    has_image = bool(embed_data.get('image', {}).get('url'))
                    has_thumbnail = bool(embed_data.get('thumbnail', {}).get('url'))
                    has_fields = len(embed_data.get('fields', [])) > 0
                    
                    result = {
                        'station_name': station_name,
                        'embed_created': True,
                        'image_embedded': image_embedded,
                        'has_title': has_title,
                        'has_description': has_description,
                        'has_image': has_image,
                        'has_thumbnail': has_thumbnail,
                        'has_fields': has_fields,
                        'image_url': embed_data.get('image', {}).get('url', 'N/A')
                    }
                    
                    print(f"   ✅ Embed 創建成功")
                    print(f"   📸 圖片嵌入: {'✅' if image_embedded else '❌'}")
                    print(f"   🖼️ 主圖片: {'✅' if has_image else '❌'}")
                    print(f"   🔗 縮圖: {'✅' if has_thumbnail else '❌'}")
                    if has_image:
                        print(f"   🌐 圖片 URL: {embed_data['image']['url'][:100]}...")
                    
                else:
                    result = {
                        'station_name': station_name,
                        'embed_created': False,
                        'image_embedded': False,
                        'error': 'Embed 創建失敗'
                    }
                    print(f"   ❌ Embed 創建失敗")
                
                test_results.append(result)
                
            except Exception as e:
                print(f"   ❌ 測試失敗: {str(e)}")
                test_results.append({
                    'station_name': station_name,
                    'embed_created': False,
                    'image_embedded': False,
                    'error': str(e)
                })
        
        # 統計結果
        print(f"\n📊 測試結果統計:")
        total = len(test_results)
        embed_success = sum(1 for r in test_results if r.get('embed_created', False))
        image_success = sum(1 for r in test_results if r.get('image_embedded', False))
        
        print(f"   總測試數量: {total}")
        print(f"   Embed 創建成功: {embed_success}/{total} ({embed_success/total*100:.1f}%)")
        print(f"   圖片嵌入成功: {image_success}/{total} ({image_success/total*100:.1f}%)")
        
        # 保存測試報告
        report_data = {
            'timestamp': str(datetime.now()),
            'test_type': 'Discord Embed 功能測試',
            'total_tested': total,
            'embed_success_count': embed_success,
            'image_embed_success_count': image_success,
            'test_results': test_results
        }
        
        with open('discord_embed_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📋 測試報告已保存至: discord_embed_test_report.json")
        
        # 結論和建議
        print(f"\n🔍 測試結論:")
        if image_success == total:
            print("   ✅ 所有監視器的圖片嵌入功能都正常工作")
            print("   ✅ Discord embed 結構完整")
            print("   💡 機器人的圖片嵌入邏輯沒有問題")
            print("   🚨 如果 Discord 中仍看不到圖片，可能的原因：")
            print("      1. Discord 快取問題 - 嘗試重啟 Discord 應用程式")
            print("      2. 網路連線問題 - 檢查網路設定")
            print("      3. Discord 伺服器設定 - 檢查伺服器權限")
            print("      4. 機器人權限不足 - 確認機器人有嵌入連結權限")
        elif image_success > 0:
            print(f"   ⚠️ 部分監視器圖片嵌入成功 ({image_success}/{total})")
            print("   💡 建議檢查失敗的監視器資料")
        else:
            print("   ❌ 所有監視器圖片嵌入都失敗")
            print("   💡 需要進一步檢查圖片 URL 處理邏輯")

async def main():
    """主函數"""
    async with DiscordImageEmbedTest() as tester:
        await tester.test_discord_embed_functionality()

if __name__ == "__main__":
    asyncio.run(main())
