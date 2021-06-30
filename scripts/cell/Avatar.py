
import KBEngine

import KBEDebug as log

class Avatar(KBEngine.Entity):

    def __init__(self):
        KBEngine.Entity.__init__(self)
        log.DEBUG_MSG('cell Avatar.__init__')

    def onDestroy(self):
        log.DEBUG_MSG('cell Avatar.onDestroy')
