#-*- coding: utf8 -*-
from tkinter.filedialog import askopenfilename
import time
import sqlite3
import os
import glob
import xlrd
import tkinter
from tkinter import *


def choose2fir():
    filewin = Toplevel(root)
    label = Label(filewin, text="请先选择原设备和原文件！！！")
    label.pack()


def btnClicked():#选择文件按钮
    global fname
    fname = askopenfilename(filetypes=(("All  files", "*.*"), ("HTML files", "*.html;*.htm"), ("All files", "*.*")))
    label3.config(text=fname)

def trans_btnclicked():#转换配置函数
    if label2.cget('text') and label3.cget('text'):
        done_label.config(text='正在转换配置，请等待......')
        #print('26')
        if label2.cget("text") == "CISCO":
            #print('27')
            isciscoasa()
        elif label2.cget("text") == "JUNOS":
            isjunos()
        elif label2.cget("text") == "NETSCREEN":
            pass
        elif label2.cget("text") == "F5":
            pass
        elif label2.cget("text") == "HUAWEI":
            pass
        elif label2.cget("text") == "H3C":
            pass
        elif label2.cget("text") == "EXCEL":
            isexcel()
        else:
            pass
    else:
        choose2fir()
    print('转换完成！')
    done_label.config(text='转换完成！')
    return 0

def test_btnclicked():
    print(label2.cget("text"))#获得标签当前的text值。

def option1():
    #print('hello menu')
    label2.config(text=var.get())
    #print(label2.cget('text'))
    #print(var.get())

def option2():
    # print('hello menu')
    label2.config(text=var.get())

def option3():
    label2.config(text=var.get())

def option4():
    label2.config(text=var.get())

def option5():
    label2.config(text=var.get())

def option6():
    label2.config(text=var.get())



def creatdb(list):
    # 创建数据库和表
    if os.path.exists(os.path.split(list)[0] + '/test.db'):  # 判断当前源文件的文件夹下是否存在，
        os.remove(os.path.split(list)[0] + '/test.db')  # 如果存在就删除这个数据库，
    global conn
    global curs
    conn = sqlite3.connect(os.path.split(list)[0] + '/test.db')  # 无则创建一个test.db的数据库，
    curs = conn.cursor()
    curs.execute('''
        CREATE TABLE addr_ip(
            id	integer primary key autoincrement,
            addr	TEXT,
            ip	TEXT
        )
        ''')
    curs.execute('''
        CREATE TABLE addrname_pubip(
            id	integer primary key autoincrement,
            addrname	TEXT,
            priip	TEXT,
            pubip	TEXT
        )
        ''')
    # 创建完成
    return 0



def transaddr(list):  # 转换服务				#list是words,
    global addrstr
    straddrip = ''
    words = list[i].split()  # 将第i行分割成一个个元素放在列表words中，list[i]是一个字符串(文件中的一行)
    m = words.index('address')  # 获得’‘索引值
    straddrname = words[m + 1]  # 获得addr名称
    addrstr = addrstr + 'address ' + straddrname + '\n'
    if 'dns-name' in words:
        straddrip = words[m + 3]
        addrstr = addrstr + ' host ' + straddrip + '\n'
    else:
        try:
            straddrip = words[m + 2]
        except :
            print(words)
            exit()
        addrstr = addrstr + ' ip ' + straddrip + '\n'
    addrstr = addrstr + 'exit\n'
    tux=straddrname,straddrip
    #print(tux)
    query = 'INSERT INTO addr_ip(addr,ip) VALUES(?,?)'
    global curs,conn
    curs.execute(query, tux)
    conn.commit()
    tux = None
    return 0


def transaddrgroup(list):
    global i
    global addrgroupstr
    straddrip=''
    words=list[i].split()        #将第i行分割成一个个元素放在列表words中，list[i]是一个字符串(文件中的一行)
    m=words.index('address-set')#获得’‘索引值
    straddrname=words[m+1]#获得addr-set的名称
    addrgroupstr =addrgroupstr+ 'address ' + straddrname + '\n'
    while 1:
        if (straddrname in words):
            addrgroupstr=addrgroupstr+' member '+words[m+3]+'\n'
            i+=1
            words = list[i].split()
        else:
            i = i - 1
            break
    addrgroupstr=addrgroupstr+'exit\n'

    return 0


def transservice(list):
    '''
    情况一：
    set applications application Service_3389 term Service_3389 protocol tcp
    set applications application Service_3389 term Service_3389 source-port 0-65535
    set applications application Service_3389 term Service_3389 destination-port 3389-3389
    '''
    global i
    strservice=''
    words = list[i].split()
    m = words.index('application')
    servname = words[m + 1]
    namelist=['SNMP','SSH']
    if servname in namelist:
        return 0
    #print(i)
    m = words.index('protocol')
    strserpro = words[m + 1]#看协议是TCP还是UDP
    i = i + 1   #读下一行
    while servname in words:
        words = list[i].split()
        if 'destination-port' in words:
            n = words.index('destination-port')
            strport = words[n + 1]
            preport = ['ssh', 'telnet', 'tftp']
            afport = ['22', '23', '69']
            for j in range(len(preport)):
                if strport == preport[j]:
                    strport = afport[j]
                    break
            strservice += 'service ' + servname + '\n'
            strport=strport.replace('-',' ')

            strservice += ' ' + strserpro + ' dst-port ' + strport + '\n' + 'exit\n'
        i=i+1
    i=i-2
    #print(i)
    return strservice


