#coding:utf-8
from en_mouth_to_num import *
import time
from opensrcfile import *
import os
from creatdb import *


def asa_interface_trans(alist,j):
    temp=''
    zone = ''
    ipaddr = ''
    words = alist[j].split()  #
    interface = words[1]
    j += 1
    while(1):
        words = alist[j].split()  #
        if '!' in words:
            if zone=='':
                break
            query = "insert into interface_tb(interface,zone,ipaddress) values(?,?,?);"
            tmplist3 = [interface, zone, ipaddr]
            insert2table_new(query, tmplist3)
            temp = 'interface '+interface+'\n'+ \
                ' zone '+zone+'\n'+ \
                ' ip address '+ipaddr+'\n'+ \
                'exit\n'
            break
        elif 'no' in words and 'nameif' in words:
            break
        elif 'nameif' in words:
            zone=words[1]
        elif 'ip' in words and 'address' in words:
            ipaddr=words[2]+' '+words[3]
        j += 1
    j -= 1
    return temp,j

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


def asa_exchangemask(mask_b):
    try:
        exchange_mask = lambda mask: sum(bin(int(i)).count('1') for i in mask.split('.'))
    except:
        print('911')
    mask_d = str(exchange_mask(mask_b))
    return mask_d


def asa_addr_trans(list,j):
    words=list[j].split()
    addrname=words[2]
    j+=1
    temp='address '+addrname+'\n'
    while(j<len(list)):
        words = list[j].split()  # 第二行，定义内容部分
        if 'subnet' in words:
            ipnet=words[1]
            netmask=words[2]
            temp+=' ip ' +ipnet+' '+netmask+'\n'
        elif 'host' in words:
            ip=words[1]
            temp+=' ip '+ip+'/32\n'
        elif 'range' in words:
            ipstart=words[1]
            ipend=words[2]
            temp+=' range '+ipstart+' '+ipend+'\n'
        elif 'object' in words or 'object-group' in words:
            break
        j+=1
    temp+='exit\n'
    j-=1
    return temp,j

def asa_addr_group_trans(list,j):
    words = list[j].split()
    addr_group_name = words[2]
    j += 1
    temp = 'address ' + addr_group_name + '\n'
    while (j < len(list)):
        words = list[j].split()  # 下一行，定义内容部分
        if 'network-object' not in words:
            break
        elif 'object' in words:
            member = words[2]
            temp += ' member ' + member + '\n'
        elif 'description' in words:
            temp += list[j]
        elif 'host' in words:
            ip = words[2]
            temp += ' ip ' + ip + '/32\n'
        elif 'range' in words:
            ipstart = words[1]
            ipend = words[2]
            temp += ' range ' + ipstart + ' ' + ipend + '\n'

        else:
            ipnet=words[1]
            netmask=words[2]
            temp += ' ip ' + ipnet + ' ' + netmask + '\n'
        j += 1
    temp += 'exit\n'
    j -= 1
    return temp, j


