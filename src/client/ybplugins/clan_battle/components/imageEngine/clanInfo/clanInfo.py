import time
import json
import os
import asyncio
from pathlib import Path
from typing import Any, Dict, Union
from aiocqhttp.api import Api
from ..clanInfo import databaseCheck
from ..clanInfo import clanRankSearch
from ..clanInfo.userCookies import USER_COOKIES
from apscheduler.schedulers.asyncio import AsyncIOScheduler

clanInfoPath = Path(__file__).parent.joinpath("./clanInfo.json")

# 1. 创建API客户端
api_client = clanRankSearch.PCRAPIClient(cookies=USER_COOKIES)


class ClanInfo:
    def __init__(self,
                 glo_setting: Dict[str, Any],
                 scheduler: AsyncIOScheduler,
                 bot_api: Api,
                 *args, **kwargs):
        # 这是来自yobot_config.json的设置，如果需要增加设置项，请修改default_config.json文件
        self.setting = glo_setting
        # 这是cqhttp的api，详见cqhttp文档
        self.api = bot_api

        # @scheduler.scheduled_job("cron", minute='*', second='0', id="clan_battle_info_inquire")
        @scheduler.scheduled_job("cron", day='1/10/20', hour='10', minute='0', second='0', id="clan_battle_info_inquire")
        async def clan_battle_info_inquire():
            await databaseCheck.clan_battle_info_inquire("https://priconne.kimura.icu/calendar/events_cn.json", clanInfoPath)

        # @scheduler.scheduled_job("cron",  minute='*', second='0', id="clan_rank_inquire")
        @scheduler.scheduled_job("cron", hour='*', minute='10,40', second='0', id="clan_rank_inquire")
        async def clan_rank_inquire():
            if os.path.exists(clanInfoPath) and os.path.getsize(clanInfoPath) > 0:
                try:
                    with open(clanInfoPath, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                except json.JSONDecodeError:
                    file_data = {}
            else:
                file_data = {}

            if "database" in file_data:
                now = time.time()
                if file_data["database"]["start_seconds"] < now < file_data["database"]["end_seconds"]:
                    for key, value in file_data.items():
                        if key != "database" and "clan_name" in value:
                            try:
                                resp_data = await api_client.get(
                                    params=file_data[key]
                                )
                                if not resp_data["data"]:
                                    print("公会名称错误，请检查绑定信息")
                                for leader_name in resp_data["data"]:
                                    if leader_name["leader_name"] == file_data[key]["leader_name"]:
                                        file_data[key].update(leader_name)
                                        print(f"群{key}更新成功")
                                await asyncio.sleep(1)
                            except Exception as e:
                                print(f"\n 搜索请求失败：{str(e)}")
                    with open(clanInfoPath, 'w', encoding='utf-8') as f:
                        json.dump(file_data, f, indent=4, ensure_ascii=False)
                # else:
                #     print("当前不在公会战时间内")
            else:
                print("数据库内无公会战时间信息")

    # 无该功能作用
    async def execute_async(self, ctx: Dict[str, Any]) -> Union[None, bool, str]:
        cmd = ctx['raw_message']
        if cmd == '你好':

            # 调用api发送消息，详见cqhttp文档
            await self.api.send_private_msg(
                user_id=123456, message='收到问好')

            # 返回字符串：发送消息并阻止后续插件
            return '世界'

        # 返回布尔值：是否阻止后续插件（返回None视作False）
        return False


