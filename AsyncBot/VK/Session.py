import asyncio
from typing import *

import aiohttp


class Session:
    """
    Class for accessing VK_API as user
    """
    base_url = f'https://api.vk.com/method/'

    def __init__(self, access_token: str, api_version: float = 5.126):
        """
        :param access_token: USER_API_TOKEN for VK_API
        :param api_version: version af VK_API that you use
        """
        self.session_params: dict = {'access_token': access_token,
                                     'v': api_version}

    async def method(self, method: str, params: dict):
        """
        Base method for accessing VK_API

        :param method: method of VK_API
        :param params: params of request to VK_API
        :return: JSON-response from VK_API
        """
        url = f'{self.base_url}{method}'
        params |= self.session_params
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                return await resp.json()

    async def get_users(self, users: Union[int, Sequence[int]]):
        users = await self.method('users.get',
                                  {'user_ids': ','.join(str(u) for u in users) if users is not int else [users]})
        for user in users['response']:
            print(user)


async def main():
    from AsyncBot.config import token, bot_admin
    session = Session(token, 5.126)
    await session.get_users([bot_admin, 1])


if __name__ == '__main__':
    asyncio.run(main())
