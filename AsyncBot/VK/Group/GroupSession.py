from AsyncBot.VK.Session import Session


class GroupSession(Session):
    """
    Class to accessing VK_API as group
    """
    def __init__(self, access_token: str, group_id: int, api_version: int = 5.126):
        """

        :param access_token: GROUP_API_TOKEN for VK_API
        :param group_id: id of group you are logging in to
        :param api_version: version af VK_API that you use
        """
        super().__init__(access_token, api_version)
        self.session_params |= {'group_id': group_id}