def transpolicy(list):
    global i
    strpolicy=''
    strsrcz = ''
    strdstz = ''
    strsrcaddr = ''
    strdstaddr = ''
    strservice = ''
    straction = ''
    strnatname = ''
    strdescrip=''
    words = list[i].split()
    if ('description' in list[i]):
        temp = list[i].replace(' ', '-')
        temp = temp.replace('"', '')
        strdescrip = temp[temp.find('description') + 11:]
        m = words.index('description')
        strnatname = words[m - 1]
        strsrcz = words[m - 5]
        strdstz = words[m - 3]
        namestr = ' name ' + strnatname + '\n'
        namestr = ' description ' + strdescrip +'\n'+ namestr
        strpolicy = strpolicy + ' src-zone ' + strsrcz + '\n dst-zone ' + strdstz + '\n'
    elif ('source-address' in words):
        m = words.index('source-address')
        strnatname = words[m - 2]
        strsrcaddr = words[m + 1]
        strsrcz = words[m - 6]
        strdstz = words[m - 4]
        namestr = ' name ' + strnatname + '\n'
        strpolicy =strpolicy+ ' src-zone ' + strsrcz + '\n dst-zone ' + strdstz + '\n src-addr ' + strsrcaddr + '\n'
    i += 1
    words = list[i].split()
    while (strnatname in words):
        if ('source-address' in words):
            m = words.index('source-address')
            strsrcaddr = words[m + 1]
            strpolicy = strpolicy + ' src-addr ' + strsrcaddr + '\n'
        elif ('destination-address' in words):
            m = words.index('destination-address')
            strdstaddr = words[m + 1]
            strpolicy = strpolicy + ' dst-addr ' + strdstaddr + '\n'
        elif ('application' in words):
            m = words.index('application')
            strservice = words[m + 1]
            strpolicy = strpolicy + ' service ' + strservice + '\n'
        elif ('then' in words):
            if ('session-init' in words):
                strpolicy = strpolicy + ' log session-start\n'
            elif ('session-close' in words):
                strpolicy = strpolicy + ' log session-end\n'
            else:
                m = words.index('then')
                strpolicyction = words[m + 1]
                strpolicy = '\nrule\n action ' + straction + '\n'+strpolicy+namestr
        i = i + 1
        words = list[i].split()
    i = i - 1
    strpolicy = strpolicy + 'exit\n'
    return strpolicy


def transGpolicy(list):
    global i
    strgplicy=''
    strsrcaddr = ''
    strdstaddr = ''
    strservice = ''
    straction = ''
    strnatname = ''
    words = list[i].split()
    if ('description' in list[i]):
        temp = list[i].replace(' ', '-')
        temp = temp.replace('"', '')
        strdescrip = temp[temp.find('description') + 11:]
        m = words.index('description')
        strnatname = words[m - 1]
        namestr = ' name ' + strnatname + '\n'
        namestr = ' description ' + strdescrip +'\n'+ namestr
    elif ('source-address' in words):
        m = words.index('source-address')
        strnatname = words[m - 2]
        strsrcaddr = words[m + 1]
        namestr = ' name ' + strnatname + '\n'
        strgplicy= 'src-addr ' + strsrcaddr + '\n'
    i = i + 1
    words = list[i].split()
    while (strnatname in words):
        # print(words)
        # print(strnatname)
        if ('source-address' in words):
            m = words.index('source-address')
            strsrcaddr = words[m + 1]
            strgplicy = strgplicy + ' src-addr ' + strsrcaddr + '\n'
        elif ('destination-address' in words):
            m = words.index('destination-address')
            strdstaddr = words[m + 1]
            strgplicy = strgplicy + ' dst-addr ' + strdstaddr + '\n'
        elif ('application' in words):
            m = words.index('application')
            strservice = words[m + 1]
            strgplicy = strgplicy + ' service ' + strservice + '\n'
        elif ('then' in words):
            if ('session-init' in words):
                strgplicy = strgplicy + ' log session-start\n'
            elif ('session-close' in words):
                strgplicy = strgplicy + ' log session-end\n'
            else:
                m = words.index('then')
                straction = words[m + 1]
                strgplicy = '\nrule\n action ' + straction + '\n'+strgplicy + namestr
        i += 1
        words = list[i].split()
    # print(i)
    # print(words)
    i -= 1
    strgplicy += 'exit\n'
    return strgplicy