def service_group_trans(alist,j):
    # 服务组有两种类型的，
    #object-group service bucapbr_svc
    # service-object tcp destination eq ssh
    # service-object tcp destination eq 9043
    # service-object tcp destination eq https
    # service-object tcp destination eq 9080
    # service-object tcp destination eq 9443
    # service-object tcp destination eq 26999
    words = alist[j].split()
    service_group_name = words[2]
    temp = 'servgroup ' + service_group_name + '\n'
    if 'tcp' in words or 'udp' in words:#判断是不是直接定义型的服务组，
        prot = words[3]
        j += 1
        while (j < len(alist)):
            words = alist[j].split()  # 第二行，定义内容部分
            if 'eq' in words:
                port = words[2]
                # 查port在表中对应的端口号，
                if port.isdigit():  # port中全是数字，则这是表示端口的，
                    servname = prot + '-' + port
                    # 将此作为新服务，插入到表中
                    query = "insert into service_s(servname,proto,dstport) values(?,?,?);"
                    tmplist = [servname, prot, port]
                    insert2table_new(query, tmplist)
                    temp += ' service ' + servname + '\n'
                else:  # 去表中查对应的hillstone名字，这时port中一般是英文，比如ftp、ssh等，
                    query = 'select  distinct hillservname from predeservmatch where origservname="%s";' % port
                    temp1 = fetchallfrom(query)  # temp1=[(443,)]
                    if temp1:
                        port = list(temp1[0])[0]
                        temp += ' service ' + port + '\n'
            elif 'description' in words:
                temp += alist[j]
            elif 'range' in words:
                portstart = words[2]
                portend = words[3]
                servname = prot + '-' + portstart + '-' + portend

                # 将portstart，比如是ftp-data替换为20，
                query = 'select  distinct dstport1 from predeservmatch where origservname="%s";' % portstart
                temp1 = fetchallfrom(query)  # temp1=[(443,)]
                if temp1:
                    portstart = list(temp1[0])[0]

                query = 'select  distinct dstport1 from predeservmatch where origservname="%s";' % portend
                temp1 = fetchallfrom(query)  # temp1=[(443,)]
                if temp1:
                    portend = list(temp1[0])[0]

                query = "insert into service_range(servname,proto,dstport1,dstport2) values(?,?,?,?);"
                tmplist = [servname, prot, portstart, portend]
                insert2table_new(query, tmplist)
                temp += ' service ' + servname + '\n'
            elif 'port-object' not in words:
                break
            j += 1
    else:
        j += 1
        while (j < len(alist)):
            words = alist[j].split()  # 第二行，定义内容部分
            if 'tcp' in words or 'udp' in words:
                prot = words[1]
                # temp += ' '+prot+ ' dst-port '
            if 'eq' in words:
                port = words[4]
                #查port在表中对应的端口号，
                if port.isdigit():#port中全是数字，则这是表示端口的，
                    servname=prot+'-'+port
                    #将此作为新服务，插入到表中
                    query = "insert into service_s(servname,proto,dstport) values(?,?,?);"
                    tmplist = [servname, prot, port]
                    insert2table_new(query, tmplist)
                    temp += ' service ' + servname + '\n'
                else:#去表中查对应的hillstone名字，这时port中一般是英文，比如ftp、ssh等，
                    query = 'select  distinct hillservname from predeservmatch where origservname="%s";' % port
                    temp1=fetchallfrom(query)#temp1=[(443,)]
                    if temp1:
                        port=list(temp1[0])[0]
                        temp += ' service '+port + '\n'
            elif 'description' in words:
                temp += alist[j]
            elif 'range' in words:
                portstart = words[4]
                portend = words[5]
                servname = prot + '-' + portstart + '-' + portend

                #将portstart，比如是ftp-data替换为20，
                query = 'select  distinct dstport1 from predeservmatch where origservname="%s";' % portstart
                temp1 = fetchallfrom(query)  # temp1=[(443,)]
                if temp1:
                    portstart = list(temp1[0])[0]

                query = 'select  distinct dstport1 from predeservmatch where origservname="%s";' % portend
                temp1 = fetchallfrom(query)  # temp1=[(443,)]
                if temp1:
                    portend = list(temp1[0])[0]

                query = "insert into service_range(servname,proto,dstport1,dstport2) values(?,?,?,?);"
                tmplist = [servname, prot, portstart,portend]
                insert2table_new(query, tmplist)
                temp += ' service ' + servname + '\n'

            elif 'service-object' not in words:
                break
            j += 1
    temp += 'exit\n'
    j -= 1
    return temp, j


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


