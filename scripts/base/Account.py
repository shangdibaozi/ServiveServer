import socket
import struct
# import time

import KBEngine

import KBEDebug as log


class Account(KBEngine.Proxy):
    """
    帐号实体
    客户端登录到服务端后，服务端将会自动创建这个实体，通过这个实体与客户端进行交互
    """

    def __init__(self):
        KBEngine.Proxy.__init__(self)
        # 当前激活的Avatar
        self.activeAvatar = None
        log.DEBUG_MSG('Account[%i]::__init__' % self.id)
        self.ip = None

    # region KBEngine method
    def onTimer(self, id, userArg):
        """
        KBEngine method.
        使用addTimer后， 当时间到达则该接口被调用
        @param id		: addTimer 的返回值ID
        @param userArg	: addTimer 最后一个参数所给入的数据
        """
        pass

    def onClientEnabled(self):
        """
        KBEngine method.
        该entity被正式激活为可使用， 此时entity已经建立了client对应实体， 可以在此创建它的
        cell部分。
        """
        self.ip = socket.inet_ntoa(struct.pack('!L', self.clientAddr[0]))
        log.INFO_MSG("Account[%i] entities enable. entityCall:%s, clientIp: %s self.client is %s" % (
            self.id, self.client, self.ip, self.client))

    def onLogOnAttempt(self, ip, port, password):
        """
        KBEngine method.
        如果在脚本中实现了此回调，这个函数在客户端尝试使用当前账号实体进行登录时触发回调。
        这种情况通常是实体存在于内存中处于有效状态，最明显的例子是用户A使用此账号登录了，用户B使用同一账号进行登录，此时回调触发。

        这个回调函数可以返回如下常量值：
        KBEngine.LOG_ON_ACCEPT：允许新的客户端与实体进行绑定，如果实体已经绑定了一个客户端，之前的客户端将被踢出。
        KBEngine.LOG_ON_REJECT：拒绝新的客户端与实体绑定。
        KBEngine.LOG_ON_WAIT_FOR_DESTROY：等待实体销毁后再进行客户端绑定。

        """
        log.INFO_MSG("Account[%i].onLogOnAttempt: ip = %s, port = %i, selfClient = %s, clientAddr: %i" % (self.id, ip, port, self.client, self.clientAddr[0]))

        # TODO: 暂时只考虑断线重连的功能，不考虑顶号

        # 如果一个在线的帐号被一个客户端登录并且onLogOnAttempt返回允许，那么会踢掉之前的客户端连接
        # 那么此时self.activeAvatar可能不为None
        if self.activeAvatar is not None:
            if self.activeAvatar.client is not None:  # 存在两种情况：1、玩家短时间内断线重连；2、顶号
                log.DEBUG_MSG('onLogOnAttempt before giveClientTo')
                # 为什么这里要将client给Account实体呢？
                # 因为客户端的登录流程是通过客户端的Account和服务端交互的
                self.activeAvatar.giveClientTo(self)
                log.DEBUG_MSG('onLogOnAttempt after giveClientTo 1')
            # 如果client已销毁，则会重新再创建一个
            log.DEBUG_MSG('onLogOnAttempt after giveClientTo 2')
            
        return KBEngine.LOG_ON_ACCEPT

    def onClientDeath(self):
        """
        KBEngine method.
        客户端对应实体已经销毁
        """
        log.DEBUG_MSG("Account[%i].onClientDeath:" % self.id)
        if self.activeAvatar is not None:
            self.activeAvatar.accountEntity = None
            self.activeAvatar = None
        
        self.destroy()

    def onDestroy(self):
        """
        KBEngine method.
        entity销毁
        """
        log.DEBUG_MSG("Account[%i].onDestroy." % (self.id))
        if self.activeAvatar:
            self.activeAvatar.accountEntity = None
            try:
                self.activeAvatar.destroySelf()
            except Exception as err:
                log.ERROR_MSG('Account::onDestroy error: %s' % err)

        self.activeAvatar = None
    # endregion

    # region exposed method
    def reqAvatarList(self):
        """
        请求所有角色列表，不包括已经逻辑删除的角色
        """
        log.DEBUG_MSG(f'Account.reqAvatarList: size={len(self.characters)}')
        characters = []
        for character in self.characters:
            if character['isDel'] == 0:
                characters.append(character)

        self.client.onReqAvatarList(characters)

    def reqCreateAvatar(self, roleType, name):
        """
        客户端请求创建一个角色
        """
        if len(name) == 0:
            log.ERROR_MSG(f'Account[{self.id}].reqCreateAvatar error name is empty')
            return
        
        props = {
            'roleType': roleType,
            'name': name
        }

        # 将avatar创建在和account相同的baseapp上，这样它们之间的方法调用和属性访问不需要通过rpc的方式实现。
        avatar: KBEngine.Proxy = KBEngine.createEntityLocally("Avatar", props)
        if avatar:
            avatar.writeToDB(self._onAvatarSaved)

    def reqRemoveAvatar(self, dbid):
        """
        请求删除指定角色，这里只进行了逻辑删除
        """
        for character in self.characters:
            if character['dbid'] == dbid:
                character['isDel'] = 1  # 表示逻辑删除
                self.client.onRemoveAvatar(dbid)
                break

    def selectAvatarGame(self, dbid):
        """
        客户端选择某个角色进入游戏
        """
        log.DEBUG_MSG("Account[%i].selectAvatarGame: %i. self.activeAvatar = %s" % (self.id, dbid, self.activeAvatar))
        # 注意：使用giveClientTo的entity必须是当前baseapp上的entity
        if self.activeAvatar is None:
            # 由于需要从数据加载角色，因此是一个异步过程，加载成功或者失败会调用__onAvatarCreated接口
            # 当角色创建好之后，account会调用giveClientTo将客户端控制权（可理解为网络连接与某个实体的绑定）切换到Avatar身上，
            # 之后客户端各种输入输出都通过服务器上这个Avatar来代理，任何proxy实体获得控制权都会调用onClientEnabled
            # Avatar继承了Teleport，Teleport.onClientEnabled会将玩家创建在具体的场景中
            KBEngine.createEntityFromDBID('Avatar', dbid, self._onAvatarCreated)
        else:
            self.giveClientTo(self.activeAvatar)
    # endregion

    # region callback method
    def _onAvatarCreated(self, baseRef, dbid, wasActive):
        """
        选择角色进入游戏时被调用
        """
        if wasActive:
            log.ERROR_MSG("Account[%i]._onAvatarCreated: this character is in world now!" % self.id)
            return

        if baseRef is None:
            log.ERROR_MSG("Account[%i]._onAvatarCreated: the character you wanted to create is not exist!" % self.id)
            return

        avatar = KBEngine.entities.get(baseRef.id)
        if avatar is None:
            log.ERROR_MSG("Account[%i]._onAvatarCreated: when character was created, it died as well!" % self.id)
            return

        if self.isDestroyed:
            log.ERROR_MSG("Account[%i]._onAvatarCreated: i dead, will the destroy of Avatar!" % self.id)
            avatar.destroy()
            return
            
        avatar.accountEntity = self
        self.activeAvatar = avatar
        self.giveClientTo(avatar)

    def _onAvatarSaved(self, success, avatar):
        """
        新建角色写入数据库回调
        """
        log.INFO_MSG("Account[%i]._onAvatarSaved: create avatar state: %i, %s, %i" % (self.id, success, avatar.name, avatar.databaseID))
        # 如果此时帐号已经销毁，角色已经无法被记录则我们清除这个角色
        if self.isDestroyed:
            if avatar:
                avatar.destroy(True)
            return

        if success:
            avatarInfo = {
                'isDel': 0,
                'dbid': avatar.databaseID,
                'name': avatar.name,
                'roleType': avatar.roleType
            }
            self.characters.append(avatarInfo)
            self.writeToDB()

            avatar.accountEntity = self
            self.activeAvatar = avatar
            self.giveClientTo(avatar)
        else:
            log.ERROR_MSG('Account[%i]._onAvatarSaved: create avatar faile.' % (self.id))
                
    # endregion
