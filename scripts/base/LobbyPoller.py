import socket

from Request import Request

import KBEngine
import Utils

from KBEDebug import DEBUG_MSG, INFO_MSG, WARNING_MSG

# ip白名单
IP_WHITELIST = ["127.0.0.1"]

class LobbyPoller:
    """
    演示：
    可以向kbengine注册一个socket，由引擎层的网络模块处理异步通知收发。
    用法:
    from Poller import Poller
    poller = Poller()
    
    开启(可在onBaseappReady执行)
    poller.start("localhost", 12345)
    
    停止
    poller.stop()
    """
    def __init__(self):
        self._socket = None
        self._clients = {}
        if KBEngine.publish() == 0:
            IP_WHITELIST.append("192.168.11.88")
            IP_WHITELIST.append("192.168.11.44")
            IP_WHITELIST.append("118.31.38.202")
        else:
            IP_WHITELIST.append("118.31.38.202")
        
    def start(self, addr, port):
        """
        virtual method.
        """
        self._socket = socket.socket()
        self._socket.bind((addr, port))
        self._socket.listen(10)
        
        INFO_MSG("LobbyPoller::start: %s" % str(self._socket))
        KBEngine.registerReadFileDescriptor(self._socket.fileno(), self.onRecv)
        # KBEngine.registerWriteFileDescriptor(self._socket.fileno(), self.onWrite)

    def stop(self):
        if self._socket:
            KBEngine.deregisterReadFileDescriptor(self._socket.fileno())
            self._socket.close()
            self._socket = None
        
    def onWrite(self, fileno):
        DEBUG_MSG("Poller::onWrite ***************************")
                
    def onRecv(self, fileno):
        if self._socket.fileno() == fileno:
            sock, addr = self._socket.accept()
            self._clients[sock.fileno()] = (sock, addr)
            KBEngine.registerReadFileDescriptor(sock.fileno(), self.onRecv)
            DEBUG_MSG("Poller::onRecv: new channel[%s/%i]" % (addr, sock.fileno()))
        else:
            sock, addr = self._clients.get(fileno, None)
            if sock is None:
                return

            if addr[0] not in IP_WHITELIST:
                WARNING_MSG("Poller::onRecv: %s/%i not in whitelist!" % (addr, sock.fileno()))
                KBEngine.deregisterReadFileDescriptor(sock.fileno())
                sock.close()
                del self._clients[fileno]
                return
            
            data = sock.recv(2048)

            if len(data) == 0:
                DEBUG_MSG("Poller::onRecv: %s/%i disconnect!" % (addr, sock.fileno()))
                KBEngine.deregisterReadFileDescriptor(sock.fileno())
                sock.close()
                del self._clients[fileno]
                return

            DEBUG_MSG("Poller::onRecv: %s/%i get data, size=%i" % (addr, sock.fileno(), len(data)))
            self.processData(sock, addr, data)
           
    def processData(self, sock, addr, datas):
        """
        处理接收数据
        """
        INFO_MSG("prcessData: %s" % datas)
        data_src = datas.decode('utf-8')
        INFO_MSG("prcessData: decode=%s" % (data_src))

        req = Request(data_src)
        if len(req.jsondata) != 0:
            Utils.baseLobby().onProcessData(req.jsondata)
        response = req.getResponse(200)
        INFO_MSG("prcessData: response=%s" % (response))
        sock.send(response.encode('utf-8'))
 
