import os
import sys
import importlib
import weakref

import KBEDebug as log
import KBEngine


g_allReloadObjs = []
class Reload:
    """
    不是继承于KBEngine.Entity的类，如果也想热更新需要继承Reload
    """
    def __init__(self):
        g_allReloadObjs.append(weakref.ref(self))

def reloadPyCls(reloadPaths):
    """
    热更新。不能热更涉及到引擎层的py模块，比如KBEngine.Entity
    """
    entitiesXMLAP = KBEngine.matchPath('scripts/entities.xml')
    pyScriptRootPath = entitiesXMLAP.split('entities.xml')[0]
    dontReloadFile = {'__init__', 'KBEngine'}

    log.DEBUG_MSG('pyScriptRootPath: %s' % pyScriptRootPath)
    """
    {
        'BattleSimulator': <module 'BattleSimulator' from 'D:/CocosCreator/BaiTan/baitan-server/scripts/common\\BattleSimulator.py'>,
        'cfgmgr': <module 'cfgmgr' from 'D:/CocosCreator/BaiTan/baitan-server/scripts/common\\cfgmgr.py'>,
        'db': <module 'db' from 'D:/CocosCreator/BaiTan/baitan-server/scripts/common\\db.py'>
    }
    """
    allNewModule = {}
    for reloadPath, pkgName in reloadPaths.items():
        fileDir = os.path.join(pyScriptRootPath, reloadPath)
        log.DEBUG_MSG(f'fileDir: {fileDir}')
        for root, dir, files in os.walk(fileDir):
            if fileDir != root:
                break

            for file in files:
                fileName, fileSuffix = file.split('.')
                if fileName in dontReloadFile or fileSuffix != 'py':
                    continue

                modName = fileName
                if pkgName != '':
                    modName = pkgName + '.' + fileName
                    
                log.DEBUG_MSG(f'modName={modName}')
                mod = sys.modules.get(modName)
                # 有的模块不在sys.modules中（为什么？代码执行到需要改模块的语句时，才会导入该模块，模块就被缓存到sys.modules中）
                if mod is None:
                    log.ERROR_MSG(f'Not found module = {fileName}')
                    continue
                
                log.DEBUG_MSG(f'reloaded module: {fileName}')
                allNewModule[modName] = importlib.reload(mod)

    return allNewModule

def reloadData():
    """
    只热更新配置表
    """
    reloadPaths = {
        'data': '',
    }
    reloadPyCls(reloadPaths)


def reloadModule():
    """
    热更新

    注意：
        1、给实体添加新的存储属性，热更新后虽然内存能获取该属性，但该属性不会存盘；
        2、hotupdate只会热更当前进程中的代码，如果有多个baseapp和cellapp，要确保每个baseapp和cellapp所在的进程都执行hotupdate
    """
    # 目录->包名
    reloadPaths = {
        'data': '',
        'common': '',
        'server_common': ''
    }
    
    componentName = KBEngine.component
    log.DEBUG_MSG('componentName: %s' % componentName)
    if componentName == 'baseapp':
        reloadPaths['base/ilobby'] = 'ilobby'
        reloadPaths['base/interfaces'] = 'interfaces'
        reloadPaths['base'] = ''
    elif componentName == 'cellapp':
        reloadPaths['cell/interfaces'] = 'interfaces'
        reloadPaths['cell'] = ''
    else:
        log.DEBUG_MSG('fcomponent: {componentName}')
        return
    # 实体热更
    allNewModule = reloadPyCls(reloadPaths)
    for entity in KBEngine.entities.values():
        entityNewModule = allNewModule.get(entity.className)
        if entityNewModule is None:
            log.WARNING_MSG(f'reloadModule className {entity.className} not found')
            continue
        
        entity.__class__ = getattr(entityNewModule, entity.className)
    
    # 继承了Reload对象热更
    for refObj in g_allReloadObjs:
        obj = refObj()
        if obj is None:
            g_allReloadObjs.remove(refObj)
            log.WARNING_MSG('refObj is None')
            continue
        className = obj.__class__.__name__
        newModule = allNewModule.get(className)
        if newModule is None:
            log.WARNING_MSG(f'reloadModule className {className} not found')
            continue
        obj.__class__ = getattr(newModule, className)

    # 在def文件里面添加了新的方法或者属性，必须调用，否则不生效
    # 如果添加的是persistent为true的属性，热更后数据库表里面并不会写入该属性字段，对于这种情况必须重启引擎
    success = KBEngine.reloadScript()
    log.DEBUG_MSG(f'KBEngine.reloadScript is {success}')
        
    