def asa_acl_src_dst_addr(alist,y):   #y是地址串中最后一个元素的下标，
    # access-list outside_acl extended permit tcp object PMO_21F_IP object-group 21F_BL_UAT_IP eq 50000

    string2 = ''
    srcip=''
    dstip=''
    j = 5 #下标为5的元素为地址串中的第一位，
    if y-j+1 ==2:#地址串长度为2，
        #例如：icmp any any
        #tcp any any
        string2 = ' src-addr any\n dst-addr any\n'
    elif y-j+1 ==3:#地址串长度为3，
        #any host 41.248.98.98
        #host 172.26.136.148 any
        #any 172.26.158.100 255.255.255.252
        if alist[5] =='any':
            #any host 41.248.98.98
            srcip='any'
            if alist[6] =='host':
                dstip=alist[7]+'/32'
                string2 = ' src-addr ' + srcip + '\n dst-ip ' + dstip + '\n'
            elif alist[6] == 'any':
                dstip='any'
                string2 = ' src-addr ' + srcip + '\n dst-addr ' + dstip + '\n'
            elif alist[6] == 'object' or alist[6] == 'object-group':
                dstip = alist[7]
                string2 = ' src-addr ' + srcip + '\n dst-addr ' + dstip + '\n'
            else:
                dstip = alist[6] + '/' + asa_exchangemask(alist[7])
                string2 = ' src-ip '+srcip+'\n dst-ip '+dstip+'\n'
        elif alist[5] == 'host':
            # host 172.26.136.148 any
            srcip=alist[6]+'/32'
            if alist[7] == 'any':
                dstip='any'
                string2 = ' src-ip ' + srcip + '\n dst-addr ' + dstip + '\n'
            elif alist[7] == 'host':
                pass
            elif alist[7] == 'object':
                pass
            else:
                dstip = alist[7] + '/' + asa_exchangemask(alist[8])
                string2 = ' src-ip '+srcip+'\n dst-ip '+dstip+'\n'
        elif alist[5] == 'object' or alist[5] == 'object-group' :
            srcip = alist[6]
            dstip = 'any'
            string2 = ' src-addr ' + srcip + '\n dst-addr ' + dstip + '\n'
        else:
            srcip=alist[5]+'/'+ asa_exchangemask(alist[6])
            if alist[7] == 'any':
                dstip = 'any'
                string2 = ' src-ip ' + srcip + '\n dst-addr ' + dstip + '\n'
            elif alist[7] == 'host':
                pass
            elif alist[7] == 'object':
                pass
            else:
                dstip = alist[7] + '/' + asa_exchangemask(alist[8])
                string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
    elif y-j+1 ==4:#地址串长度为4
        #eg.tcp 172.26.149.32 255.255.255.224 172.26.141.0 255.255.255.0
        #host 172.25.241.56 host 172.26.156.1
        #10.44.0.0 255.255.0.0 host 172.26.140.3
        #object PMO_21F_IP object-group 21F_BL_UAT_IP
        #object-group OBJ-BaoLeiJi-1 host 10.20.65.13
        if alist[5] == 'any':#如果第一位是any，
            pass
        elif alist[5] == 'host':
            srcip = alist[6] + '/32'
            if alist[7] == 'any':
                dstip = 'any'
                string2 = ' src-ip ' + srcip + '\n dst-addr ' + dstip + '\n'
            elif alist[7] == 'host':
                dstip=alist[8]+'/32'
                string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
            elif alist[7] == 'object' or alist[7] == 'object-group':
                dstip = alist[8]
                string2 = ' src-ip ' + srcip + '\n dst-addr ' + dstip + '\n'
            else:
                dstip = alist[7] + '/' + asa_exchangemask(alist[8])
                string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
        elif alist[5] == 'object' or alist[5] == 'object-group' :
