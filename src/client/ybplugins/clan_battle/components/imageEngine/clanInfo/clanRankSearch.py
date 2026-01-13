import uuid
import time
import hashlib
import aiohttp
from aiohttp import ClientTimeout


class PCRAPIClient:
    def __init__(self, cookies=None):
        self.base_url = "//api.game.bilibili.com"
        self.appkey = "f07288b7ef7645c7a3997baf3d208b62"
        self.secret = "mNnGiylYAFXbY0gPy4Zw2nG+dz1t6TYHENz61fxR3Ic="
        self.timeout = 10
        self.cookies = cookies or {}
        self.client_timeout = ClientTimeout(total=self.timeout)

    def api_sign(self, params):
        public_params = {
            "name": params["clan_name"],
            "ts": int(time.time() * 1000),
            "nonce": str(uuid.uuid4()),
            "appkey": self.appkey
        }

        sign_str = "appkey=" + public_params["appkey"] + "&name=" + public_params["name"] + "&nonce=" + public_params["nonce"] + "&ts=" + str(public_params["ts"]) + "&secret=mNnGiylYAFXbY0gPy4Zw2nG+dz1t6TYHENz61fxR3Ic="
        hexMd5 = hashlib.md5()
        hexMd5.update(sign_str.encode())
        sign = str(hexMd5.hexdigest())
        combined_params = public_params
        combined_params['sign'] = sign
        return combined_params

    async def get(self, params=None):
        path = "/game/player/tools/pcr/search_clan"
        request_params = self.api_sign(params or {})
        full_url = f"https:{self.base_url}{path}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://game.bilibili.com/",
            "Origin": "https://game.bilibili.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        try:
            async with aiohttp.ClientSession(
                timeout=self.client_timeout,
                cookies=self.cookies,
            ) as session:
                async with session.get(
                    url=full_url,
                    params=request_params,
                    headers=headers
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    if data.get("code") == -101 and "user_info" not in path:
                        raise Exception("登录失效！Cookie已过期，请重新获取")
                    return data
        except Exception as e:
            print(f"\n 响应处理失败：{str(e)}")
            raise

