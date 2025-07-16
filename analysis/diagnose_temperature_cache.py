#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷溫度分布圖快取問題
檢查可用的即時溫度分布圖URL
"""

import aiohttp
import asyncio
import ssl
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_temperature_image_urls():
    """檢查各種溫度分布圖URL"""
    
    # 設定 SSL 上下文
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    # 各種可能的溫度分布圖URL
    urls_to_test = [
        # 原本使用的URL
        "https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0038-001.jpg",
        
        # 可能的即時圖片URL
        "https://www.cwa.gov.tw/Data/temperature/temp_Taiwan.png",
        "https://www.cwa.gov.tw/Data/temperature/temp_Taiwan.jpg",
        "https://www.cwa.gov.tw/V8/assets/img/weather_img/temp_Taiwan.png",
        
        # 氣象署觀測圖
        "https://www.cwa.gov.tw/V8/assets/img/weather_img/obs/TEMP.png",
        "https://www.cwa.gov.tw/V8/assets/img/weather_img/obs/TEMP.jpg",
        
        # 可能的AWS S3 URL變體
        "https://cwaopendata.s3.ap-northeast-1.amazonaws.com/MSC/O-A0038-001.jpg",
        "https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0038-002.jpg",
        
        # 其他可能的格式
        "https://www.cwa.gov.tw/Data/js_typhoon/obs_temp.png",
        "https://www.cwa.gov.tw/Data/js_typhoon/temp_map.png",
    ]
    
    print("=== 檢查溫度分布圖URL可用性 ===")
    
    available_urls = []
    
    async with aiohttp.ClientSession(connector=connector) as session:
        for url in urls_to_test:
            try:
                async with session.head(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    status = response.status
                    content_type = response.headers.get('content-type', '')
                    last_modified = response.headers.get('last-modified', '')
                    
                    if status == 200:
                        print(f"✅ {url}")
                        print(f"   Content-Type: {content_type}")
                        print(f"   Last-Modified: {last_modified}")
                        available_urls.append({
                            'url': url,
                            'content_type': content_type,
                            'last_modified': last_modified
                        })
                    else:
                        print(f"❌ {url} (狀態: {status})")
                        
            except Exception as e:
                print(f"❌ {url} (錯誤: {e})")
    
    print(f"\n找到 {len(available_urls)} 個可用的圖片URL")
    
    return available_urls

def generate_timestamped_urls():
    """生成帶時間戳的URL來避免快取"""
    base_urls = [
        "https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0038-001.jpg",
        "https://www.cwa.gov.tw/V8/assets/img/weather_img/obs/TEMP.png",
    ]
    
    timestamp = int(datetime.now().timestamp())
    
    print("\n=== 帶時間戳的URL（避免快取）===")
    timestamped_urls = []
    
    for base_url in base_urls:
        timestamped_url = f"{base_url}?t={timestamp}"
        timestamped_urls.append(timestamped_url)
        print(f"🕐 {timestamped_url}")
    
    return timestamped_urls

async def check_data_freshness():
    """檢查資料新鮮度"""
    print("\n=== 檢查溫度資料API新鮮度 ===")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    api_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0038-001"
    
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # 檢查資料時間
                    records = data.get('records', {})
                    dataset = records.get('Station', [])
                    
                    if dataset:
                        first_station = dataset[0]
                        obs_time = first_station.get('ObsTime', {})
                        datetime_str = obs_time.get('DateTime', 'N/A')
                        
                        print(f"✅ API 連接成功")
                        print(f"📅 最新觀測時間: {datetime_str}")
                        print(f"📊 測站數量: {len(dataset)}")
                        
                        return datetime_str
                    else:
                        print("❌ 沒有找到測站資料")
                        return None
                else:
                    print(f"❌ API 請求失敗: {response.status}")
                    return None
                    
    except Exception as e:
        print(f"❌ 檢查API時發生錯誤: {e}")
        return None

async def main():
    print("🔍 開始診斷溫度分布圖快取問題")
    print("=" * 50)
    
    # 檢查圖片URL可用性
    available_urls = await check_temperature_image_urls()
    
    # 生成帶時間戳的URL
    timestamped_urls = generate_timestamped_urls()
    
    # 檢查資料新鮮度
    latest_time = await check_data_freshness()
    
    print("\n" + "=" * 50)
    print("📋 診斷結果總結")
    print("=" * 50)
    
    if available_urls:
        print("✅ 找到可用的圖片URL:")
        for url_info in available_urls:
            print(f"   • {url_info['url']}")
    else:
        print("❌ 沒有找到可用的圖片URL")
    
    print(f"\n🕐 建議使用帶時間戳的URL避免快取問題")
    print(f"📊 API資料時間: {latest_time if latest_time else '無法取得'}")
    
    # 提供修復建議
    print(f"\n💡 修復建議:")
    print(f"1. 在圖片URL後加上時間戳參數避免快取")
    print(f"2. 使用多個備用URL提高可用性")
    print(f"3. 定期檢查圖片URL的有效性")

if __name__ == "__main__":
    asyncio.run(main())
