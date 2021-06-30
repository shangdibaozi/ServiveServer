import KBEngine
# import Utils

import KBEDebug as log

TIMER_TYPE_DESTROY = 0

class Avatar(KBEngine.Proxy):

    def __init__(self):
        KBEngine.Proxy.__init__(self)

        self.accountEntity = None
        self.destroyTimer = 0
        self.roomCell = None
        log.DEBUG_MSG('Avatar::__init__ base dbid = %i' % (self.databaseID))

    # -------------------KBEngine method----------------------------
    def onClientEnabled(self):
        """
        该entity被正式激活为可使用，此时entity已经建立了client对应实体，可以在此创建它的cell部分
        """
        log.INFO_MSG("Avatar[%i].onClientEnabled entity enable." % self.id)

        # 断线重连回来后删除自动销毁实体的定时器
        if self.destroyTimer > 0:
            self.delTimer(self.destroyTimer)
            self.destroyTimer = 0

        # Utils.baseLobby().avatarEnterWorld(self, self.databaseID)
        self.client.onAvatarEnabled()

    def onClientDeath(self):
        """
        KBEngine methods.
        entity丢失了客户端实体
        """
        log.DEBUG_MSG('Avatar[%i]::onClientDeath.' % self.id)
        self.destroyTimer = self.addTimer(60, 0, TIMER_TYPE_DESTROY)  # 60s后销毁avatar实体

    def onTimer(self, tid, userArg):
        """
        引擎回调timer触发
        """
        if userArg == TIMER_TYPE_DESTROY:
            self.onDestroyTimer()

    def onDestroy(self):
        """
        KBEngine method.
        如果这个函数在脚本中有实现，这个函数在调用Entity.destroy()后，在实际销毁之前被调用。
        这个函数没有参数。
        """
        log.DEBUG_MSG("Avatar[%i].onDestroy" % self.id)

        if self.accountEntity is not None:
            self.accountEntity.destroy()
            self.accountEntity = None
    
    def onGetCell(self):
        """
        entity的cell部分实体被创建成功
        """
        log.DEBUG_MSG(f'Avatar[{self.id}].onGetCell')
        self.roomCell.onEnter(self.cell)

    def onLoseCell(self):
        log.DEBUG_MSG(f'Avatar[{self.id}].onLoseCell')
        self.opRoom.roomKey = 0

    # ---------------------defined method-----------------------

    def destroySelf(self):
        log.DEBUG_MSG('Avatar::destroySelf %s' % (self.accountEntity is None))

        if self.client is not None:
            return
        
        if self.cell is not None:
            self.destroyCellEntity()

        # 如果帐号ENTITY存在，则也通知销毁它
        if self.accountEntity is not None:
            log.DEBUG_MSG('Avatar[%i]::destroySelf, destroy Account Entity' % self.id)
            if self.accountEntity.isDestroyed is False:
                log.DEBUG_MSG('Avatar::destroySelf destroy Account Entity')
                self.accountEntity.destroy()
            self.accountEntity = None

        # 销毁base
        if self.isDestroyed is False:
            log.DEBUG_MSG('Avatar[%i]::destroy' % self.id)
            self.destroy()

    def onDestroyTimer(self):
        log.DEBUG_MSG('Avatar[%i]::onDestroyTimer' % self.id)
        self.destroySelf()

    def createCell(self, roomCell):
        log.DEBUG_MSG(f'Avatar[{self.id}].createCell')
        self.roomCell = roomCell
        self.createCellEntity(roomCell)

    
