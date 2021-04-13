import aiohttp


class Session:
    base_url = f'https://api.vk.com/method/'

    def __init__(self, access_token: str, api_version: int = 5.126):
        self.session_params: dict = {'access_token': access_token,
                                     'v': api_version}
        self.access_token: str = access_token
        self.api_version: int = api_version

    async def method(self, method: str, params: dict):
        url = f'{self.base_url}{method}'
        params |= self.session_params
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                return await resp.json()
