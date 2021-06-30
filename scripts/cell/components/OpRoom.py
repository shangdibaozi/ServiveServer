
import KBEngine

import KBEDebug as log

class OpRoom(KBEngine.EntityComponent):

    def __init__(self):
        KBEngine.EntityComponent.__init__(self)

    # region kbengine method
    def onAttached(self, owner):
        log.DEBUG_MSG(f'cell OpRoom onAttached: owner={owner.id}')
        
    def onDetached(self, owner):
        log.DEBUG_MSG(f'cell OpRoom onDetached: owner={owner.id}')

    def onClientEnabled(self):
        log.DEBUG_MSG(f'cell OpRoom onClientEnabled owner={self.owner.id}')

    def onClientDeath(self):
        log.DEBUG_MSG(f'cell OpRoom onClientDeath owner={self.owner.id}')
    
    # endregion
    

    def enterRoomSuccess(self):
        self.client.enterRoomCallback(0)