def transnatpool(list):
    natpool =''
    straddrip = ''

    words = list[i].split()  # 将第i行分割成一个个元素放在列表words中，list[i]是一个字符串(文件中的一行)
    # print(i)
    m = words.index('address')  # 获得’‘索引值
    straddrname = words[m - 1]  # 获得addr名称
    if ('port' in words):
        port = words[m + 2]
        #natpool = 'address ' + straddrname
        #natpool = natpool + ' port ' + straddrip
        #natpool = natpool + ' exit\n'
        #hd.writelines(natpool)
        tux = straddrname, port    #待插入的数据
        # print(tux)
        query = 'INSERT INTO addr_ip(addr,ip) VALUES(?,?)'
        global curs, conn
        curs.execute(query, tux)
        conn.commit()
        tux = None
    else:
        straddrip = words[m + 1]
        natpool = 'address ' + straddrname + '\n'
        natpool = natpool + ' ip ' + straddrip + '\n'
        natpool = natpool + 'exit\n'
        #ed.writelines(natpool)
        tux = straddrname, straddrip
        # print(tux)
        query = 'INSERT INTO addr_ip(addr,ip) VALUES(?,?)'
        curs.execute(query, tux)
        conn.commit()
        tux = None
    return natpool


def transsnat(list):
    global i
    snat=''
    strsrcz = ''
    strdstz = ''
    strsrcip = ''
    strdstaddr = ''
    strservice = ''
    straction = ''
    strnatname = ''
    srcipbookname=''
    dstipbookname=''
    srcipbookcontent=''
    dstipbookcontent=''
    words = list[i].split()
    if ('source-address' in words):
        m = words.index('source-address')
        strnatname = words[m - 2]
        strsrcip = words[m + 1]
        srcipbookname = strnatname + '-srcip'
        srcipbookcontent = 'address ' + strnatname + '-srcip\n' + ' ip ' + strsrcip + '\nexit\n'
    i = i + 1
    words = list[i].split()#下一行
    flagk=0#是否有多个destaddr的flag
    j=i
    while (strnatname in words):
        if ('source-address' in words):
            m = words.index('source-address')
            strnatname = words[m - 2]
            strsrcip = words[m + 1]
            srcipbookcontent+='address ' + strnatname + '-srcip\n' + ' ip ' + strsrcip + '\nexit\n'
        elif ('destination-address' in words):
            m = words.index('destination-address')
            strdstaddr = words[m + 1]
            if strdstaddr=='0.0.0.0/0':
                strdstaddr='any'
            else:
                dstipbookname=strnatname+'-dstip'
                dstipbookcontent+='address ' + strnatname + '-dstip\n' + ' ip ' + strdstaddr + '\nexit\n'
        elif ('then' in words):
            snat += srcipbookcontent + dstipbookcontent
            if strdstaddr=='any':
                snat += 'nat\nsnatrule from ' + srcipbookname + ' to any service any trans-to '
            else:
                snat += 'nat\nsnatrule from ' + srcipbookname + ' to ' + dstipbookname + ' service any trans-to '
            if ('interface' in words):
                snat +='eif interface mode dynamicport sticky log\nexit\n'
            else:
                m = words.index('then')
                #print(i)
                straction = words[m + 3]
                snat +='address-book '+ straction + ' mode dynamicport sticky\nexit\n'
        j += 1
        words = list[j].split()
    i=j-1
    #i -= 1
    return snat


def transdnat(list):
    global i
    dnat=''
    strdnatpool=''
    strdstz=''
    strsrcip=''
    strdstaddr=''
    strservice=''
    strport=''
    strnatname=''
    strdesc=''
    strdstaddr32=''
    words=list[i].split()
    if ('rule' in words):
        m=words.index('rule')
        strnatname=words[m+1]
    while ( strnatname in words):
        if ('source-address' in words):
            pass
        elif ('description' in words):
            temp=list[i].replace(' ','-')
            temp=temp.replace('"','')
            strdesc=temp[temp.find('description')+11:]
        elif ('destination-address' in words):
            m=words.index('destination-address')
            strdstaddr32=words[m+1]#保存的是公网ip
            strdstaddr=words[m+1].split('/')[0]		#将/32去掉了
        elif ('destination-port' in words):
            m=words.index('destination-port')
            strport=words[m+1]
            dnat += 'service tcp-' + strport + '\n'
            dnat += ' tcp dst-port ' + strport + '\nexit\n'
        elif ('then' in words):
            m=words.index('then')
            strdnatpool=words[m+3] #与公网对应的私网地址簿名称
            dnat = dnat + 'nat\ndnatrule from any to ' + strdstaddr + ' service '
            if ( strport == ''):
                dnat=dnat+'any trans-to '+strdnatpool+' description '+strnatname+strdesc+'\nexit\n'
            else:
                dnat+='tcp-'+strport+' trans-to '+strdnatpool+' port '+strport+' description '+strnatname+strdesc+'\nexit\n'
            tux = strdnatpool, strdstaddr32  # print(tux)
            query = 'INSERT INTO addrname_pubip(addrname,pubip) VALUES(?,?)'
            global curs, conn
            curs.execute(query, tux)
            conn.commit()
            tux = None
            query = 'UPDATE addrname_pubip SET priip = ( select ip from addr_ip where addrname_pubip.addrname=addr_ip.addr) where addrname=?'
            curs.execute(query, (strdnatpool,))
            conn.commit()
        i=i+1
        words=list[i].split()
    i=i-1
    return dnat


