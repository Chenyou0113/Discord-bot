#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord 圖片嵌入最終診斷與修復
檢查圖片 URL 的有效性和 Discord 支援格式
"""

import asyncio
import aiohttp
import json
import ssl
import re
from urllib.parse import urljoin, urlparse
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageEmbedDiagnostic:
    """圖片嵌入診斷工具"""
    
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
    
    def validate_discord_image_url(self, url):
        """驗證 URL 是否符合 Discord 圖片嵌入要求"""
        if not url:
            return False, "URL 為空"
        
        # Discord 支援的圖片格式
        supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        
        # 檢查 URL 格式
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "URL 格式不正確"
        except Exception as e:
            return False, f"URL 解析錯誤: {str(e)}"
        
        # 檢查是否為 HTTPS (Discord 偏好)
        if not url.startswith('https://'):
            return False, "Discord 偏好 HTTPS 協議"
        
        # 檢查檔案副檔名
        url_lower = url.lower()
        has_image_ext = any(url_lower.endswith(fmt) for fmt in supported_formats)
        
        if not has_image_ext:
            # 如果沒有明確副檔名，檢查是否為動態圖片 URL
            if 'image' in url_lower or 'img' in url_lower or 'photo' in url_lower:
                return True, "可能的動態圖片 URL"
            else:
                return False, f"不支援的圖片格式，支援: {supported_formats}"
        
        return True, "URL 格式符合 Discord 要求"
    
    async def test_image_accessibility(self, url):
        """測試圖片 URL 是否可訪問"""
        try:
            async with self.session.head(url) as response:
                status = response.status
                content_type = response.headers.get('Content-Type', '').lower()
                content_length = response.headers.get('Content-Length', 'unknown')
                
                # 檢查狀態碼
                if status == 200:
                    # 檢查 Content-Type
                    image_types = ['image/', 'application/octet-stream']
                    is_image = any(img_type in content_type for img_type in image_types)
                    
                    return {
                        'accessible': True,
                        'status': status,
                        'content_type': content_type,
                        'content_length': content_length,
                        'is_image': is_image,
                        'message': f"可訪問 - 狀態: {status}, 類型: {content_type}"
                    }
                else:
                    return {
                        'accessible': False,
                        'status': status,
                        'content_type': content_type,
                        'message': f"HTTP 錯誤: {status}"
                    }
                    
        except asyncio.TimeoutError:
            return {
                'accessible': False,
                'status': 'timeout',
                'message': "連線逾時"
            }
        except Exception as e:
            return {
                'accessible': False,
                'status': 'error',
                'message': f"連線錯誤: {str(e)}"
            }
    
    async def get_water_camera_sample(self):
        """獲取水利監視器資料樣本"""
        api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
        
        try:
            async with self.session.get(api_url) as response:
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
            logger.error(f"獲取水利監視器資料失敗: {str(e)}")
            return None
    
    def process_image_url(self, url):
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
                    if self.is_valid_url_format(test_url):
                        processed_url = test_url
                        break
        
        # 確保 URL 格式正確
        if self.is_valid_url_format(processed_url):
            return processed_url
        
        return None
    
    def is_valid_url_format(self, url):
        """檢查 URL 格式是否有效"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

