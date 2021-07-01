import KBEngine


import KBEDebug as log

class Room(KBEngine.Entity):

    def __init__(self):
        KBEngine.Entity.__init__(self)
        self.avatars = {}
        log.DEBUG_MSG('cell Room.__init__')

    def onEnter(self, entity):
        log.DEBUG_MSG(f'cell Room[{entity.id}].onEnter')
        self.avatars[entity.id] = entity

        # entity.opRoom.enterRoomSuccess()
        # entity.opRoom.client.enterRoomCallback(0)

    def onLeave(self, eid):
        if eid in self.avatars:
            del self.avatars[eid]

    def destroyRoom(self):
        for eid in self.avatars:
            self.base.onLeave(eid)
            self.avatars[eid].cell.destroy()
        self.avatars.clear()