def transroute(list):
    route=''
    words = list[i].split()
    m = words.index('route')  # 获得’‘索引值
    strdst = words[m + 1]
    if 'next-hop' in words:
        n = words.index('next-hop')
        strnexthop = words[n + 1]
        route = route +' ip route ' + strdst + ' ' + strnexthop + '\n'
    return route




def en_mouth_to_num(string):
    en_mouth=['January','February','March','April','May','June','July','August','September','October','November','December']
    num_mouth=['01','02','03','04','05','06','07','08','09','10','11','12']
    m = en_mouth.index(string)
    temstring = num_mouth[m]
    return temstring





def asa_trans_schedu(list):
    global i
    string = 'schedule ' + list[1] + '\n' #list[1]中是对象名字
    k = i
    while (('!' not in srcfile[k].split())):
        k += 1
    #以上while循环结束时，srcfile[k]中含有！，
    i += 1
    while (i < k):
        list = srcfile[i].split()
        if 'absolute' in list:
            m = list.index('start')
            starttime = list[m+1]
            startday = list[m+2]
            startmouth = list[m + 3]
            startmouth = en_mouth_to_num(startmouth)
            startyear = list[m + 4]
            n = list.index('end')
            endtime = list[n + 1]
            endday = list[n + 2]
            endmouth = list[n + 3]
            endmouth = en_mouth_to_num(endmouth)
            endyear = list[n + 4]
            string = string + ' absolute start ' + startmouth + '/' + startday + '/' + startyear + ' ' + starttime
            string = string + ' end ' + endmouth + '/' + endday + '/' + endyear + ' ' + endtime + '\n'
            string = string + 'exit\n'
        i += 1
    return string


def asa_exchangemask(string):
    exchange_mask = lambda mask: sum(bin(int(i)).count('1') \
                                     for i in mask.split('.'))
    string1 = str(exchange_mask(string))
    return string1




def asa_trans_standard_acl(list):
    global i
    m= list.index('standard')
    aclname = list[m-1]
    action = list[m+1]
    string = '#This is ' + aclname + '\nrule' + '\n action '+ action + '\n'
    if 'host' in list:
        srcip = list[m+3]
        srcmask = '32'
    else:
        srcip = list[m+2]
        srcmask = list[m+3]
        srcmask = asa_exchangemask(srcmask)
    string = string + ' src-ip ' + srcip + '/' + srcmask + '\n'
    while 1:
        if aclname in srcfile[i+1].split() and action in srcfile[i+1].split():
            i += 1
            list = srcfile[i].split()
            m = list.index('standard')
            if 'host' in list:
                srcip = list[m + 3]
                srcmask = '32'
            else:
                srcip = list[m + 2]
                srcmask = list[m + 3]
                srcmask = asa_exchangemask(srcmask)
            string = string + ' src-ip ' + srcip + '/' + srcmask + '\n'
        else:
            string = string + ' dst-addr any\n service any\nexit\n\n'
            break
    return string


def asa_acl_src_dst_addr(list,y):   #y是地址串最后一个元素的下标，
    string2 = ''
    srcip=''
    dstip=''
    j = 5 #从下标为5的元素为源地址的开始，
    #print(y)
    if y-j+1 ==2:
        #例如：icmp any any
        #tcp any any
        string2 = ' src-addr any\n dst-addr any\n'
    elif y-j+1 ==3:
        #any host 41.248.98.98
        #host 172.26.136.148 any
        #any 172.26.158.100 255.255.255.252
        if list[5] =='any':
            #any host 41.248.98.98
            srcip='any'
            if list[6] =='host':
                dstip=list[7]+'/32'
                string2 = ' src-addr ' + srcip + '\n dst-ip ' + dstip + '\n'
            elif list[6] == 'any':
                dstip='any'
                string2 = ' src-ip ' + srcip + '\n dst-addr ' + dstip + '\n'
            elif list[6] == 'object':
                pass
            else:
                dstip = list[6] + '/' + asa_exchangemask(list[7])
                string2 = ' src-ip '+srcip+'\n dst-ip '+dstip+'\n'
        elif list[5] == 'host':
            # host 172.26.136.148 any
            srcip=list[6]+'/32'
            if list[7] == 'any':
                dstip='any'
                string2 = ' src-ip ' + srcip + '\n dst-addr ' + dstip + '\n'
            elif list[7] == 'host':
                pass
            elif list[7] == 'object':
                pass
            else:
                dstip = list[7] + '/' + asa_exchangemask(list[8])
                string2 = ' src-ip '+srcip+'\n dst-ip '+dstip+'\n'
        elif list[5] == 'object':
            pass
        else:
            srcip=list[5]+'/'+ asa_exchangemask(list[6])
            if list[7] == 'any':
                dstip = 'any'
                string2 = ' src-ip ' + srcip + '\n dst-addr ' + dstip + '\n'
            elif list[7] == 'host':
                pass
            elif list[7] == 'object':
                pass
            else:
                dstip = list[7] + '/' + asa_exchangemask(list[8])
                string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
    elif y-j+1 ==4:
        #eg.tcp 172.26.149.32 255.255.255.224 172.26.141.0 255.255.255.0
        #host 172.25.241.56 host 172.26.156.1
        #tcp 10.44.0.0 255.255.0.0 host 172.26.140.3
        if list[5] == 'any':
            pass
        elif list[5] == 'host':
            srcip = list[6] + '/32'
            if list[7] == 'any':
                dstip = 'any'
                string2 = ' src-ip ' + srcip + '\n dst-addr ' + dstip + '\n'
            elif list[7] == 'host':
                dstip=list[8]+'/32'
                string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
            elif list[7] == 'object':
                pass
            else:
                dstip = list[7] + '/' + asa_exchangemask(list[8])
                string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
        elif list[5] == 'object':
            pass
        else:
            srcip=list[5]+'/'+ asa_exchangemask(list[6])
            if list[7] == 'any':
                pass
            elif list[7] == 'host':
                dstip = list[8] + '/32'
                string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
            elif list[7] == 'object':
                pass
            else:
                dstip = list[7] + '/' + asa_exchangemask(list[8])
            string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
    return string2

