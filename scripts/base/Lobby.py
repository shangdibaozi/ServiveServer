import time
import datetime

import KBEngine
import hotupdate

import KBEDebug as log

TIMER_TYPE_REFRESH_DAILY_TASK = 111
TIMER_TYPE_KILL_SERVER = 333

class Lobby(KBEngine.Entity):
            
    def __init__(self):
        KBEngine.Entity.__init__(self)

        KBEngine.baseAppData['Lobby'] = self
        
        self.initRefreshTimer()

        KBEngine.baseAppData['dailyZeroTime'] = int(time.mktime(datetime.date.today().timetuple()))

        log.DEBUG_MSG('Lobby::__init__')

        KBEngine.baseAppData['hotupdate'] = 0
        # 关服倒计时剩余时间
        self.leftTime = -1
        
    # 每日刷新
    def initRefreshTimer(self):
        offset = 0
        currTime = time.time()
        curTimeList = list(time.localtime())
        if curTimeList[4] != 0 or curTimeList[5] != 0:  # 分和秒不为0
            curTimeList[3] += 1  # 下个小时
            curTimeList[4] = 0
            curTimeList[5] = 0
            newTime = time.mktime(time.struct_time(curTimeList))
            offset = newTime - currTime

        offset += 1
        log.DEBUG_MSG('Lobby::initRefreshTimer offset: %f' % offset)
        self.addTimer(offset, 3600, TIMER_TYPE_REFRESH_DAILY_TASK)

    def onTimer(self, tid, userArg):
        if userArg == TIMER_TYPE_REFRESH_DAILY_TASK:
            timeList = list(time.localtime())
            if timeList[3] == 0:
                KBEngine.baseAppData['dailyZeroTime'] = int(time.mktime(datetime.date.today().timetuple()))
                log.DEBUG_MSG('Lobby::onTimer dailyRefresh')

        #         for dbid in self.onlineAvatars:
        #             self.onlineAvatars[dbid].dailyRefresh()

        # elif userArg == TIMER_TYPE_AUTO_SAVE_DB:
        #     self.allSaveDB()
        # elif userArg == TIMER_TYPE_KILL_SERVER:  # 关服倒计时
        #     for eid in self.onlineAvatars:
        #         self.onlineAvatars[eid].client.onKillServer(self.leftTime)
        #     self.leftTime -= 1
        #     if self.leftTime < 0:
        #         self.leftTime = -1
        #         self.delTimer(self.killServerTimer)
        #         self.killServerTimer = 0

    def onDestroy(self):
        log.DEBUG_MSG('Lobby::onDestroy')

    def hotupdate(self):
        hotupdate.reloadModule()
        KBEngine.baseAppData['hotupdate'] += 1
        log.INFO_MSG('Lobby::hotupdate')

    def killServer(self):
        if self.leftTime == -1:
            self.leftTime = 10
            self.killServerTimer = self.addTimer(0, 1, TIMER_TYPE_KILL_SERVER)

    def testFromImport(self):
        log.DEBUG_MSG('Lobby::testFromImport 11')
