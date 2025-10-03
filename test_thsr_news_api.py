"""
測試高鐵新聞 API 資料
檢查 NewsURL 欄位是否存在
"""

import asyncio
import aiohttp
import json
import sys
import os

# 加入路徑以導入 bot 的程式碼
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cogs.info_commands_fixed_v4_clean import InfoCommands

async def test_thsr_news():
    print("=== 測試高鐵新聞 API ===\n")
    
    # 建立 InfoCommands 實例
    info_commands = InfoCommands(None)
    
    try:
        # 獲取高鐵新聞
        news_list = await info_commands.fetch_thsr_news()
        
        if news_list is None:
            print("❌ 無法獲取高鐵新聞資料")
            return
        
        if len(news_list) == 0:
            print("⚠️ 高鐵新聞資料為空")
            return
        
        print(f"✅ 獲取到 {len(news_list)} 則高鐵新聞")
        
        # 檢查前 3 則新聞的欄位
        for i, news in enumerate(news_list[:3], 1):
            print(f"\n📰 第 {i} 則新聞:")
            print(f"  完整資料: {json.dumps(news, ensure_ascii=False, indent=2)}")
            
            # 檢查各種可能的 URL 欄位
            url_fields = ['NewsURL', 'Link', 'Url', 'URL', 'WebsiteURL', 'DetailURL']
            url_found = False
            
            for field in url_fields:
                if field in news and news[field]:
                    print(f"  ✅ 找到連結欄位 '{field}': {news[field]}")
                    url_found = True
                    break
            
            if not url_found:
                print(f"  ❌ 未找到有效的連結欄位")
                print(f"  可用欄位: {list(news.keys())}")
            
            # 檢查標題和內容
            title = news.get('Title', news.get('NewsTitle', '無標題'))
            description = news.get('Description', news.get('Content', news.get('NewsContent', '')))
            
            print(f"  標題: {title}")
            print(f"  內容長度: {len(description) if description else 0}")
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

# 執行測試
if __name__ == "__main__":
    asyncio.run(test_thsr_news())