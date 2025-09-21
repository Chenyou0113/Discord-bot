import asyncio
import sys
import os
sys.path.append('.')

from cogs.info_commands_fixed_v4_clean import InfoCommands

async def test_tra_function():
    """測試台鐵查詢功能"""
    print("🔍 測試台鐵班次查詢功能...")
    
    # 創建一個模擬的 InfoCommands 實例
    info_commands = InfoCommands(None)
    
    # 測試志學站
    print("\n📍 測試志學站 (ID: 6240):")
    try:
        result = await info_commands.get_liveboard_data("志學")
        if result:
            print("✅ 志學站查詢成功")
            print(f"找到 {len(result)} 筆班次資料")
            if result:
                first_train = result[0]
                print(f"第一班車: 車次 {first_train.get('TrainNo', 'N/A')} - 方向 {first_train.get('Direction', 'N/A')}")
        else:
            print("⚠️ 志學站無班次資料（可能是非營運時間）")
    except Exception as e:
        print(f"❌ 志學站查詢失敗: {e}")
    
    # 測試其他幾個站
    test_stations = ["臺北", "高雄", "花蓮"]
    for station in test_stations:
        print(f"\n📍 測試 {station} 站:")
        try:
            result = await info_commands.get_liveboard_data(station)
            if result:
                print(f"✅ {station} 站查詢成功，找到 {len(result)} 筆班次")
            else:
                print(f"⚠️ {station} 站無班次資料")
        except Exception as e:
            print(f"❌ {station} 站查詢失敗: {e}")

if __name__ == "__main__":
    asyncio.run(test_tra_function())
