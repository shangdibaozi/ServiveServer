from __future__ import annotations
from typing import Dict, List, Any

import time
import datetime

import KBEngine
from KBEDebug import DEBUG_MSG, ERROR_MSG

class DataType:
    def __init__(self, filedType: str, notNull: bool, defaultVal: str = ''):
        self.filedType = filedType
        self.notNull = notNull
        self.defaultVal = defaultVal

        if 'int' in filedType:
            self.convertFunc = self.toInt
        elif 'float' in filedType or 'double' in filedType:
            self.convertFun = self.toFloat
        elif 'varchar' in filedType:
            self.convertFunc = self.toStr
        else:
            self.convertFunc = self.toBlob

    def __str__(self):
        if self.notNull:
            return '%s not null default %s' % (self.filedType, self.defaultVal)
        else:
            return self.filedType

    # region 类型转换方法


    def toInt(self, val: bytes):
        return int(val)

    def toStr(self, val: bytes):
        return str(val, 'utf-8')

    def toFloat(self, val: bytes):
        return float(val)

    def toBlob(self, val: bytes):
        return val

    # endregion

# region 数据类型
def INT8(defaultVal=0) -> DataType:
    return DataType('tinyint(4)', True, defaultVal)

def INT16(defaultVal=0) -> DataType:
    return DataType('smallint(6)', True, defaultVal)

def INT32(defaultVal=0) -> DataType:
    return DataType('int(11)', True, defaultVal)

def INT64(defaultVal=0) -> DataType:
    return DataType('bigint(20)', True, defaultVal)

def UINT8(defaultVal=0) -> DataType:
    return DataType('tinyint(3) unsigned', True, defaultVal)

def UINT16(defaultVal=0) -> DataType:
    return DataType('smallint(5) unsigned', True, defaultVal)

def UINT32(defaultVal=0) -> DataType:
    return DataType('int(10) unsigned', True, defaultVal)

def UINT64(defaultVal=0) -> DataType:
    return DataType('bigint(20) unsigned', True, defaultVal)

def FLOAT(defaultVal=0) -> DataType:
    return DataType('float', True, defaultVal)

def DOUBLE(defaultVal=0) -> DataType:
    return DataType('double', True, defaultVal)

def STRING(length=0, defaultVal='""') -> DataType:
    return DataType('varchar(%i)' % length, True, defaultVal)

def UNICODE(length=0, defaultVal='""') -> DataType:
    return DataType('varchar(%i)' % length, True, defaultVal)

def BLOB() -> DataType:
    return DataType('blob', False)

# endregion


