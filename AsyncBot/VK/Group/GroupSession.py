from AsyncBot.VK.Session import Session


class GroupSession(Session):
    def __init__(self, access_token: str, group_id: int, api_version: int = 5.126):
        super().__init__(access_token, api_version=api_version)
        self.session_params |= {'group_id': group_id}