def asa_acl_aftertcpudp(list):
    string3=''
    serviceend=''
    global string4

    if 'eq' in list:
        m = list.index('eq')
        string3 = string3 + asa_acl_src_dst_addr(list, (m - 1))  # 交给地址转换函数
        service = list[m + 1]
        if service == 'www':
            service = 'http'
        elif service =='ftp-data':
            service='20'
        service = service.upper()
        if service == 'SQLNET':
            service = 'SQLNETv2'
        if service[0].isnumeric():#为生成service做准备，
            string4 = string4 + service + '\n'
            service='tcp-' + service
        string3 = string3 + ' service ' + service + '\n'
        if 'time-range' in list:
            m = list.index('time-range')
            schedule = list[m + 1]
            string3 = string3 + ' schedule ' + schedule + '\n'
    elif 'range' in list:
        # extended permit tcp any host 172.26.158.2 range www 81
        m = list.index('range')
        string3 = string3 + asa_acl_src_dst_addr(list, (m - 1))  # 交给地址转换函数
        if list[m + 1] == 'www':
            servicestart = '80'
        elif list[m + 1] == 'ftp-data':
            servicestart = '20'
        elif list[m + 1] == 'ftp':
            servicestart = '21'
        else:
            servicestart = list[m + 1]
        if list[m + 2] == 'ftp':
            serviceend = '21'
        elif list[m + 2] == 'ssh':
            serviceend = '22'
        else:
            serviceend =list[m + 2]
        service = servicestart + '-' + serviceend  # list[m+2]是range中的结束端口
        string4= string4 + service + '\n'
        service='tcp-'+service
        string3 = string3 + ' service ' + service + '\n'
        if 'time-range' in list:
            m = list.index('time-range')
            schedule = list[m + 1]
            string3 = string3 + ' schedule ' + schedule + '\n'
    elif 'time-range' in list:  # 这一行没有端口，是tcp-any，
        # extended permit tcp host 172.26.73.52 host 172.26.153.17 time-range 20181231
        m = list.index('time-range')
        service = 'tcp-any'
        string3 = string3 + asa_acl_src_dst_addr(list, (m - 1))  # 交给地址转换函数
        string3 = string3 + ' service ' + service + '\n'
        schedule = list[m + 1]
        string3 = string3 + ' schedule ' + schedule + '\n'
    else:
        # tcp 172.26.149.32 255.255.255.224 172.26.141.0 255.255.255.0
        # tcp any any
        if list[4]=='tcp':
            service = 'tcp-any'
        else:
            service = 'udp-any'
        string3 = string3 + asa_acl_src_dst_addr(list, (len(list) - 1))
        string3 = string3 + ' service ' + service + '\n'

    return string3


def asa_trans_extend_acl(list):
    global i
    string=''
    servicestart=''
    m = list.index('extended')
    aclname = list[m - 1]
    action = list[m + 1]
    if aclname in srcfile[i-1].split():
        pass
    else:
        string = '#This is ' + aclname + '\n'
    #string = string + '#line\n'
    string= string + 'rule\n action ' + action + '\n'

    j = 4
    if list[j] == 'icmp':  # 判断下标为4的元素是icmp
        service = 'ICMP'
        if 'time-range' in list:
            m = list.index('time-range')
            string = string + asa_acl_src_dst_addr(list, (m- 1))
            string = string + ' service ' + service + '\n'
            schedule = list[m + 1]
            string = string + ' schedule ' + schedule + '\n'
        else:
            string = string + asa_acl_src_dst_addr(list, (len(list) - 1))
            string = string + ' service '+service+'\n'
        string = string + 'exit\n\n'
    elif list[j] == 'ip':
        service = 'any'
        if 'time-range' in list:
            m = list.index('time-range')
            string = string + asa_acl_src_dst_addr(list, (m- 1))
            string = string + ' service ' + service + '\n'
            schedule = list[m + 1]
            string = string + ' schedule ' + schedule + '\n'
        else:

            string = string + asa_acl_src_dst_addr(list, (len(list) - 1))
            string = string + ' service ' + service + '\n'
        string = string + 'exit\n\n'
    elif list[j] == 'tcp':# 判断下标为4的元素是tcp
        #eg.permit tcp host 172.26.136.148 any eq https time-range 20171231
        #eg.permit tcp 172.26.149.32 255.255.255.224 172.26.141.0 255.255.255.0
        string = string + asa_acl_aftertcpudp(list)
        string = string + 'exit\n\n'
    #print(list[j])
    elif list[j] == 'udp': # 判断下标为4的元素是udp
        #print('653')
        string = string + asa_acl_aftertcpudp(list)
        string = string + 'exit\n\n'

    return string


