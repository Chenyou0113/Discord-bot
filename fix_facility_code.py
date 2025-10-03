"""
修正車站設施顯示代碼
"""

file_path = r"c:\Users\xiaoy\OneDrive\桌面\Discord-bot hp\Discord-bot\cogs\info_commands_fixed_v4_clean.py"

# 讀取文件
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 新的代碼
new_code = '''            
            # 設施資訊
            facilities = []
            
            # 電梯 (檢查陣列長度)
            elevators = station_data.get('Elevators', [])
            if elevators and len(elevators) > 0:
                facilities.append(f"🛗 電梯 ({len(elevators)}台)")
            
            # 電扶梯
            escalators = station_data.get('Escalators', [])
            if escalators and len(escalators) > 0:
                facilities.append(f"🚶 電扶梯 ({len(escalators)}台)")
            
            # 廁所
            toilets = station_data.get('Toilets', [])
            if toilets and len(toilets) > 0:
                facilities.append(f"🚻 廁所 ({len(toilets)}間)")
            
            # 飲水機
            drinking_fountains = station_data.get('DrinkingFountains', [])
            if drinking_fountains and len(drinking_fountains) > 0:
                facilities.append(f"💧 飲水機 ({len(drinking_fountains)}台)")
            
            # 服務台/詢問處
            info_spots = station_data.get('InformationSpots', [])
            if info_spots and len(info_spots) > 0:
                facilities.append(f"ℹ️ 服務台 ({len(info_spots)}處)")
            
            # AED
            aeds = station_data.get('AEDs', [])
            if aeds and len(aeds) > 0:
                facilities.append(f"🏥 AED ({len(aeds)}台)")
            
            # 哺集乳室
            nursing_rooms = station_data.get('NursingRooms', [])
            if nursing_rooms and len(nursing_rooms) > 0:
                facilities.append(f"🍼 哺集乳室 ({len(nursing_rooms)}間)")
            
            # 置物櫃
            lockers = station_data.get('Lockers', [])
            if lockers and len(lockers) > 0:
                facilities.append(f"🔐 置物櫃 ({len(lockers)}組)")
            
            # 停車場
            parkings = station_data.get('ParkingLots', [])
            if parkings and len(parkings) > 0:
                facilities.append(f"🅿️ 停車場 ({len(parkings)}處)")
            
            # 自行車停車
            bike_parkings = station_data.get('BikeParkingLots', [])
            if bike_parkings and len(bike_parkings) > 0:
                facilities.append(f"🚲 自行車停車 ({len(bike_parkings)}處)")
            
            # 充電站
            charging = station_data.get('ChargingStations', [])
            if charging and len(charging) > 0:
                facilities.append(f"🔌 充電站 ({len(charging)}處)")
            
            # 售票機
            ticket_machines = station_data.get('TicketMachines', [])
            if ticket_machines and len(ticket_machines) > 0:
                facilities.append(f"🎫 售票機 ({len(ticket_machines)}台)")
            
            if facilities:
                embed.add_field(
                    name="🎯 車站設施",
                    value=" | ".join(facilities),
                    inline=False
                )
            else:
                embed.add_field(
                    name="🎯 車站設施",
                    value="無詳細設施資訊",
                    inline=False
                )
            
            # 設施地圖 (PDF 連結)
            facility_maps = station_data.get('FacilityMapURLs', [])
            if facility_maps and len(facility_maps) > 0:
                map_links = []
                for map_item in facility_maps[:3]:  # 最多顯示3個
                    map_name = map_item.get('MapName', {}).get('Zh_tw', '車站資訊圖')
                    map_url = map_item.get('MapURL', '')
                    if map_url:
                        map_links.append(f"[{map_name}]({map_url})")
                
                if map_links:
                    embed.add_field(
                        name="🗺️ 車站設施圖",
                        value="\\n".join(map_links),
                        inline=False
                    )
            
'''

# 找到起始行 (搜尋 "# 設施資訊")
start_line = None
for i, line in enumerate(lines):
    if i > 6390 and "# 設施資訊" in line and "facilities = []" in lines[i+1]:
        start_line = i
        break

if start_line is None:
    print("❌ 找不到起始位置")
    exit(1)

print(f"✅ 找到起始行: {start_line + 1}")

# 找到結束行 (搜尋下一個 "# 位置資訊")
end_line = None
for i in range(start_line, min(start_line + 100, len(lines))):
    if "# 位置資訊" in lines[i]:
        end_line = i
        break

if end_line is None:
    print("❌ 找不到結束位置")
    exit(1)

print(f"✅ 找到結束行: {end_line + 1}")
print(f"📝 將替換第 {start_line + 1} 到 {end_line} 行")

# 替換代碼
new_lines = lines[:start_line] + [new_code] + lines[end_line:]

# 寫回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ 修正完成!")
print(f"📊 原始行數: {len(lines)}")
print(f"📊 新的行數: {len(new_lines)}")
print(f"📊 替換了 {end_line - start_line} 行代碼")