class DBTable(dict):
    """
    功能：自动创建表、删除字段、增加字段、修改字段类型
    注意：表名不能以tbl_或者kbe_开头

    offlineDay: 离线天数
    
    如果需要加载指定离线时长内的玩家数据，则defaultKey必须为玩家的dbid
    """
    def __init__(self, tbName: str, defaultKey: str, filterKey: str = None, offlineDay: int = 0):
        """
        tbName: 表名，不能以tbl_或者kbe_开头

        defaultKey: 除自增id外的表唯一键值

        filterKey: 过滤用的key值

        offlineDay: 最长离线天数

        filterKey和offlineDay一起使用。在查询数据都时候回去kbe_accountinfos里面查找离线天数在offlineDay一下的数据，并且kbe_accountinfos.entityDBID=value(filterKey)
        """
        self.tbName = tbName
        # 表字段
        self.filedDict: Dict[str, DataType] = {
            'id': INT32()
        }
        self.filedKeys: List[str] = None
        self.filedKeysStr: str = None
        self.filedKeysWithoutId: List[str] = None
        self.filedKeysStrWithoutId: str = None
        # 新增的字段
        self.newFileds: Dict[str, DataType] = {}
        # 要删除的字段
        self.delFileds: List[str] = []
        # 更新类型的字段
        self.excFileds: Dict[str, DataType] = {}
        # TableLine缓存池
        self.tableLinePool: List[TableLine] = []
        # 主键字段（）
        self.defaultKey = defaultKey

        # 新增的
        self.newDatas: Dict[int, TableLine] = {}
        # 待删除的
        self.delDatas: Dict[int, TableLine] = {}
        # 改变内容的
        self.updateDatas: Dict[int, TableLine] = {}

        # 表字段（和数据库表中字段顺序一致）
        self.filedNames: List[str] = None

        self.filterKey = filterKey
        # 最早的离线时刻
        if offlineDay > 0:
            self.minOfflineTime = int(time.mktime(datetime.date.today().timetuple())) - offlineDay * 24 * 60 * 60
        else:
            self.minOfflineTime = 0

        # 在查找未加载到内存的数据时，缓存请求。待从数据库中读取到数据后统一处理。
        self.searchItemRequest = {}
    
    # region sql语句
    @property
    def sql(self):
        # id不需要用bigint，存不了那么多数据
        sql = 'create table if not exists %s(id int primary key auto_increment,' % self.tbName

        for filedName in self.filedKeysWithoutId:
            sql += ' %s %s,' % (filedName, self.filedDict[filedName])

        sql = sql[:-1] + ') default charset=utf8;'

        return sql

    @property
    def newFiledSql(self):
        if len(self.newFileds) <= 0:
            return ''

        sql = 'alter table %s add(' % self.tbName
        for filedName in self.newFileds:
            sql += ' %s %s,' % (filedName, self.filedDict[filedName])

        sql = sql[:-1] + ');'

        return sql

    @property
    def delFiledSql(self):
        if len(self.delFileds) <= 0:
            return ''
        
        sql = 'alter table %s' % self.tbName
        for filedName in self.delFileds:
            sql += ' drop column %s,' % filedName

        sql = sql[:-1] + ';'
        return sql

    @property
    def chaFiledSql(self):
        if len(self.excFileds) <= 0:
            return ''

        sql = 'alter table %s' % self.tbName
        for filedName in self.excFileds:
            sql += ' modify %s %s,' % (filedName, self.excFileds[filedName])

        sql = sql[:-1] + ';'

        return sql
    
    # endregion

    @property
    def isSaveAll(self):
        if len(self.delDatas) > 0:
            return False
        if len(self.newDatas) > 0:
            return False
        if len(self.updateDatas) > 0:
            return False
        return True

    def setFiled(self, filedName: str, filedType: DataType):
        """
        设置字段类型
        """
        self.filedDict[filedName] = filedType
        self.newFileds[filedName] = filedType

    def checkFiled(self, filedName: str, filedType: str):
        """
        检测mysql表的字段和py表中的字段是否匹配：
            1、是否存在
            2、类型是否一样
        """
        if filedName == 'id':
            return

        # 删除已存在的字段
        if filedName in self.newFileds:
            del self.newFileds[filedName]

        if filedName in self.filedDict:
            if filedType != str(self.filedDict[filedName]):
                self.excFileds[filedName] = self.filedDict[filedName]
        else:
            # 记录表中有的字段而配置中删掉的字段
            self.delFileds.append(filedName)

    def exec(self, finishCallback=None):
        """
        执行对表字段的增、删、改
        """
        self.finishCallback = finishCallback
        self.filedKeys = list(self.filedDict.keys())
        self.filedKeysStr = ','.join(self.filedKeys)

        self.filedKeysWithoutId = []
        self.filedKeysWithoutId.extend(self.filedKeys)
        self.filedKeysWithoutId.remove('id')
        self.filedKeysStrWithoutId = ','.join(self.filedKeysWithoutId)

        def callback(result, rows, insertid, error):
            if error:
                ERROR_MSG('db::exec create table error: %s' % error)
            else:
                # 虽然每次都会调用到这里，但是除了第一次会创建表，其它时候都不会重新创建表
                DEBUG_MSG('db::exec create table success result: %s, rows: %s, insertid: %i, error: %s' % (str(result), str(rows), insertid, error))
                self.checkExistedFileds()

        KBEngine.executeRawDatabaseCommand(self.sql, callback)

    def checkExistedFileds(self):
        """
        检测表中的字段和配置的字段，根据情况对表进行字段的增删改操作。
        """
        def callback(result, rows, insertid, error):
            if error:
                ERROR_MSG('db::checkExistedFileds error: %s' % error)
            else:
                DEBUG_MSG('db::checkExistedFileds result: %s' % (str(result)))

                size = len(result)
                for i in range(1, size, 1):  # 注意这里忽略了id这个字段的检测
                    item = result[i]  # [b'dbid', b'bigint(20) unsigned', b'NO', b'', b'0', b'']
                    filedName = str(item[0], 'utf-8')  # 二进制转字符串必须指定编码
                    filedType = str(item[1], 'utf-8')
                    notNo = 'not null' if str(item[2], 'utf-8') == 'NO' else ''
                    default = str(item[4], 'utf-8')
                    
                    if len(notNo) > 0:
                        if 'varchar' in filedType:
                            default = '""'
                        fullFiledType = '%s %s default %s' % (filedType, notNo, default)
                    else:
                        fullFiledType = filedType

                    self.checkFiled(filedName, fullFiledType)

                self._updateTable()

        sql = 'desc %s;' % self.tbName
        KBEngine.executeRawDatabaseCommand(sql, callback)

    def _updateTable(self):
        """
        更新表结构
        """
        def _execSQL(sql, callback):
            """
            执行新增字段、删除字段、更新字段类型
            """
            DEBUG_MSG('db::execSQL sql: %s ' % (sql))

            def sqlCallback(result, rows, insertid, error):
                if error:
                    ERROR_MSG('db::execSQL error: %s' % error)
                else:
                    DEBUG_MSG('db::execSQL success')
                    callback()

            KBEngine.executeRawDatabaseCommand(sql, sqlCallback)

        def _deleteFiled():
            delSql = self.delFiledSql
            if len(delSql) > 0:
                _execSQL(delSql, _changeFiled)
            else:
                _changeFiled()

        def _changeFiled():
            excSql = self.chaFiledSql
            if len(excSql) > 0:
                _execSQL(excSql, _addFiled)
            else:
                _addFiled()

        def _addFiled():
            newSql = self.newFiledSql
            if len(newSql):
                _execSQL(newSql, self.selectData)
            else:
                self.selectData()

        _deleteFiled()

    def selectData(self):
        # region 从表中读取数据

        def _selectData(filedNames: List[str]):
            def callback(result, rows, insertid, error):
                if error:
                    ERROR_MSG('db::selectData error: %s' % error)
                else:
                    DEBUG_MSG('db::selectData filedNames: %s' % str(filedNames))
                    for items in result:
                        line = TableLine()
                        line.defaultKey = self.defaultKey
                        
                        for i, filedName in enumerate(filedNames):
                            line[filedName] = self.filedDict[filedName].convertFunc(items[i])
                            
                        self._setitem(line[self.defaultKey], line)
                    
                    if self.finishCallback is not None:
                        self.finishCallback()
                        self.finishCallback = None  # 去引用

            if self.minOfflineTime == 0:
                sql = 'select %s from %s;' % (','.join(filedNames), self.tbName)
            else:
                # sql = 'select %s from %s where %s in (select entityDBID from kbe_accountinfos where lasttime >= %s);' % (','.join(filedNames), self.tbName, self.defaultKey, self.minOfflineTime)
                sql = 'select %s from %s JOIN kbe_accountinfos on %s.%s=kbe_accountinfos.entityDBID where kbe_accountinfos.lasttime >= %s' % (','.join(filedNames), self.tbName, self.tbName, self.filterKey, self.minOfflineTime)

            DEBUG_MSG('db::selectData::_selectData sql: %s' % sql)
            KBEngine.executeRawDatabaseCommand(sql, callback)
        # endregion

        # region 按顺序获取表字段名称
        def descCallback(result, rows, insertid, error):
            if error:
                ERROR_MSG('db::checkExistedFileds error: %s' % error)
            else:
                DEBUG_MSG('db::checkExistedFileds result: %s' % (str(result)))
                filedNames = []
                for item in result:
                    filedName = str(item[0], 'utf-8')  # 二进制转字符串必须指定编码
                    filedNames.append(filedName)

                self.filedNames = filedNames
                _selectData(filedNames)

        sql = 'desc %s;' % self.tbName
        KBEngine.executeRawDatabaseCommand(sql, descCallback)
        # endregion

    def exeSave(self, maxRows=100):
        """
        执行sql，对数据进行增删改。
        """
        self._execSaveDel(maxRows)

    def _execSaveDel(self, maxRows):
        """
        执行存表操作：删除行

        每次最多删除100行数据
        """
        if len(self.delDatas) == 0:
            self._execSaveUpdate(maxRows)
            return

        def callback(result, rows, insertid, error):
            if error:
                ERROR_MSG('db::_execSaveDel error: %s' % error)
            else:
                DEBUG_MSG('db::_execSaveDel success')
                self._execSaveUpdate(maxRows)
        
        i = 0
        values = []
        for k in list(self.delDatas.keys()):
            values.append('%s' % k)

            self.putLineObj(self.delDatas[k])
            del self.delDatas[k]

            i += 1
            if i >= maxRows:
                break
        
        sql = 'delete from %s where %s in (%s);' % (self.tbName, self.defaultKey, ','.join(values))
        DEBUG_MSG('db::_execSaveDel sql: %s' % sql)
        KBEngine.executeRawDatabaseCommand(sql, callback)

    def _execSaveAdd(self, maxRows):
        """
        执行存表操作：添加行，新添加行其自增id还是为0，所以不要用id作为唯一key管理数据。
        """
        if len(self.newDatas) == 0:
            return

        def callback(result, rows, insertid, error):
            if error:
                ERROR_MSG('db::_execSaveDel error: %s' % error)
            else:
                DEBUG_MSG('db::_execSaveDel success')

        i = 0
        values = []
        for k in list(self.newDatas.keys()):
            i += 1
            data = self.newDatas[k]
            del self.newDatas[k]
            
            line = []
            for filedName in self.filedKeysWithoutId:
                val = data[filedName]
                # DEBUG_MSG('<--filedName: %s, val %s, isStr: %s' % (filedName, val, isinstance(val, str)))
                if isinstance(val, str):
                    val = val.replace('"', '\"').replace("'", '\"')
                    line.append("'%s'" % val)
                else:
                    line.append('%s' % val)

            values.append('(%s)' % ','.join(line))

            if i >= maxRows:
                break
                
        sql = 'insert into %s (%s) values %s;' % (self.tbName, self.filedKeysStrWithoutId, ','.join(values))
        DEBUG_MSG('db::_execSaveAdd sql: %s' % sql)
        KBEngine.executeRawDatabaseCommand(sql, callback)

    def _execSaveUpdate(self, maxRows):
        """
        更新值改变的数据

        注意：即使一行数据中只有一个字段的值改变了，整行数据都会被更新。

        mysql批量更新数据方法：
        一、replace into table_name (id, filed1, filed2) values (1, xx, xx), (2, xx, xx);
        二、insert into table_name (id, filed1, filed3) values (1, xx, xx), (2, xx, xx) on duplicate key update filed1=values(filed1), filed2=values(filed2);
        三、
            update tableName
            set orderId = case id
                when 1 then 3
                when 2 then 4
                when 3 then 5
            end,
            title = case id
                when 1 then 'New Title 1'
                when 2 then 'New Title 2'
                when 3 then 'New Title 3'
            end
            where id in (1,2,3);

        replace into  和 insert into on duplicate key update的不同在于：
            replace into 操作本质是对重复的记录先delete 后insert，如果更新的字段不全会将缺失的字段置为缺省值，用这个要悠着点否则不小心清空大量数据可不是闹着玩的。
            insert into 则是只update重复记录，不会改变其它字段。
        """

        if len(self.updateDatas) == 0:
            self._execSaveAdd(maxRows)
            return

        def callback(result, rows, insertid, error):
            if error:
                ERROR_MSG('db::_execSaveUpdate error: %s' % error)
            else:
                DEBUG_MSG('db::_execSaveUpdate success')
                self._execSaveAdd(maxRows)
                
        
        # region 方式三的实现
        keys = set()
        sqlBlock = {}

        i = 0
        for k in list(self.updateDatas.keys()):
            i += 1
            line = self.updateDatas[k]
            del self.updateDatas[k]

            keys.add(line[self.defaultKey])
            for filedName in self.filedKeysWithoutId:
                if filedName != self.defaultKey:
                    val = line[filedName]

                    if isinstance(val, str):
                        val = val.replace('"', '\"').replace("'", '\"')
                        val = "'%s'" % val
                    else:
                        val = '%s' % val

                    sqlBlock.setdefault(filedName, []).append('when %s then %s' % (line[self.defaultKey], val))

            if i >= maxRows:
                break

        sql = 'update %s set' % self.tbName
        for k in sqlBlock:
            sql += ' %s = case %s ' % (k, self.defaultKey)
            sql += ' '.join(sqlBlock[k])
            sql += ' end,'
        sql = sql[:-1] + ' where %s in (%s);' % (self.defaultKey, str(list(keys))[1:-1])
        # endregion

        # region 方式一实现的批量更新。有个很严重的问题，新加的数据在执行_execSaveAdd没有获得自增id，默认为0，导致后面更新数据是id都是0，每次都是新插入一行。
        # 获得除id外的所有键值
        # allLineValues = []
        # for k in list(self.updateDatas.keys()):
        #     line = self.updateDatas[k]
        #     del self.updateDatas[k]

        #     # 按keys的键值顺序读取出数据
        #     values = []
        #     for k in self.filedKeys:
        #         # values.append('%s' % line[k])
        #         val = line[k]
        #         print('--> k, v: %s, %s' % (k, val))
        #         if isinstance(val, str):
        #             val = val.replace('"', '\"').replace("'", '\"')
        #             values.append("'%s'" % val)
        #         else:
        #             values.append('%s' % val)
                
        #     allLineValues.append('(%s)' % ','.join(values))

        # sql = 'replace into %s (%s) values %s;' % (self.tbName, self.filedKeysStr, ','.join(allLineValues))

        DEBUG_MSG('db::_execSaveUpdate sql: %s' % sql)
        KBEngine.executeRawDatabaseCommand(sql, callback)

    def getLineObj(self, defaultKeyVal):
        """
        优先从缓存池中获取行对象
        """
        if len(self.tableLinePool) > 0:
            line = self.tableLinePool.pop()
        else:
            line = TableLine()
            line.defaultKey = self.defaultKey
        # 数值重置
        for k in self.filedDict:
            line[k] = self.filedDict[k].defaultVal

        line[self.defaultKey] = defaultKeyVal
        self[defaultKeyVal] = line
        return line

    def putLineObj(self, line: TableLine):
        """
        将行对象添加到缓存池中
        """
        if line.dbTable is not None:
            line.dbTable = None
            self.tableLinePool.append(line)

    def _searchItem(self, key):
        def sqlCallback(result, rows, insertid, error):
            if error:
                ERROR_MSG('db::_searchItem error: %s' % error)
            else:
                DEBUG_MSG('db::_searchItem filedNames: %s' % str(self.filedNames))
                for items in result:
                    line = TableLine()
                    line.defaultKey = self.defaultKey
                    
                    for i, filedName in enumerate(self.filedNames):
                        line[filedName] = self.filedDict[filedName].convertFunc(items[i])
                        
                    self._setitem(line[self.defaultKey], line)

                    # 处理批量查找同个数据的请求
                    callbacks = self.searchItemRequest[key]
                    for callback in callbacks:
                        callback(dict.__getitem__(self, key))
                    del self.searchItemRequest[key]

        sql = 'select %s from %s where %s=%s;' % (','.join(self.filedNames), self.tbName, self.defaultKey, key)

        DEBUG_MSG('db::_searchItem sql: %s' % sql)
        KBEngine.executeRawDatabaseCommand(sql, sqlCallback)

    def getItem(self, key, callback):
        """
        根据key拿取数据，如果当前缓存中没有数据，则会去数据库中查找
        """
        if key in self:
            callback(dict.__getitem__(self, key))
        else:
            isNotSearching = key not in self.searchItemRequest
            self.searchItemRequest.setdefault(key, []).append(callback)
            if isNotSearching:
                self._searchItem(key)
    
    # region 重写内部方法
    def __getitem__(self, key) -> TableLine:
        if key in self:
            return dict.__getitem__(self, key)
        else:
            return None

    def __setitem__(self, key, value: TableLine):
        value.dbTable = self

        if key in self:
            oldVal = self[key]
            hasExchange = False
            for k in oldVal:
                if k in value and oldVal[k] != value[k]:
                    hasExchange = True
                    break

            if hasExchange:
                self.updateDatas[key] = value
        else:
            self.newDatas[key] = value

        if key in self.delDatas:
            del self.delDatas[key]

        dict.__setitem__(self, key, value)

    def _setitem(self, key, value: TableLine):
        """
        从数据库中加载表的时候用
        """
        value.dbTable = self
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        if key in self.newDatas:  # 如果在newDatas里面，说明该行还没有入库
            self.putLineObj(self.newDatas[key])
            del self.newDatas[key]
        elif key in self:
            self.delDatas[key] = self[key]

        dict.__delitem__(self, key)

        if key in self.updateDatas:
            del self.updateDatas[key]

    def __len__(self):
        return dict.__len__(self)

    def __contains__(self, key):
        return dict.__contains__(self, key)
    # endregion

    def _setLineUpdate(self, keyVal):
        """
        改变行内容

        只能改变已经存盘的数据
        """
        if keyVal in self and keyVal not in self.newDatas:
            self.updateDatas[keyVal] = self[keyVal]


class TableLine(dict):

    def __init__(self, *args):
        dict.__init__(self, args)
        self.dbTable: DBTable = None
        self.defaultKey = None
        
    def __getitem__(self, key) -> Any:
        return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if self.dbTable is not None:
            if key == self.defaultKey:  # 如果已经绑定了dbTable则不能修改主键的值
                ERROR_MSG('db::TableLine __setitem__ error can not modify defaultKey: %s' % key)
                return
            # 行数据更新，通知表进行记录
            self.dbTable._setLineUpdate(self[self.defaultKey])
    
    def __delitem__(self, key):
        ERROR_MSG('db::TableLine error can not use del')

    def __len__(self):
        return dict.__len__(self)

    def __contains__(self, key):
        return dict.__contains__(self, key)
        
    