async def run_comprehensive_diagnosis():
    """執行全面的圖片嵌入診斷"""
    print("🔍 開始 Discord 圖片嵌入診斷...")
    
    async with ImageEmbedDiagnostic() as diagnostic:
        # 1. 獲取水利監視器資料
        print("\n📡 獲取水利監視器資料...")
        camera_data = await diagnostic.get_water_camera_sample()
        
        if not camera_data:
            print("❌ 無法獲取水利監視器資料")
            return
        
        print(f"✅ 成功獲取 {len(camera_data)} 筆監視器資料")
        
        # 2. 分析前 10 個監視器的圖片 URL
        print("\n🔍 分析監視器圖片 URL...")
        
        test_results = []
        for i, camera in enumerate(camera_data[:10]):
            station_name = camera.get('StationName', f'監視器_{i+1}')
            original_url = camera.get('ImageURL', '')
            
            print(f"\n📸 {i+1}. {station_name}")
            print(f"   原始 URL: {original_url}")
            
            # 處理 URL
            processed_url = diagnostic.process_image_url(original_url)
            print(f"   處理後 URL: {processed_url}")
            
            if processed_url:
                # Discord 格式驗證
                is_valid, validation_msg = diagnostic.validate_discord_image_url(processed_url)
                print(f"   Discord 驗證: {'✅' if is_valid else '❌'} {validation_msg}")
                
                # 可訪問性測試
                access_result = await diagnostic.test_image_accessibility(processed_url)
                print(f"   可訪問性: {'✅' if access_result['accessible'] else '❌'} {access_result['message']}")
                
                test_results.append({
                    'station_name': station_name,
                    'original_url': original_url,
                    'processed_url': processed_url,
                    'discord_valid': is_valid,
                    'validation_message': validation_msg,
                    'accessible': access_result['accessible'],
                    'access_message': access_result['message'],
                    'content_type': access_result.get('content_type', 'unknown')
                })
            else:
                print(f"   ❌ URL 處理失敗")
                test_results.append({
                    'station_name': station_name,
                    'original_url': original_url,
                    'processed_url': None,
                    'discord_valid': False,
                    'validation_message': 'URL 處理失敗',
                    'accessible': False,
                    'access_message': 'URL 無效'
                })
        
        # 3. 統計結果
        print("\n📊 診斷結果統計:")
        total = len(test_results)
        discord_valid = sum(1 for r in test_results if r['discord_valid'])
        accessible = sum(1 for r in test_results if r['accessible'])
        both_valid = sum(1 for r in test_results if r['discord_valid'] and r['accessible'])
        
        print(f"   總測試數量: {total}")
        print(f"   Discord 格式符合: {discord_valid}/{total} ({discord_valid/total*100:.1f}%)")
        print(f"   URL 可訪問: {accessible}/{total} ({accessible/total*100:.1f}%)")
        print(f"   完全可用: {both_valid}/{total} ({both_valid/total*100:.1f}%)")
        
        # 4. 找出可用的圖片 URL
        valid_urls = [r for r in test_results if r['discord_valid'] and r['accessible']]
        
        if valid_urls:
            print(f"\n✅ 找到 {len(valid_urls)} 個可用的圖片 URL:")
            for i, result in enumerate(valid_urls[:3]):  # 只顯示前3個
                print(f"   {i+1}. {result['station_name']}")
                print(f"      URL: {result['processed_url']}")
                print(f"      類型: {result['content_type']}")
        else:
            print("\n❌ 沒有找到完全可用的圖片 URL")
        
        # 5. 保存診斷報告
        report_data = {
            'timestamp': str(datetime.now()),
            'total_tested': total,
            'discord_valid_count': discord_valid,
            'accessible_count': accessible,
            'fully_valid_count': both_valid,
            'test_results': test_results,
            'valid_sample_urls': [r['processed_url'] for r in valid_urls[:5]]
        }
        
        with open('discord_image_diagnosis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📋 診斷報告已保存至: discord_image_diagnosis_report.json")
        
        # 6. 提供修復建議
        print("\n🔧 修復建議:")
        if both_valid == 0:
            print("   1. 所有測試的圖片 URL 都無法在 Discord 中使用")
            print("   2. 可能的原因:")
            print("      - API 提供的圖片 URL 格式不被 Discord 支援")
            print("      - 圖片服務器設定 CORS 限制")
            print("      - 圖片 URL 需要特殊認證")
            print("   3. 建議解決方案:")
            print("      - 使用 Discord 文件上傳功能")
            print("      - 建立圖片代理服務")
            print("      - 使用外部圖片托管服務")
        elif both_valid < total * 0.5:
            print("   1. 部分圖片 URL 可用，但成功率偏低")
            print("   2. 建議改善 URL 處理邏輯")
            print("   3. 增加錯誤處理和備用方案")
        else:
            print("   1. 大部分圖片 URL 可用")
            print("   2. 建議測試實際的 Discord 嵌入效果")

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(run_comprehensive_diagnosis())
