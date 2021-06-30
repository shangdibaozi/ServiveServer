from typing import List

import zlib

import KBEngine

import Lobby
import RoomMgr
from KBEDebug import DEBUG_MSG, ERROR_MSG


"""
在这个文件里面写能在其他游戏中能复用的代码逻辑
"""

def nickName2IntArr(nickNameHexStr):
    # 将字节码字符串转为字节码数组
    bytesArr = bytearray.fromhex(nickNameHexStr)
    # 将字节码数组转为十进制数组
    nickNameArr = [b for b in bytesArr]
    return nickNameArr


def toInt(num):
    """
    将浮点数四舍五入后再取整
    """
    return int(round(num))

def convertListUUID(lst: List[any], uuidKeys: List[str]):
    """
    转化带UINT64或者INT64的列表

    只能是单层列表，不能有嵌套列表
    """
    # newLst = copy.deepcopy(lst)  # KBEngine的基础类型不支持
    newLst = []
    for e in lst:
        o = {}
        for k in e:
            if k in uuidKeys:
                o[k] = str(e[k])
            else:
                o[k] = e[k]

        newLst.append(o)
    
    return newLst

def convert2bytes(obj: any, uuidKeys: List[str] = None) -> bytes:
    """
    将python的字典转成bytes并压缩
    """
    json_str = None
    if uuidKeys is not None:
        newObj = {}
        for k in obj:
            newObj[k] = obj[k]
            if k in uuidKeys:
                newObj[k] = str(obj[k])
    elif isinstance(obj, str):
        json_str = obj
    else:
        json_str = str(obj)
    binary_s = zlib.compress(bytes(json_str, 'utf-8'))
    return binary_s


def createSingletonEntity(entityName: str, params: dict = {}):
    """
    创建全局唯一实体。必须声明好py脚本和def文件。是用KBEngine.globalData[entityName]获取实体
    还是用KBEngine.baseAppData[entityName]获取实体需要自己在实体脚本中写明。

    如果明确该实体只在BaseApp中共享数据则用KBEngine.baseAppData。

    eg.
        Utils.createSingletonEntity('Lobby', {})
    """
    
    def sqlCallback(result, rows, insertid, error):
        if error:
            ERROR_MSG('Utils::createSingletonEntity %s error: %s' % (entityName, error))
        else:
            if len(result) > 0:
                dbid = int(result[0][0])
                KBEngine.createEntityFromDBID(entityName, dbid)
            else:
                entity = KBEngine.createEntityLocally(entityName, params)
                if entity is not None:
                    entity.writeToDB()
                else:
                    ERROR_MSG('Utils::createSingletoneEntity create %s entity error' % entityName)

            DEBUG_MSG('Utils::createSingletoneEntity %s, result: %s' % (entityName, str(result)))

    sql = 'select id from tbl_%s;' % entityName
    KBEngine.executeRawDatabaseCommand(sql, sqlCallback)


def baseLobby() -> Lobby.Lobby:
    return KBEngine.baseAppData['Lobby']

def roomMgr() -> RoomMgr.RoomMgr:
    return KBEngine.baseAppData['RoomMgr']