#access-list OAS-OUTSIDE-ACL extended deny tcp object-group OBJ-BaoLeiJi-1 host 10.20.65.13 eq www
            srcip = alist[6]#源地址是地址簿，
            if alist[7] == 'object' or alist[7] == 'object-group' :
                dstip = alist[8]#目的地址也是地址簿，
                string2 = ' src-addr ' + srcip + '\n dst-addr ' + dstip + '\n'
            elif alist[7] == 'host':
            # object-group OBJ-BaoLeiJi-1 host 10.20.65.13
                dstip=alist[8]+'/32'
                string2 = ' src-addr ' + srcip + '\n dst-ip ' + dstip + '\n'
        else:
            srcip=alist[5]+'/'+ asa_exchangemask(alist[6])
            if alist[7] == 'any':
                pass
            elif alist[7] == 'host':
                dstip = alist[8] + '/32'
                string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
            elif alist[7] == 'object' or alist[7] == 'object-group':
                dstip = alist[8]
                string2 = ' src-ip ' + srcip + '\n dst-addr ' + dstip + '\n'
            else:
                dstip = alist[7] + '/' + asa_exchangemask(alist[8])
                string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
    return string2





def asa_acl_aftertcpudp(alist,proto):
    #alist:
    #access-list outside_acl extended permit tcp any host 22.237.188.132 eq 445
    #access-list outside_acl extended permit tcp object PMO_21F_IP object-group 21F_BL_UAT_IP eq 50000
    string3=''
    serviceend=''
    global string4
    service=''

    if 'eq' in alist:
        m = alist.index('eq')
        string3 = string3 + asa_acl_src_dst_addr(alist, (m - 1))  # 源目的地址部分，交给地址转换函数

        port = alist[m + 1]#下一步到2个表中查此端口对应的服务名字，
        if port.isdigit():
            query = 'select  distinct servname from service_s where dstport="%s";' % port
            servname_tmp = fetchallfrom(query)  # temp1=[(,)]
            if servname_tmp:
                service = list(servname_tmp[0])[0]
            else:
                query = 'select  distinct hillservname from predeservmatch where dstport1="%s";' % port
                servname_tmp = fetchallfrom(query)  # temp1=[(,)]
                if servname_tmp:
                    service = list(servname_tmp[0])[0]
                else:
                    service=proto+'-'+port
                    query = "insert into service_s(servname,proto,dstport) values(?,?,?);"
                    tmplist = [service, proto, port]
                    insert2table_new(query, tmplist)
        else:#如果port不是数字，比如：www,ssh,radius等，
            query = 'select  distinct hillservname from predeservmatch where origservname="%s";' % port
            servname_tmp = fetchallfrom(query)  # temp1=[(,)]
            if servname_tmp:
                service = list(servname_tmp[0])[0]
            else:
                service='需要新建'
        string3 += ' service ' + service + '\n'

        if 'time-range' in alist:
            m = alist.index('time-range')
            schedule = alist[m + 1]
            string3 = string3 + ' schedule ' + schedule + '\n'
    elif 'range' in alist:
        # extended permit tcp any host 172.26.158.2 range www 81
        # extended permit tcp host 30.32.14.220 host 30.39.252.198 range ssh telnet
        m = alist.index('range')
        string3 = string3 + asa_acl_src_dst_addr(alist, (m - 1))  # 交给地址转换函数

        portstart = alist[m+1]
        portend = alist[m+2]
        if portstart.isdigit():#如果是数字，
            pass
        else:#如果不是数字，
            query = 'select  distinct dstport1 from predeservmatch where origservname="%s";' % portstart
            servname_tmp = fetchallfrom(query)  # temp1=[(,)]
            if servname_tmp:
                portstart = list(servname_tmp[0])[0]
            else:
                portstart = '需要新建替换'+portstart

        if portend.isdigit():#如果是数字，
            pass
        else:#如果不是数字，而是预定义的，
            query = 'select  distinct dstport1 from predeservmatch where origservname="%s";' % portend
            servname_tmp = fetchallfrom(query)  # temp1=[(,)]
            if servname_tmp:
                portend = list(servname_tmp[0])[0]
            else:
                portend = '需要新建替换'+portend

        service = portstart + '-' + portend  # alist[m+2]是range中的结束端口
        string4 +=  service + '\n'
        service= proto +'-'+service
        query = "insert into service_range(servname,proto,dstport1,dstport2) values(?,?,?,?);"
        tmplist = [service, proto, portstart, portend]
        insert2table_new(query, tmplist)


        string3 = string3 + ' service ' + service + '\n'
        if 'time-range' in alist:
            m = alist.index('time-range')
            schedule = alist[m + 1]
            string3 = string3 + ' schedule ' + schedule + '\n'
    elif 'time-range' in alist:  # 这一行没有端口，是tcp-any，
        # extended permit tcp host 172.26.73.52 host 172.26.153.17 time-range 20181231
        m = alist.index('time-range')
        service = 'tcp-any'
        string3 = string3 + asa_acl_src_dst_addr(alist, (m - 1))  # 交给地址转换函数
        string3 = string3 + ' service ' + service + '\n'
        schedule = alist[m + 1]
        string3 = string3 + ' schedule ' + schedule + '\n'
    elif 'object-group' in alist:
