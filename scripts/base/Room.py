
import KBEngine
import Utils

from KBEDebug import ERROR_MSG, DEBUG_MSG

class Room(KBEngine.Entity):

    def __init__(self):
        KBEngine.Entity.__init__(self)
        self.createCellEntityInNewSpace(None)
        DEBUG_MSG('base Room.__init__')

    def enterRoom(self, entity):
        if self.cell is not None:
            entity.createCell(self.cell)
        else:
            ERROR_MSG('Room.enterRoom error, cell is None')

    def onEnter(self, entity):
        if self.cell is not None:
            self.cell.onEnter(entity)

    def onLeave(self, entityId):
        if self.cell is not None:
            self.cell.onLeave(entityId)

    def onGetCell(self):
        """
        entity的cell部分实体被创建成功
        """
        Utils.roomMgr().onRoomGetCell(self, self.roomKey)
