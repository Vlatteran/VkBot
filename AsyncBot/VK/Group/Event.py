from enum import Enum
from functools import partial
from typing import Coroutine

from AsyncBot.VK.Group.EventHandler import EventHandler


class Events(Enum):
    """
    Represents events from VK_BOT_API and binds them to handlers
    """
    # message events
    MESSAGE_NEW = partial(EventHandler.on_message_new)

    MESSAGE_REPLY = partial(EventHandler.on_message_reply)
    MESSAGE_EDIT = partial(EventHandler.on_message_edit)

    MESSAGE_ALLOW = partial(EventHandler.on_message_allow)

    MESSAGE_DENY = partial(EventHandler.on_message_deny)

    MESSAGE_TYPING_STATE = partial(EventHandler.on_message_typing_state)

    MESSAGE_EVENT = partial(EventHandler.on_message_event)

    # photo events
    PHOTO_NEW = partial(EventHandler.on_photo_new)

    PHOTO_COMMENT_NEW = partial(EventHandler.on_photo_comment_new)
    PHOTO_COMMENT_EDIT = partial(EventHandler.on_photo_comment_edit)
    PHOTO_COMMENT_RESTORE = partial(EventHandler.on_photo_comment_restore)

    PHOTO_COMMENT_DELETE = partial(EventHandler.on_photo_comment_delete)

    # audio events
    AUDIO_NEW = partial(EventHandler.on_audio_new)

    # video events
    VIDEO_NEW = partial(EventHandler.on_video_new)

    VIDEO_COMMENT_NEW = partial(EventHandler.on_video_comment_new)
    VIDEO_COMMENT_EDIT = partial(EventHandler.on_video_comment_edit)
    VIDEO_COMMENT_RESTORE = partial(EventHandler.on_video_comment_restore)

    VIDEO_COMMENT_DELETE = partial(EventHandler.on_video_comment_delete)

    # wall events
    WALL_POST_NEW = partial(EventHandler.on_wall_post_new)
    WALL_REPOST = partial(EventHandler.on_wall_repost)

    WALL_REPLY_NEW = partial(EventHandler.on_wall_reply_new)
    WALL_REPLY_EDIT = partial(EventHandler.on_wall_reply_edit)
    WALL_REPLY_RESTORE = partial(EventHandler.on_wall_reply_restore)

    WALL_REPLY_DELETE = partial(EventHandler.on_wall_reply_delete)

    # like events
    LIKE_ADD = partial(EventHandler.on_like_add)

    LIKE_REMOVE = partial(EventHandler.on_like_remove)

    # board events
    BOARD_POST_NEW = partial(EventHandler.on_board_post_new)
    BOARD_POST_EDIT = partial(EventHandler.on_board_post_edit)
    BOARD_POST_RESTORE = partial(EventHandler.on_board_post_restore)

    BOARD_POST_DELETE = partial(EventHandler.on_board_post_delete)

    def __init__(self, handler):
        self.handler = handler

    def __call__(self, context: dict, handler) -> Coroutine:

        return self.value(self=handler, **context)