def isciscoasa():
    global addrgroupstr
    addrgroupstr = ''
    global addrstr
    addrstr = ''
    global string4
    string4 = ''
    global fname
    fd = open(fname, 'r', encoding='utf-8')  # 打开源文件
    global srcfile
    srcfile = fd.readlines()  # 将源文件读取到列表srcfile中
    print(str(len(srcfile)) + '行')  # 源文件有这些行
    fd.close()  # 读取原文件结束

    schedu_str = ''
    standard_acl = ''
    extended_acl = ''
    global i
    i = 0
    # print(len(srcfile))	#srcfile[len(srcfile)-1]是最后一行
    while (i < len(srcfile)):
        words = srcfile[i].split()
        if 'time-range' in words and 'access-list' not in words:
            schedu_str =  schedu_str + asa_trans_schedu(words)
        elif 'object-group' in words and 'network' in words:
            pass
        elif 'access-list' in words and ('standard' in words ):
            standard_acl = standard_acl + asa_trans_standard_acl(words)
        elif 'access-list' in words and ('extended' in words):
            extended_acl = extended_acl + asa_trans_extend_acl(words)

        i += 1
    temptime = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    #fa = open('create_schdule_' + temptime + '.txt', 'w')
    #fa.writelines(schedu_str)
    #fa.close()

    fa = open('create_standardacl_' + temptime + '.txt', 'w')
    fa.writelines(standard_acl)
    fa.close()

    fa = open('create_extendedacl_' + temptime + '.txt', 'w')
    fa.writelines(extended_acl)
    fa.close()

    list4=string4.split('\n')
    list5=[]
    for fstr in list4:
        if fstr not in list5:
            list5.append(fstr)
    string5=''
    for fstr in list5:
        string5=string5+create_service(fstr)

    fa = open('create_service_' + temptime + '.txt', 'w')
    fa.writelines(string5)
    fa.close()
    return 0


def isjunos():
    #global strservice
    #global strpolicy
    #global strgpolicy
    #global natpool
    #global snat
    #global dnat
    #global route
    output=''
    global addrgroupstr
    addrgroupstr=''
    global addrstr
    addrstr=''
    global fname
    fd = open(fname, 'r', encoding='utf-8')  # 打开源文件
    srcfile = fd.readlines()  # 将源文件读取到列表srcfile中
    print(str(len(srcfile)) + '行')  # 源文件有这些行
    fd.close() #读取原文件结束

    creatdb(fname)

    global i
    i = 0
    # print(len(srcfile))	#srcfile[len(srcfile)-1]是最后一行
    while (i < len(srcfile)):
        words = srcfile[i].split()
        if ('set' in words and 'address-book' in words and 'address-set' in words):
             transaddrgroup(srcfile)
        elif ('set' in words and 'address-book' in words and 'address' in words):
             transaddr(srcfile)
        elif ('set' in words and 'junos-defaults' in words and 'applications' in words and 'application' in words):
            pass
        elif ('set' in words and 'applications' in words and 'application' in words):
            output = output + transservice(srcfile)
        elif ('set' in words and 'policies' in words and 'from-zone' in words):
            # print(words)
            output = output + transpolicy(srcfile)
        elif ('set' in words and 'policies' in words and 'global' in words):
            # print(words)
            output = output + transGpolicy(srcfile)
        elif ('set' in words and 'nat' in words and 'pool' in words and 'address' in words):
            # print(words)
            output = output + transnatpool(srcfile)
        elif ('set' in words and 'nat' in words and 'source' in words and 'rule-set' in words and 'rule' in words):
            # print(words)
            output = output + transsnat(srcfile)
        elif ('set' in words and 'nat' in words and 'destination' in words and 'rule-set' in words and 'rule' in words):
            # print(words)
            output = output + transdnat(srcfile)
        elif ('set routing-options static route' in srcfile[i]):
            output = output + transroute(srcfile)
        i = i + 1
    newfilename = ''
    newfilename = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    listsfile = os.path.split(fname)  # 将路径和文件名分开
    newfilename = listsfile[0] + '/' + newfilename + '.txt'  # 新文件为源文件在同一个文件夹下
    ed = open(newfilename, 'w')  # 打开转换后的文件
    ed.writelines(addrstr)
    ed.writelines(addrgroupstr)
    ed.writelines(output)
    ed.close()
    done_label.config(text='转换完成!')
    return 0


