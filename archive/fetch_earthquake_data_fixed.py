"""
此函數為修復版的fetch_earthquake_data方法，用於解決地震資料結構不完整的問題。
"""
import datetime
import logging
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

async def fetch_earthquake_data(self, small_area: bool = False) -> Optional[Dict[str, Any]]:
    """從氣象局取得最新地震資料 (使用非同步請求)"""
    current_time = datetime.datetime.now().timestamp()
    cache_key = "small" if small_area else "normal"
    
    logger.info(f"開始獲取地震資料 (類型: {cache_key})")
    
    # 如果快取資料未過期（5分鐘內），直接返回快取
    if (cache_key in self.earthquake_cache and 
        current_time - self.cache_time < 300):
        logger.info(f"使用快取的地震資料 (類型: {cache_key})")
        logger.info(f"快取資料內容: {str(self.earthquake_cache[cache_key])[:200]}...")
        return self.earthquake_cache[cache_key]

    try:
        # 選擇適當的 API 端點
        if small_area:
            url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={self.api_auth}&limit=1"  # 小區域有感地震
        else:
            url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization={self.api_auth}&limit=1"  # 一般地震
        
        logger.info(f"正在獲取地震資料，URL: {url}")
        
        # 使用非同步請求獲取資料，並處理 SSL 相關錯誤
        try:
            data = await self.fetch_with_retry(url, timeout=30, max_retries=3)
            
            if data and isinstance(data, dict):
                # 驗證資料結構
                if 'success' in data and data['success'] == 'true':
                    if 'result' in data and 'records' in data['result'] and 'Earthquake' in data['result']['records'] and data['result']['records']['Earthquake']:
                        # 更新快取
                        self.earthquake_cache[cache_key] = data
                        self.cache_time = current_time
                        logger.info(f"成功獲取並更新地震資料快取，資料：{data}")
                        return data
                    else:
                        logger.error(f"地震資料結構不完整: {data}")
                else:
                    logger.error(f"API 請求不成功: {data}")
            else:
                logger.error(f"獲取到的資料格式不正確: {data}")
        
        except Exception as e:
            logger.error(f"地震資料請求失敗: {str(e)}")
            if 'SSL' in str(e):
                logger.warning("SSL 驗證錯誤，嘗試重新初始化連線")
                # 重新初始化工作階段並重試
                await self.init_aiohttp_session()
                try:
                    data = await self.fetch_with_retry(url, timeout=30, max_retries=3)
                    if data and isinstance(data, dict) and data.get('success') == 'true':
                        return data
                except Exception as retry_e:
                    logger.error(f"重試請求也失敗了: {str(retry_e)}")
        
        # 如果請求失敗，檢查是否有快取資料可用
        if cache_key in self.earthquake_cache:
            logger.warning("使用過期的地震資料快取")
            return self.earthquake_cache[cache_key]
        
        return None
            
    except Exception as e:
        logger.error(f"獲取地震資料時發生錯誤: {str(e)}")
        
        # 如果發生錯誤，檢查是否有快取資料可用
        if cache_key in self.earthquake_cache:
            logger.info("發生錯誤，使用地震快取資料")
            return self.earthquake_cache[cache_key]
        
        return None
