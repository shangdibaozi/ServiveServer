
from enum import Enum

import Utils

INVITE_ACTIVITY_STALL_ID = 1000000
MAX_STALL_LEVEL = 500
VIDEO_RANDOM_COUNT = 3

gm_dbid = [2, 3]

class INVITE_TALENT_TYPE(Enum):
    STALL_INVITE = 1001
    VIDEO_INVITE = 1002
    FRIEND_INVITE = 1003
    SIGN_INVITE = 1004

class TALENT_QUALITY_LEVEL(Enum):
    ONE = 10101
    TWO = 10201
    THREE = 10301
    NORMAL_FOUR = 10401
    ELITE_FOUR = 10402
    NORMAL_FIVE = 10501
    ELITE_FIVE = 10502


STALL_INVIATION_ONE_TABLE_ID = 10101001


STALL_INVIATION_TEN_TABLE_ID = 10101002

VIDEO_INVIATION_TABLE_ID = 10102001

FRIEND_INVIATION_ONE_TABLE_ID = 10103001
FRIEND_INVIATION_TEN_TABLE_ID = 10103002

SIGN_INVIATION_ONE_TABLE_ID = 10104001
SIGN_INVIATION_TEN_TABLE_ID = 10104002

GOLD_BUY_HORN_TABLEID = 10201001
STOEN_BUY_HORN_TABLEID = 10201002
STONE_BUY_INVIATION_TABLEID = 10202001
VIDEO_GET_GOLD_INCOME_TABLEID = 10401001

# 每日最大可偷金币次数
MAX_STEAL_GOLD_COUNT = 10


class MALL_TAKE_CARD_RESULT(Enum):
    SUCCESS = 0
    GOLD_ERR = 1
    STONE_ERR = 2
    VIDEO_ERR = 3
    LOVE_HEART_ERR = 4


class MALL_MARKET_BUY_RESULT(Enum):
    SUCCESS = 0
    GOLD_ERR = 1
    STONE_ERR = 2
    VIDEO_ERR = 3
    DAY_LIMIT_ERR = 4
    LOCKED_DECORATION = 5


class SHOP_TYPE(Enum):
    GOLD = 1
    STONE = 2
    PROP = 3
    VIDEO = 4
    BIG_TALENT_BOX = 5


class PROP(Enum):
    HORN = 10305001
    LOVE_HEART = 10405001
    INVIATION = 10505001


CATCH_THIEF_DETECTIVE_CARD = 0
CATCH_THIEF_POLICE_CARD = 1
CATCH_THIEF_RANDOM_CARD = 2
# UINT64的最大值
MAX_UNSIGNED_VALUE = 18446744073709551615


# 默认双倍收益时长
DEFAULT_REWARD_DOUBLE_INCOME_TIME = 2 * 60 * 60

# 看视频每次获得宝石数量
AD_GEM_CNT = 30
# 看视频获得宝石总次数
AD_GEM_TIMES = 12

# 概率基础值
RATE_BASE = 10000


# region 道具类型
PROP_BOOK_TALENT_EXP = 21  # 人才经验书
PROP_BOOK_SKILL_EXP = 25   # 技能经验书
PROP_BOOK_SKILL = 22       # 人才技能书
PROP_CATCHTHIEF_CARD = 4   # 抓贼道具卡
PROP_MALL_COMSUME = 5      # 商城消耗道具

PROP_FRAGMENT = 61          # 碎片
PROP_FRAGMENT_BOX3 = 66     # 3星人才碎片宝箱
PROP_FRAGMENT_BOX4 = 67     # 4星人才碎片宝箱
PROP_FRAGMENT_BOX5 = 68     # 5星人才碎片宝箱
PROP_CATCH_THIEF = 4   # 抓贼小游戏道具卡
PROP_MALL = 5          # 商城招聘道具
PROP_GOLD = 1          # 金币
PROP_STONE = 2          # 宝石
PROP_HONGBAO = 3        # 红包

# endregion

INVITER_REWARD_TABLEID = 102001  # 邀请人的奖励
INVITEE_REWARD_TABLEID = 201001  # 接受邀请人的奖励


def strutf8(item):
    return str(item, 'utf-8')


AVATAR_INFO_FIELD = {
    'nickName': lambda item: Utils.nickName2IntArr(str(item, 'utf-8')),
    'headImgUrl': strutf8,
    'inviteCode': strutf8,
    'inviterDBID': int,
    'achievementPoint': int,
    'headOfficeStarLv': int,
    'specialBuildingStarLv': int,
    'bookstoreStarLv': int,
    'prosperity': int,
    'decorations': int,
    'sceneId': int,
    'persecondIncome': int,
    'lastStolenTime': int,
    'offlineIncome': int,
    'stolenCount': int,
    'stealCount': int,
    'lastResetTime': int,
    'stolenAvatarsDBID': strutf8,
    'defensePage': int,
    'channelID': strutf8,
    'catchThiefLevel': int,
    'stealersInfo': strutf8,
    'contributionRecord': strutf8,
}

PROP_CATCH_THIEF_RANDOM_CARD = 10204003
PROP_CATCH_THIEF_POLICE_CARD = 10204002
PROP_CATCH_THIEF_DETECTIVE_CARD = 10204001
PROP_MALL_HORN = 10305001
PROP_MALL_LOVEHEART = 10405001
PROP_MALL_INVIATION = 10505001

# region 人才属性类型
PROP_TYPE_VIM = 'energy'
PROP_TYPE_KNOWLEDGE = 'knowedge'
PROP_TYPE_ELOQUENCE = 'eloquence'
PROP_TYPE_REACTION = 'reaction'
# endregion


# region 偷金币
STEAL_GOLD_AVATAR_ONLINE = 0  # 该玩家当前在线，无法进行偷金币
STEAL_GOLD_HAS_STEAL = 1  # 已经偷过该玩家
STEAL_GOLD_NOT_ENOUGH = 2  # 该玩家金币不足
STEAL_GOLD_STEAL_COUNT_FULL = 3  # 玩家已经进行了10次偷金币
STEAL_GOLD_WITHOUT_BATTLE_TALENTS = 4  # 没有配置出战人才

MAX_STEAL_GOLD_COUNT = 10
# endregion

SHOP_DESC = 202  # 商城装饰物

# 红包相关
HONGBAO_JINDU_FULL = 10000
CAISHEN_VEDIO_COUNT = 5
RedEnvelope_TABLEID_CAISHEN = 10001
RedEnvelope_TABLEID_VEDIO = 30001

STALL_TALENT_UUID = [f'idx{i}TalentUUID' for i in range(4)]


# 贡献来自徒弟
FROM_APPRENTICE = 0
# 贡献来自徒孙
FROM_APP_APPRENTICE = 1
