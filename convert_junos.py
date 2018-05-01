#coding:utf-8
import os
import time
from creatdb import *


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

    insert2db(tux)

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
    servname = words[m + 1]#取得服务簿名称
    namelist=['SNMP','SSH']
    if servname in namelist:
        return 0
    # print(i)
    # print(70)
    try:
        m = words.index('protocol')
    except:
        print(i)
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
                strpolicy = '\nrule\n action ' + strpolicyction + '\n'+strpolicy+namestr
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
        insert2db(tux)
        tux = None
    else:
        straddrip = words[m + 1]
        natpool = 'address ' + straddrname + '\n'
        natpool = natpool + ' ip ' + straddrip + '\n'
        natpool = natpool + 'exit\n'
        #ed.writelines(natpool)
        tux = straddrname, straddrip
        # print(tux)
        insert2db(tux)
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
            insert_pubip2db(tux)
            tux = None
            update2db(strdnatpool)
            # query = 'UPDATE addrname_pubip SET priip = ( select ip from addr_ip where addrname_pubip.addrname=addr_ip.addr) where addrname=?'
            # curs.execute(query, (strdnatpool,))
            # conn.commit()
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


def isjunos(fname):
    output=''
    global addrgroupstr
    addrgroupstr=''
    global addrstr
    addrstr=''
    fd = open(fname, 'r', encoding='utf-8')  # 打开源文件
    srcfile = fd.readlines()  # 将源文件读取到列表srcfile中
    print(str(len(srcfile)) + '行')  # 源文件有这些行
    fd.close() #读取原文件结束

    creatdb(fname)

    global i
    i = 0
    print(len(srcfile))	#srcfile[len(srcfile)-1]是最后一行
    while (i < len(srcfile)):
        words = srcfile[i].split()
        if ('set' in words and 'address-book' in words and 'address-set' in words):
             transaddrgroup(srcfile)
        elif ('set' in words and 'address-book' in words and 'address' in words):
             transaddr(srcfile)
        elif ('set' in words and 'junos-defaults' in words and 'applications' in words and 'application' in words):
            pass
        elif ('set' in words and 'applications' in words and 'application' in words):
            # print(type(output))
            # print(type(transservice(srcfile)))
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

    #done_label.config(text='转换完成!')
    done_label='转换完成!'
    return done_label