#access-list OAS-OUTSIDE-ACL extended deny tcp 10.20.190.0 255.255.255.0 host 10.20.64.10 object-group GBDK-PORT
        # if alist.index('object-group') == (len(alist)-2):
        if alist[len(alist)-2] == 'object-group':
            #倒数第二个元素是object-group，则这个是服务，
            service = alist[(len(alist)-1)]#最后一个元素是具体服务簿，
            pass
            string3 = string3 + asa_acl_src_dst_addr(alist, (len(alist) - 3))
            #(len(alist) - 3)是地址串中最后一个元素的下标，即目的地址的下标，
            string3 = string3 + ' service ' + service + '\n'
    else:
        # tcp 172.26.149.32 255.255.255.224 172.26.141.0 255.255.255.0
        # tcp any any
        # tcp 10.20.190.0 255.255.255.0 host 10.20.64.10 object-group GBDK-PORT
        if alist[4]=='tcp':
            service = 'tcp-any'
        else:
            service = 'udp-any'
        string3 = string3 + asa_acl_src_dst_addr(alist, (len(alist) - 1))
        string3 = string3 + ' service ' + service + '\n'

    return string3


def asa_trans_extend_acl(alist,j):
    string = ''
    servicestart = ''
    srczone = ''
    dstzone = ''

    while (j < len(alist)):
        words = alist[j].split()  #
        if 'extended' not in words:
            break
        m = words.index('extended')
        aclname = words[m - 1]
        action = words[m + 1]
        # string += '#This is ' + aclname + '\n'
        # string += '#Thist is line'+ str(j+1) +'\n'
        string += 'rule id ' + str(j+1)+ '\n' \
                  ' action ' + action + '\n'
        query = 'select   srczone,dstzone from aclgroup_zone where aclgroup="%s";' % aclname
        temp1 = fetchallfrom(query)  # temp1=[(inside,any)]
        if temp1:
            srczone,dstzone = (list(temp1[0])[0],list(temp1[0])[1])
        string +=' src-zone '+srczone+'\n' + \
            ' dst-zone '+dstzone+'\n'

        k = 4
        #access-list inside_acl extended permit icmp any any
        try:
            words[k] == 'icmp'
        except:
            pass
        if words[k] == 'icmp':  # 判断下标为4的元素是icmp
            service = 'ICMP'
            if 'time-range' in words:
                m = words.index('time-range')
                string = string + asa_acl_src_dst_addr(words, (m- 1))
                string = string + ' service ' + service + '\n'
                schedule = words[m + 1]
                string = string + ' schedule ' + schedule + '\n'
            else:
                string = string + asa_acl_src_dst_addr(words, (len(words) - 1))
                string = string + ' service '+service+'\n'
            string = string + 'exit\n\n'
        elif words[k] == 'ip':# 判断下标为4的元素是ip
            service = 'any'
            if 'time-range' in words:
                m = words.index('time-range')
                string = string + asa_acl_src_dst_addr(words, (m- 1))
                string = string + ' service ' + service + '\n'
                schedule = words[m + 1]
                string = string + ' schedule ' + schedule + '\n'
            else:
                string = string + asa_acl_src_dst_addr(words, (len(words) - 1))
                string = string + ' service ' + service + '\n'
            string = string + 'exit\n\n'
        elif words[k] == 'tcp':# 判断下标为4的元素是tcp
            #eg.permit tcp host 172.26.136.148 any eq https time-range 20171231
            #eg.permit tcp 172.26.149.32 255.255.255.224 172.26.141.0 255.255.255.0
            #access-list outside_acl extended permit tcp object PMO_21F_IP object-group 21F_BL_UAT_IP eq 50000
            string = string + asa_acl_aftertcpudp(words,words[k])
            string = string + 'exit\n\n'
        #print(list[j])
        elif words[k] == 'udp': # 判断下标为4的元素是udp
            #print('653')
            string = string + asa_acl_aftertcpudp(words,words[k])
            string = string + 'exit\n\n'
        elif words[k] == 'object-group':
