#coding:utf-8
import os
import sqlite3
import time


def creatdb_new(filepath,string):#输入路径和sql语句，输出:无,,,,需要删除，不再使用
    # 创建数据库和表
    if os.path.exists(filepath + '/test_new.db'):  # 判断当前源文件的文件夹下是否存在，
        os.remove(filepath + '/test_new.db')  # 如果存在就删除这个数据库，
    global conn
    global curs
    conn = sqlite3.connect(filepath + '/test_new.db')  # 无则创建一个test.db的数据库，
    curs = conn.cursor()
    if sqlite3.complete_statement(string):
        curs.execute(string)

def creatdb_new2(fileuri):#输入路径，输出：无
    # 创建数据库
    temptime = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    if os.path.exists(fileuri + '_'+temptime+'.db'):  # 判断当前源文件的文件夹下是否存在，
        os.remove(fileuri + '_'+temptime+'.db')  # 如果存在就删除这个数据库，
    global conn
    global curs
    conn = sqlite3.connect(fileuri + '_'+temptime+'.db')  # 无则创建一个test.db的数据库，
    curs = conn.cursor()


def creat_table(query):
    global conn
    global curs
    if sqlite3.complete_statement(query):
        curs.execute(query)

def creat_predfserv_match_tb():#20171226
    qurey = "CREATE TABLE IF NOT EXISTS predeservmatch(id integer primary key autoincrement, \
            origservname TEXT, \
            hillservname TEXT, \
            proto TEXT, \
            dstport1 TEXT, \
            newadd TEXT);"
    creat_table(qurey)
    insert2tb_predeservmatch()
    return 0

def creat_preservicetb():#netscreen用，20180313
    qurey = "CREATE TABLE IF NOT EXISTS preservice(id integer primary key autoincrement, \
            servicename TEXT, \
            protocoltype    TEXT, \
            srcport1    TEXT, \
            srcport2    TEXT, \
            dstport1    TEXT, \
            dstport2    TEXT);"
    creat_table(qurey)

    return 0


def creatdb(filepath):#需要删除，不再使用
    # 创建数据库和表
    if os.path.exists(filepath + '/test.db'):  # 判断当前源文件的文件夹下是否存在，
        os.remove(filepath + '/test.db')  # 如果存在就删除这个数据库，
    global conn
    global curs
    conn = sqlite3.connect(filepath + '/test.db')  # 无则创建一个test.db的数据库，
    curs = conn.cursor()

    #创建服务表
    curs.execute('''
        CREATE TABLE service(
            id integer primary key autoincrement,
            servicename TEXT,
            protocoltype    TEXT,
            srcport1    TEXT,
            srcport2    TEXT,
            dstport1    TEXT,
            dstport2    TEXT
        )
        ''')
    #创建地址簿表，
    curs.execute('\n'
                 '        CREATE TABLE addr_ip(\n'
                 '            id	integer primary key autoincrement,\n'
                 '            addr	TEXT,\n'
                 '            ip	TEXT\n'
                 '        )\n'
                 '        ')
    #创建地址簿与公网ip对关系表，
    curs.execute('\n'
                 '        CREATE TABLE addrname_pubip(\n'
                 '            id	integer primary key autoincrement,\n'
                 '            addrname	TEXT,\n'
                 '            priip	TEXT,\n'
                 '            pubip	TEXT\n'
                 '        )\n'
                 '        ')
    # 创建完成
    return 0



def insert2table_service(tuple):
    query = 'INSERT INTO ' \
            'service(servicename,protocoltype,srcport1,srcport2,dstport1,dstport2) VALUES(?,?,?,?,?,?)'
    global curs, conn
    curs.execute(query, tuple)
    conn.commit()


def insert2table_new(query,list):#输入语句、变量，输出：无。
    global conn
    global curs
    if sqlite3.complete_statement(query):
        curs.execute(query,list)
    conn.commit()


def insert2tb_predeservmatch():#20171226
    global conn
    global curs
    predeservice=[['ssh','SSH','tcp','22','0'], \
                  ['www','HTTP','tcp','80','0'], \
                  ['ldap','LDAP','tcp','389','0'], \
                  ['tacacs','TACACS','tcp','49','1'], \
                  ['snmp','SNMP','udp','161','0'], \
                  ['snmptrap','SNMP','udp','161','0'], \
                  ['tftp','TFTP','udp','69','0'], \
                  ['ntp','NTP','udp','123','0'], \
                  ['syslog','SYSLOG','udp','514','0'], \
                  ['netbios-ns','NBNAME','udp','137','0'], \
                  ['netbios-dgm','NBDS','udp','138','0'], \
                  ['netbios-ssn','SMB','tcp','139','0'], \
                  ['https','HTTPS','tcp','443','0'], \
                  ['radius','RADIUS','udp','1812','0'], \
                  ['telnet','TELNET','tcp','23','0'], \
                  ['sqlnet','SQLNETv2','tcp','1521','0'], \
                  ['ftp-data','FTP','tcp','20','0'], \
                  ['ftp','FTP','tcp','21','0']]
    query = "insert into predeservmatch(origservname,hillservname,proto,dstport1,newadd) values(?,?,?,?,?);"
    for tmplist in predeservice:
        if sqlite3.complete_statement(query):
            curs.execute(query, tmplist)
    conn.commit()


def fetchallfrom(query):
    global curs, conn
    if sqlite3.complete_statement(query):
        curs.execute(query)
    tmplist=list(curs.fetchall())
    return tmplist

def fetch_service():#提供2个数据，一个是servicename的list，一个是全部表项的list
    query = 'select distinct servicename from service '#取出表servicename中的所有servicename,
    global curs, conn
    curs.execute(query)
    service_name_list=list(curs.fetchall())
    service_config=''
    if service_name_list:
        for atuple in service_name_list:
            query='select * from service where servicename="%s" ' % list(atuple)[0]#服务名称
            curs.execute(query)
            service_content_list=list(curs.fetchall())
            if service_content_list:
                for btuple in service_content_list:
                    if list(btuple):
                        service_content=list(btuple)
                        ser_name=service_content[1]
                        protocol=service_content[2]
                        srcport1=service_content[3]
                        srcport2=service_content[4]
                        dstport1 = service_content[5]
                        dstport2 = service_content[6]
                        service_config+='service '+ser_name+'\n '+protocol+' dst-port '+dstport1+' '+dstport2+' src-port '+srcport1+ ' '+srcport2+'\nexit\n'
    # conn.commit()
    return service_config

def insert2db(tuple):
    query = 'INSERT INTO addr_ip(addr,ip) VALUES(?,?)'
    global curs, conn
    curs.execute(query, tuple)
    conn.commit()


def insert_pubip2db(tuple):
    query = 'INSERT INTO addrname_pubip(addrname,pubip) VALUES(?,?)'
    global curs, conn
    curs.execute(query, tuple)
    conn.commit()

def update2db(string):
    global curs, conn
    query = 'UPDATE addrname_pubip SET priip = ( select ip from addr_ip where addrname_pubip.addrname=addr_ip.addr) where addrname=?'
    curs.execute(query, (string,))
    conn.commit()

