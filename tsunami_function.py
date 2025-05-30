from typing import Any, Dict, Optional
import datetime
import logging

# 設定 logger
logger = logging.getLogger(__name__)

# 這個函數應該是一個獨立的工具函數，或者需要被整合到 InfoCommands 類別中
# 目前移除 self 參數，使其成為獨立函數
async def fetch_tsunami_data_standalone(api_auth: str, tsunami_cache=None, tsunami_cache_time=0, fetch_with_retry_func=None) -> Optional[Dict[str, Any]]:
        """從氣象局取得最新海嘯資料 (使用非同步請求)"""
        current_time = datetime.datetime.now().timestamp()
        
        logger.info("開始獲取海嘯資料")
        
        # 如果快取資料未過期（5分鐘內），直接返回快取
        if (self.tsunami_cache and 
            current_time - self.tsunami_cache_time < 300):
            logger.info("使用快取的海嘯資料")
            return self.tsunami_cache

        try:
            # 使用海嘯資料API端點
            url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0014-001?Authorization={self.api_auth}"
            
            logger.info(f"正在獲取海嘯資料，URL: {url}")
            
            # 使用非同步請求獲取資料
            data = await self.fetch_with_retry(url, timeout=30, max_retries=3)
            
            if data and isinstance(data, dict):
                # 驗證資料結構
                if 'success' in data and (data['success'] == 'true' or data['success'] is True):
                    # 記錄完整的資料結構，以便調試
                    logger.info(f"海嘯API返回的資料結構: {str(data.keys())}")
                    
                    # 更新快取
                    self.tsunami_cache = data
                    self.tsunami_cache_time = current_time
                    logger.info("成功獲取並更新海嘯資料快取")
                    
                    return data
                else:
                    logger.error(f"海嘯API請求不成功: {data}")
            else:
                logger.error(f"獲取到的海嘯資料格式不正確: {data}")
                
            # 如果請求失敗，檢查是否有快取資料可用
            if self.tsunami_cache:
                logger.warning("使用過期的海嘯資料快取")
                return self.tsunami_cache
                
            return None
                
        except Exception as e:
            logger.error(f"獲取海嘯資料時發生錯誤: {str(e)}")
            
            # 如果發生錯誤，檢查是否有快取資料可用
            if self.tsunami_cache:
                logger.info("發生錯誤，使用海嘯快取資料")
                return self.tsunami_cache
                
            return None