#access-list outside_acl extended permit object-group QUOSPAP_SVC object UAT_IP_OSP object-group QUOSPAP_SVR

            service=words[k+1]#下标为5的元素是服务，
            if words[k+2] =='object' or words[k+2] =='object-group':# 下标为6的元素是源地址，object或object-group
                string += ' src-addr '+ words[k+3] + '\n'
            if words[k+4] =='object' or words[k+4] =='object-group':
                string += ' dst-addr '+ words[k+5] + '\n'
            elif words[k+4] =='host':
                string += ' dst-ip ' + words[k + 5] + '/32\n'
            string += ' service ' + service + '\n'
            string += 'exit\n\n'
        j+=1
    j-=1
    return string,j


def asa_nat_trans(alist,j):
    temp = ''
    interface = ''
    words = alist[j].split()  #nat (inside,nat_network) source static buixpgw1 buixpgw1_nat
    bizone=words[1]#找出对应的出安全域及出接口，
    bizonelist=bizone.split(',')
    outzone=bizonelist[1][0:-1]
    query = 'select interface from interface_tb where zone="%s";' % outzone
    temp3 = fetchallfrom(query)  # temp3=[(e0/1,)]
    if temp3:
        interface = list(temp3[0])[0]

    m=words.index('static')
    realip=words[m+1]
    vip = words[m+2]

    temp = 'snatrule from '+realip+' to any service any eif '+interface+' trans-to address-book ' + vip + ' mode static' +'\n'
    temp += 'dnatrule from any to '+ vip +' service any trans-to '+realip+'\n'
    # temp = 'bnatrule interface '+interface+' virtual address-book ' + vip + ' real address-book ' + realip + '\n'
    return temp

# def asa_build_nat_fromdb():
#     temp=''
#
#
#     return temp

def asa_bulidservfromdb():
    service=''

    query = 'select * from predeservmatch where newadd="1" group by hillservname having count(hillservname)>=1;'
    temp1 = fetchallfrom(query)  # temp2=[()]
    if temp1:
        for atuple in temp1:  # atuple=(2,老名字，新名字,tcp,9900，新建位)
            service += 'service ' + list(atuple)[2] + '\n' + \
                       ' ' + list(atuple)[3] + ' dst-port ' + list(atuple)[4] + '\n' + \
                       'exit\n'

    query = 'select * from service_s group by servname having count(servname)>=1;'
    temp2 = fetchallfrom(query)  # temp2=[()]
    if temp2:
        for atuple in temp2:  # atuple=(2,tcp-9900,tcp,9900)
            service += 'service ' + list(atuple)[1] + '\n' + \
                       ' ' + list(atuple)[2] + ' dst-port ' + list(atuple)[3] + '\n' + \
                       'exit\n'

    # 取出service_range中的所有服务，并转换成脚本，
    query = 'select * from service_range group by servname having count(servname)>=1;'
    temp2 = fetchallfrom(query)  # temp2=[()]
    if temp2:
        for atuple in temp2:  # atuple=(2,tcp-1414-1416,tcp,1414,1416)
            service += 'service ' + list(atuple)[1] + '\n' + \
                       ' ' + list(atuple)[2] + ' dst-port ' + list(atuple)[3] + ' ' + list(atuple)[4] + '\n' + \
                       'exit\n'
    return service

