import requests
import json

# 快速檢查水利防災監控影像 API
url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"

try:
    print("檢查 API...")
    r = requests.get(url, timeout=30)
    if r.status_code == 200:
        content = r.text[1:] if r.text.startswith('\ufeff') else r.text
        data = json.loads(content)
        print(f"資料筆數: {len(data)}")
        
        if data:
            first = data[0]
            print("\n所有欄位:")
            for k in sorted(first.keys()):
                v = first[k]
                if v:
                    print(f"{k}: {str(v)[:60]}...")
                else:
                    print(f"{k}: (空值)")
                    
            # 檢查是否有特定的 URL 格式
            print("\n檢查可能的影像 URL 模式:")
            for k, v in first.items():
                if v and ('http' in str(v).lower() or '.jpg' in str(v).lower() or '.png' in str(v).lower()):
                    print(f"發現 URL: {k} = {v}")
    else:
        print(f"API 失敗: {r.status_code}")
except Exception as e:
    print(f"錯誤: {e}")

print("檢查完成")
