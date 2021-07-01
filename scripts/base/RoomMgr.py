

from typing import Dict
import KBEngine
import Functor

import KBEDebug as log

import Room as room
import OperateCode

MAX_PLAYER = 10

class RoomData:

    def __init__(self, roomKey) -> None:
        self.roomKey: int = roomKey
        self.playerCnt: int = 0
        self.roomEntity: room.Room = None

class RoomMgr(KBEngine.Entity):

    def __init__(self):
        KBEngine.Entity.__init__(self)
        KBEngine.baseAppData['RoomMgr'] = self

        self.rooms: Dict[int, RoomData] = {}
        self.curRoomData = None

    def enterRoom(self, avatar, roomKey):
        roomData = self.rooms.get(roomKey, None)
        if roomData is None:
            log.WARNING_MSG(f'RoomMgr::enterRoom not found roomKey: {roomKey}')
            avatar.opRoom.client.enterRoomCallback(OperateCode.ROOM_NOT_FOUND_KEY)
        else:
            if roomData.playerCnt >= MAX_PLAYER:
                avatar.opRoom.client.enterRoomCallback(OperateCode.ROOM_FULL_PLAYER)
            else:
                roomData.roomEntity.enterRoom(avatar)
                roomData.playerCnt += 1

    def leaveRoom(self, entity, roomKey):
        """
        玩家主动离开房间（包括玩家断线）
        """
        roomData = self.rooms.get(roomKey, None)
        if roomData is not None:
            if roomData.roomEntity is not None:
                roomData.roomEntity.onLeave(entity.id)
                roomData.playerCnt -= 1
            else:
                log.WARNING_MSG(f'RoomMgr::leaveRoom roomEntity is None, roomKey: {roomKey}')
        
    def createRoom(self):
        roomKey = KBEngine.genUUID64()
        KBEngine.createEntityAnywhere('Room', {
            'roomKey': roomKey
        }, Functor.Functor(self.onRoomCreatedCB, roomKey))
        self.rooms[roomKey] = RoomData(roomKey)
    
    def onRoomCreatedCB(self, roomKey, room):
        """
        当Room实体的base部分创建好就会回调到这里
        """
        log.DEBUG_MSG(f'onRoomCreatedCB roomKey: {roomKey}, roomId: {room.id}')

    def onRoomGetCell(self, roomEntity, roomKey):
        """
        当Room实体创建好cell部分后回调到这里
        """
        roomData = self.rooms.get(roomKey, None)
        if roomData is None:
            log.ERROR_MSG(f'RoomMgr::onRoomGetCell error not found roomKey: {roomKey}')
        else:
            roomData.roomEntity = roomEntity
