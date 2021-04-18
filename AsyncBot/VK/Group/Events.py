from enum import Enum


class Events(Enum):
    # message events
    MESSAGE_NEW = 'message_new'

    MESSAGE_REPLY = 'message_reply'
    MESSAGE_EDIT = 'message_edit'

    MESSAGE_ALLOW = 'message_allow'

    MESSAGE_DENY = 'message_deny'

    MESSAGE_TYPING_STATE = 'message_typing_state'

    MESSAGE_EVENT = 'message_event'

    # photo events
    PHOTO_NEW = 'photo_new'

    PHOTO_COMMENT_NEW = 'photo_comment_new'
    PHOTO_COMMENT_EDIT = 'photo_comment_edit'
    PHOTO_COMMENT_RESTORE = 'photo_comment_restore'

    PHOTO_COMMENT_DELETE = 'photo_comment_delete'

    # audio events
    AUDIO_NEW = 'audio_new'

    # video events
    VIDEO_NEW = 'video_new'

    VIDEO_COMMENT_NEW = 'photo_comment_new'
    VIDEO_COMMENT_EDIT = 'photo_comment_edit'
    VIDEO_COMMENT_RESTORE = 'photo_comment_restore'

    VIDEO_COMMENT_DELETE = 'photo_comment_delete'

    # wall events
    WALL_POST_NEW = 'wall_post_new'
    WALL_REPOST = 'wall_repost'

    WALL_REPLY_NEW = 'wall_reply_new'
    WALL_REPLY_EDIT = 'wall_reply_edit'
    WALL_REPLY_RESTORE = 'wall_reply_restore'

    WALL_REPLY_DELETE = 'wall_reply_delete'

    # like events
    LIKE_ADD = 'like_add'

    LIKE_REMOVE = 'like_remove'

    # board events
    BOARD_POST_NEW = 'board_post_new'
    BOARD_POST_EDIT = 'board_post_edit'
    BOARD_POST_RESTORE = 'board_post_restore'

    BOARD_POST_DELETE = 'board_post_delete'


if __name__ == '__main__':
    print(Events('message_new'))