def fromcoltocli( i,ingress_interface,col3):
    col_list = [2, 7, 8,0]
    tempstr = ''
    if ingress_interface == 'vlan-if750':
        ingress_interface='vlan750'
    for j in col_list:  # 循环这些列，
        cell_value = sh.cell_value(i, j)  # 将（i,j）的单元格内容赋给cell_value
        if type(cell_value) is float:
            cell_value = int(cell_value)
        cell_value = str(cell_value)
        if j == 2:  # 这一列是公网ip
            tempstr = 'dnatrule ingress-interface xethernet1/3 from any to ' + cell_value + ' service ' + col3
        elif j == 7:  # 这一列是内网地址
            tempstr = tempstr + ' trans-to ' + cell_value
        elif j==8:
            if cell_value =='0':
                pass
            elif col3 =='ICMP':
                pass
            else:
                tempstr = tempstr + ' port ' + cell_value
        elif j == 0:  # 这一列是描述
            tempstr = tempstr + ' log description ' + cell_value + '\n'
    return tempstr


def create_service(string):#string是端口号
    '''
    2000或2000-2002
    :param string:
    :return:
    '''
    cstr = 'service tcp-' + string+'\n'
    if '-' in string:
        clist =string.split('-')
        cstr = cstr + ' tcp dst-port ' + clist[0] + ' ' + clist[1]+'\n'
    else:
        cstr = cstr + ' tcp dst-port ' + string+'\n'
    cstr = cstr + 'exit\n'
    return cstr


def isexcel():
    global bk
    tempstr=''
    bk = xlrd.open_workbook(fname)
    label.config(text=fname)
    shxrange = range(bk.nsheets)
    # 获取第一个表
    global sh
    sh = bk.sheets()[0]  # 通过索引顺序获取第一个sheet
    # 获取行数
    nrows = sh.nrows
    # 获取列数
    ncols = sh.ncols
    print("nrows %d, ncols %d" % (nrows, ncols))
    # 获取第一行第一列数据
    temptime=time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    fd = open('excelout_'+ temptime +'.txt', 'w')

    startline=1
    endline=27

    cell_value = ''
    filecol3 = open('col3_'+ temptime +'.txt','w')
    for i in range(startline, endline):  # 循环这些行，
        cell_value_col4 = sh.cell_value(i,4) #此列是预定义的端口，
        cell_value_col5 = sh.cell_value(i,5) #此列是自定义的端口，
        #print(cell_value_col4)
        #exit()
        if cell_value_col4==';;1':
            tem_col3='1'
        elif cell_value_col4==';;0':
            tem_col3=''
        else:
            tem_col3 = cell_value_col4.replace(';;',',')#例如，21;;1，21;;0，这样的
            tem_col3 = tem_col3.replace('#', ',')
            #print(tem_col3)
            if tem_col3[-1] =='0':
                tem_col3 = tem_col3[:-1]
        cell_value_col5=cell_value_col5.replace(';;',',')
        cell_value_col5=cell_value_col5.replace(';',',')
        cell_value_col5=cell_value_col5.replace('#',',')
        if cell_value_col5.endswith(','):
            cell_value_col5=cell_value_col5[:-1]#去掉最后的一个逗号
        if tem_col3 == '':
            tem_col3 = cell_value_col5
        else:
            tem_col3= tem_col3 + ','+cell_value_col5
        #以上：tem_col3是融合后的，

        list_col3=tem_col3.split(',')#要检查list_col3中有没有带‘-’的
        #print(list_col3)
        #exit()
        for m in range(len(list_col3)):
            if '-' in list_col3[m]:
                temlist = list_col3[m].split('-')
                if temlist[0] == temlist[1]:
                    list_col3[m] = temlist[0]
                else:
                    pass
        list_col3_temp = []
        for n in list_col3:
            if not n in list_col3_temp:
                list_col3_temp.append(n)
        list_col3 = list_col3_temp #list_col3中没有重复项了。
        while '' in list_col3:
            list_col3.remove('')
        #print(list_col3)
        tem_col3=','.join(list_col3)#这一行包含的端口号在list_col3中，
        tem_col3 = tem_col3 + '\n'
        filecol3.writelines(tem_col3)
    filecol3.close()
    #以上，将4、5列合并，并输出到文件中
    #exit()

    temptime = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    fa = open('service_' + temptime + '.txt', 'w')
    for i in range(startline, endline):  # 循环这些行，
        colout=''
        ingress_int = sh.cell_value(i,1)#取第二列的值,读每一行时先判断第二列的值，
        if  ingress_int =='vlan-if750' or ingress_int =='gige0_5' or ingress_int =='gige0_7':#这一行可以转换，以下是开始转这一行，
            col4 = sh.cell_value(i,3)#取服务端口，第四列的值，
            list_allcol3_temp = col4.split(',')  # 看这一列有几个端口，去掉逗号放到列表中，
            #list_allcol3_temp = list(set(list_allcol3_temp))#去掉其中的重复项
            if '20' in list_allcol3_temp and '21' in list_allcol3_temp:
                #print(list_allcol3_temp)
                list_allcol3_temp.remove('20')
                list_allcol3_temp.remove('21')
                list_allcol3_temp.append('FTP')
            if '1' in list_allcol3_temp:
                list_allcol3_temp.remove('1')
                list_allcol3_temp.append('ICMP')
            if '22' in list_allcol3_temp:
                list_allcol3_temp.remove('22')
                list_allcol3_temp.append('SSH')
            if '23' in list_allcol3_temp:
                list_allcol3_temp.remove('23')
                list_allcol3_temp.append('TELNET')
            if '443' in list_allcol3_temp:
                list_allcol3_temp.remove('443')
                list_allcol3_temp.append('HTTPS')
            for astr in list_allcol3_temp:
                if astr =='':
                    astr='any'
                elif astr[0].isnumeric():#判断这个服务端口是英文还是数字的，
                    astr = 'tcp-' + astr
                    fa.writelines(astr+'\n')
                temp2 = str(fromcoltocli(i,ingress_int,astr))
                colout = colout + temp2
            colout = colout + '\n'
            fd.writelines(colout)
        else:
            pass
    fa.close()
    fd.close()
    fa = open('service_' + temptime + '.txt', 'r')
    service_list = fa.readlines()
    fa.close()
    fa = open('service_' + temptime + '.txt', 'w')
    service_list2 = []
    for bstr in service_list:
        if bstr not in service_list2:
            service_list2.append(bstr)
    service_str=''.join(service_list2)#去重完成
    fa.writelines(service_str)
    fa.close()
    fa = open('service_' + temptime + '.txt', 'r')
    service_list = fa.readlines()
    fa.close()

    temptime = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    fa = open('service_create_' + temptime + '.txt', 'w')
    for m in service_list:
        dstr = m[4:]
        estr = create_service(dstr)
        fa.writelines(estr)
    fa.close()
    done_label.config(text='转换完成!')
    return 0


