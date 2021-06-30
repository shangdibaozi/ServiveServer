

import KBEngine
import Functor

import KBEDebug as log

MAX_PLAYER = 10

class RoomMgr(KBEngine.Entity):

    def __init__(self):
        KBEngine.Entity.__init__(self)
        KBEngine.baseAppData['RoomMgr'] = self

        self.rooms = {}
        self.curRoomData = None

    def enterRoom(self, avatar):
        if self.curRoomData is None:
            for k in self.rooms:
                if self.rooms[k]['playerCnt'] < MAX_PLAYER:
                    self.curRoomData = self.rooms[k]
                    break
        
        if self.curRoomData is None:
            roomData = self.createRoom()
            roomData['pendingEnterEntities'].append(avatar)
            roomData['playerCnt'] += 1
            self.curRoomData = roomData
            avatar.opRoom.onGetRoomKey(roomData['roomKey'])
        else:
            if self.curRoomData['roomEntity'] is not None:
                self.curRoomData['roomEntity'].enterRoom(avatar)
            else:
                self.curRoomData['pendingEnterEntities'].append(avatar)
            
            avatar.opRoom.onGetRoomKey(self.curRoomData['roomKey'])

            self.curRoomData['playerCnt'] += 1
            if self.curRoomData['playerCnt'] == MAX_PLAYER:
                self.curRoomData = None

    def leaveRoom(self, entity, roomKey):
        """
        玩家主动离开房间（包括玩家断线）
        游戏结束，玩家被踢出房间
        """
        roomData = self.rooms.get(roomKey, None)
        if roomData is not None:
            roomEnt = roomData['roomEntity']
            if roomEnt is not None:
                roomEnt.onLeave(entity.id)
            else:
                log.DEBUG_MSG(f'leaveRoom {entity.id}')
                self.curRoomData['pendingEnterEntities'].remove(entity)
            roomData['playerCnt'] -= 1

    def checkRoomExist(self, entityCall, roomKey):
        if roomKey in self.rooms:
            entityCall.roomExist()
        else:
            entityCall.roomNotExist()
        
    def createRoom(self):
        roomKey = KBEngine.genUUID64()
        KBEngine.createEntityAnywhere('Room', {
            'roomKey': roomKey
        }, Functor.Functor(self.onRoomCreatedCB, roomKey))
        self.rooms[roomKey] = {
            'roomKey': roomKey,
            'roomEntity': None,
            'playerCnt': 0,
            'pendingEnterEntities': []
        }
        return self.rooms[roomKey]
    
    def onRoomCreatedCB(self, roomKey, room):
        """
        当Room实体的base部分创建好就会回调到这里
        """
        log.DEBUG_MSG(f'onRoomCreatedCB roomKey: {roomKey}, roomId: {room.id}')

    def onRoomGetCell(self, roomEntity, roomKey):
        """
        当Room实体创建好cell部分后回调到这里
        """
        roomData = self.rooms[roomKey]
        roomData['roomEntity'] = roomEntity
        if len(roomData['pendingEnterEntities']) > 0:
            for avatar in roomData['pendingEnterEntities']:
                if avatar.isDestroyed is False:  # 再次判断玩家实体是否已销毁
                    roomEntity.enterRoom(avatar)
            roomData['pendingEnterEntities'].clear()