def asa_build_route_fromdb():
    temp = ''
    query = 'select * from iproute;'
    temp2 = fetchallfrom(query)  # temp2=[()]
    temp = 'ip vrouter trust-vr\n'
    if temp2:
        for atuple in temp2:  # atuple=(1,10.1.1.0/24,192.168.1.2,1)
            temp += ' ip route ' + list(atuple)[1] + ' ' + list(atuple)[2] + ' ' + list(atuple)[3] +'\n'
    temp += 'exit\n'
    return temp

def asa_route_trans(alist,j):
    temp = ''
    words = alist[j].split()
    destinet = words[2]
    netmask = words[3]
    destinet +='/'+asa_exchangemask(netmask)
    nxhop = words[4]
    metric = words[5]
    query = "insert into iproute(destinet,nxhop,metric) values(?,?,?);"
    tmplist2 = [destinet, nxhop, metric]
    insert2table_new(query, tmplist2)

    return 0



def isciscoasa(fileuri):
    global addrgroupstr
    addrgroupstr = ''
    global addrstr
    addrstr = ''
    global string4
    string4 = ''
    origfilename=''
    #global srcfile
    srcfile = openfile(fileuri)  # 打开原配置
    filepath = os.path.split(fileuri)[0]
    origfilename = os.path.split(fileuri)[1]

    qurey = "CREATE TABLE IF NOT EXISTS service_s(id integer primary key autoincrement, \
                servname TEXT, \
                proto TEXT, \
                dstport TEXT);"
    creat_table(qurey)
    qurey = "CREATE TABLE IF NOT EXISTS service_range(id integer primary key autoincrement, \
                    servname TEXT, \
                    proto TEXT, \
                    dstport1 TEXT, \
                    dstport2 TEXT);"
    creat_table(qurey)
    qurey = "CREATE TABLE IF NOT EXISTS interface_tb(id integer primary key autoincrement, \
                    interface TEXT, \
                    zone TEXT, \
                    ipaddress TEXT);"
    creat_table(qurey)
    qurey = "CREATE TABLE IF NOT EXISTS iproute(id integer primary key autoincrement, \
                        destinet TEXT, \
                        nxhop TEXT, \
                        metric TEXT);"
    creat_table(qurey)



    schedu_str = ''
    standard_acl = ''
    extended_acl = ''
    addr_book = ''
    addr_book_group=''
    service_group=''
    addr_book_temp=''
    service_temp=''
    inter_config = ''
    route_config = ''
    nat_temp = ''
    # global i
    i = 0
    # print(len(srcfile))	#srcfile[len(srcfile)-1]是最后一行

    aclgroup=''
    direc=''
    srczone=''
    dstzone=''
    nat_config = ''
    qurey = "CREATE TABLE IF NOT EXISTS aclgroup_zone(id integer primary key autoincrement, \
                    aclgroup TEXT, \
                    direction TEXT, \
                    srczone TEXT, \
                    dstzone TEXT);"
    creat_table(qurey)
