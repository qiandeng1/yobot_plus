import json
import os
import aiohttp
from aiohttp import ClientTimeout
from datetime import datetime


async def clan_battle_info_inquire(url, json_file_path):
    try:
        async with aiohttp.ClientSession(timeout=ClientTimeout(total=10)) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                text = await response.text()
                inquire_data = json.loads(text)
    except Exception as e:
        print(f"获取或解析数据失败: {e}")
        return None

    # 筛选出公会战类型的条目
    clan_battle_info = [event for event in inquire_data if event.get("type") == "公会战"]

    # 将毫秒级时间戳转换为秒级
    start_seconds = clan_battle_info[0]["startMs"] / 1000
    end_seconds = clan_battle_info[0]["endMs"] / 1000

    # 转换为可读的日期时间格式
    start_time = datetime.fromtimestamp(start_seconds).strftime("%m/%d %H:%M")
    end_time = datetime.fromtimestamp(end_seconds).strftime("%m/%d %H:%M")

    data = {
        "database": {
            "start_seconds": start_seconds,
            "end_seconds": end_seconds,
            "start_time": start_time,
            "end_time": end_time
        }
    }

    # 读取现有文件（如果文件存在且非空）
    if os.path.exists(json_file_path) and os.path.getsize(json_file_path) > 0:
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
        except json.JSONDecodeError:
            print(f"警告：{json_file_path} 文件格式无效，将覆盖为新数据")
            file_data = {}
    else:
        file_data = {}

    if "database" in file_data:
        file_data["database"].update(data["database"])
    else:
        file_data.update(data)

    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(file_data, f, indent=4, ensure_ascii=False)
        print("公会战时间更新成功")