root=tkinter.Tk()
root.title("Trans to Hillstone --by jlyang")

var = tkinter.StringVar()
menubar = Menu(root)

filemenu = Menu(menubar, tearoff=0)

#menubar.add_cascade(label="原设备类型", menu=filemenu)


filemenu.add_radiobutton(label="CISCO",  command=option1,variable =var)
filemenu.add_radiobutton(label="JUNOS", command=option2,variable =var)
filemenu.add_radiobutton(label="NETSCREEN", command=option3,variable =var)
filemenu.add_radiobutton(label="F5", command=option4,variable =var)
filemenu.add_radiobutton(label="HUAWEI", command=option5,variable =var)
filemenu.add_radiobutton(label="EXCEL-(ADX)", command=option6,variable =var)



#filemenu.add_separator()
#filemenu.add_radiobutton(label="Exit", command=root.quit)
menubar.add_cascade(label="原设备类型", menu=filemenu)


# 创建主菜单，每个菜单对应的回调函数都是hello
#menubar.add_radiobutton(label='CISCO',command=hello)
#for k in ['Python', 'PHP', 'CPP', 'C', 'Java', 'JavaScript', 'VBScript']:
#    # 绑定变量与回调函数，指定的变量vLang将这几项划为一组
#    menubar.add_radiobutton(label=k, command=hello, variable=vLang)

#for item in ['Python', 'PHP', 'CPP', 'C', 'Java', 'JavaScript', 'VBScript']:
#    menubar.add_command(label=item, command=hello)
# 将root的menu属性设置为menubar
#
#labelHello = tk.Label(root, text = "Press the button...", height = 5, width = 20, fg = "blue")
label4=tkinter.Label(root,text='注意：要转换的原配置文件请使用UTF-8编码的TXT!',bg='yellow')
label4.grid(row=0,column=1,sticky=W)


label=tkinter.Label(root,text='要转换的是：',bg='cyan')
label.grid(row=1,sticky=E)

label2=tkinter.Label(root,text='',bg='cyan')#显示选择的原产品
label2.grid(row=1,column=1,sticky=W)

label3=tkinter.Label(root,text='')#原文件的路径
label3.grid(row=2,column=1)

btn = tkinter.Button(root, text = "选择原文件", command = btnClicked,width='11')
btn.grid(row=2,column=0)

done_label=tkinter.Label(root,text='还未转换!',bg='gold')
done_label.grid(row=3,column=1)

trans_btn=tkinter.Button(root,text='开始转换',command=trans_btnclicked,width='11')
trans_btn.grid(row=3,column=0)

#test_btn=tkinter.Button(root,text='test',command=test_btnclicked,width='11')
#test_btn.grid(row=4,column=0)

quit=tkinter.Button(root,text='退出！',command=root.quit,fg='red',width='11')
quit.grid(column=1)

i=0
srcfile=''

root['menu'] = menubar
root.mainloop()