######################确定access-group与安全域的关系，是in还是out，
    #access-group outside_acl in interface outside
    while (i < len(srcfile)):#先判断策略和安全域的关系，
        words = srcfile[i].split()
        if 'access-group' in words and 'interface'  in words:
            m=words.index('interface')
            aclgroup=words[m-2]
            direc=words[m-1]
            if direc == 'in':
                srczone=words[m+1]
                dstzone='any'
            else:
                srczone='any'
                dstzone=words[m+1]
            query = "insert into aclgroup_zone(aclgroup,direction,srczone,dstzone) values(?,?,?,?);"
            tmplist2 = [aclgroup, direc, srczone, dstzone]
            insert2table_new(query, tmplist2)
        i +=1
########################
    i =0
    while (i < len(srcfile)):
        words = srcfile[i].split()#当前行存储在列表words中，
        if 'time-range' in words and 'access-list' not in words:
            schedu_str =  schedu_str + asa_trans_schedu(words)
        elif 'interface' in words and len(words)==2:
            (inter_temp,i) = asa_interface_trans(srcfile,i)
            inter_config += inter_temp
        elif 'object' in words and 'network' in words:#地址转换
            (addr_book_temp,i)= asa_addr_trans(srcfile,i)
            addr_book += addr_book_temp
        elif 'object-group' in words and 'network' in words:#地址组转换
            (addr_book_temp, i) = asa_addr_group_trans(srcfile, i)
            addr_book_group += addr_book_temp
        elif 'object-group' in words and 'service' in words:#服务组转换
            #object-group service 3G-DomainServer-tcp tcp，版本7.1（2）
            # description outsidein 3G-DomainServer password-change tcp-Port
            # port-object eq 135
            # port-object eq ldap
            # port-object eq ldaps
            # port-object eq 445
            # port-object eq 88
            # port-object eq domain
            # port-object eq 3268
            # port-object eq 3269
            # port-object range 50000 60000
            # port-object eq 5722
            (service_temp, i) = service_group_trans(srcfile, i)
            service_group += service_temp
        elif 'access-list' in words and ('standard' in words ):#标准ACL转换，
            pass
            #standard_acl = standard_acl + asa_trans_standard_acl(words)
        elif 'access-list' in words and ('extended' in words):#扩展ACL转换，
            # break
            (acl_temp,i) = asa_trans_extend_acl(srcfile,i)
            extended_acl += acl_temp
        elif 'nat' in words and ('static' in words):#静态NAT转换，
            #nat (inside,nat_network) source static buixpgw1 buixpgw1_nat
            nat_temp += asa_nat_trans(srcfile,i)
        elif  'route' in words  and words[0] == 'route':
            asa_route_trans(srcfile,i)
        i += 1
    temptime = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))

    # newfileuri = filepath + '/create_standardacl_' + temptime + '.txt'  # 新文件为源文件在同一个文件夹下
    # writefile(newfileuri,standard_acl)
    #
    # newfileuri=filepath + '/create_extendedacl_' + temptime + '.txt'
    # writefile(newfileuri,extended_acl)

    #取出service_s中的所有服务，并转换成脚本，
    service=''


    newfileuri = filepath + '/'+origfilename+'_new_config_' + temptime + '.txt'
    service = asa_bulidservfromdb()
    nat_config = 'nat\n'+ \
                 nat_temp + \
                 'exit\n'
    route_config = asa_build_route_fromdb()

    allconfig = ''
    allconfig = inter_config+ \
                addr_book+ \
                addr_book_group+ \
                service+ \
                service_group+ \
                extended_acl+ \
                nat_config+route_config
    writefile(newfileuri, allconfig)

    # list4=string4.split('\n')
    # list5=[]
    # for fstr in list4:
    #     if fstr not in list5:
    #         list5.append(fstr)
    # string5=''
    # # for fstr in list5:
    #     string5=string5+create_service(fstr)

    # fa = open('create_service_' + temptime + '.txt', 'w')
    # fa.writelines(string5)
    # fa.close()
    return 'OK'
