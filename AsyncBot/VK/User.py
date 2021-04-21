from requests import get

from AsyncBot.VK.Session import Session


class User:
    """
    Represent user from VK_API
    """
    def __init__(self, user_id, vk_session: Session):
        method = 'users.get'
        params = {'user_ids': {user_id}}
        result = get(url=f'{vk_session.base_url}{method}',
                     params=params | vk_session.session_params).json()['response'][0]
        self.id = user_id
        self.first_name = result['first_name']
        self.last_name = result['last_name']
