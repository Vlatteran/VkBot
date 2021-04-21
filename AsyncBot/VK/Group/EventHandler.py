from AsyncBot.VK.Message import Message
from AsyncBot.VK.User import User


def handler(func):
    async def wrapper(self, **kwargs):
        if func != self.__class__.__dict__[func.__name__]:
            await self.__class__.__dict__[func.__name__](self, **kwargs)
    return wrapper


class EventHandler:
    @handler
    async def on_message_new(self, message: Message, client_info: dict):
        pass

    @handler
    async def on_message_edit(self, message: Message):
        pass

    @handler
    async def on_message_reply(self, message: Message):
        pass

    @handler
    async def on_message_allow(self, user: User, key: str):
        pass

    @handler
    async def on_message_deny(self, user: User):
        pass

    @handler
    async def on_message_typing_state(self, state, sender: User, receiver):
        pass

    @handler
    async def on_message_event(self, context):
        pass

    @handler
    async def on_photo_new(self, context):
        pass

    @handler
    async def on_photo_comment_new(self, context):
        pass

    @handler
    async def on_photo_comment_edit(self, context):
        pass

    @handler
    async def on_photo_comment_restore(self, context):
        pass

    @handler
    async def on_photo_comment_delete(self, context):
        pass

    @handler
    async def on_audio_new(self, context):
        pass

    @handler
    async def on_video_new(self, context):
        pass

    @handler
    async def on_video_comment_new(self, context):
        pass

    @handler
    async def on_video_comment_edit(self, context):
        pass

    @handler
    async def on_video_comment_restore(self, context):
        pass

    @handler
    async def on_video_comment_delete(self, context):
        pass

    @handler
    async def on_wall_post_new(self, context):
        pass

    @handler
    async def on_wall_repost(self, context):
        pass

    @handler
    async def on_wall_reply_new(self, context):
        pass

    @handler
    async def on_wall_reply_edit(self, context):
        pass

    @handler
    async def on_wall_reply_restore(self, context):
        pass

    @handler
    async def on_wall_reply_delete(self, context):
        pass

    @handler
    async def on_like_add(self, context):
        pass

    @handler
    async def on_like_remove(self, context):
        pass

    @handler
    async def on_board_post_new(self, context):
        pass

    @handler
    async def on_board_post_edit(self, context):
        pass

    @handler
    async def on_board_post_restore(self, context):
        pass

    @handler
    async def on_board_post_delete(self, context):
        pass

    # @handler
    # async def on_(self, context):
    #     pass
