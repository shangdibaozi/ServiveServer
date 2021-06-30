import KBEngine
import Utils

import KBEDebug as log

class OpRoom(KBEngine.EntityComponent):

    def __init__(self):
        KBEngine.EntityComponent.__init__(self)

    # region kbengine method
    def onAttached(self, owner):
        log.DEBUG_MSG(f'OpRoom onAttached: owner={owner.id}')

        if self.roomKey > 0:
            Utils.roomMgr().checkRoomExist(self, self.roomKey)

    def onDetached(self, owner):
        log.DEBUG_MSG(f'OpRoom onDetached: owner={owner.id}')

    def onClientEnabled(self):
        log.DEBUG_MSG(f'OpRoom onClientEnabled owner={self.owner.id}')

    def onClientDeath(self):
        log.DEBUG_MSG(f'OpRoom onClientDeath owner={self.owner.id}')
        self.leaveRoom()
    
    # endregion

    def enterRoom(self, roomKey):
        log.DEBUG_MSG(f'OpRoom enterRoom roomKey={roomKey}')
        Utils.roomMgr().enterRoom(self.owner)

    def leaveRoom(self):
        if self.roomKey == 0:
            return
        log.DEBUG_MSG(f'OpRoom leaveRoom roomKey={self.roomKey}')
        Utils.roomMgr().leaveRoom(self.owner, self.roomKey)
        if self.owner.cell is not None:
            self.owner.destroyCellEntity()
            log.DEBUG_MSG('OpRoom leaveRoom')
            self.roomKey = 0

    def createRoom(self):
        log.DEBUG_MSG('OpRoom createRoom')

    def onGetRoomKey(self, roomKey):
        self.roomKey = roomKey
        log.DEBUG_MSG(f'onGetRoomKey roomKey={roomKey}')

    def roomExist(self):
        log.DEBUG_MSG('OpRoom roomExist')

    def roomNotExist(self):
        self.roomKey = 0
        log.DEBUG_MSG('OpRoom roomNotExist')



