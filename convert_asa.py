#coding:utf-8
from en_mouth_to_num import *
import time
from opensrcfile import *
import os
from creatdb import *
import re


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
            pass
        elif 'nameif' in words:
            zone=words[1]
        elif 'ip' in words and 'address' in words:
            '''
            interface GigabitEthernet0/7
             description connect to WGQKF
             nameif WGQKF
             security-level 90
             no ip address
            !
            '''
            if 'no' in words:
                pass
            else:
                ipaddr=words[2]+' '+words[3]
        j += 1
    # j -= 1
    return temp,j

def asa_trans_schedu(srcfile,j):
    words = srcfile[j].split()
    string = 'schedule ' + words[1] + '\n' #list[1]中是对象名字
    j += 1
    while (j < len(srcfile)):
        words =  srcfile[j].split()
        if '!' in words:
            break
        if 'absolute' in words:
            m = words.index('start')
            starttime = words[m+1]
            startday = words[m+2]
            startmouth = words[m + 3]
            startmouth = en_mouth_to_num(startmouth)
            startyear = words[m + 4]
            n = words.index('end')
            endtime = words[n + 1]
            endday = words[n + 2]
            endmouth = words[n + 3]
            endmouth = en_mouth_to_num(endmouth)
            endyear = words[n + 4]
            string = string + ' absolute start ' + startmouth + '/' + startday + '/' + startyear + ' ' + starttime
            string = string + ' end ' + endmouth + '/' + endday + '/' + endyear + ' ' + endtime + '\n'
            string = string + 'exit\n'
        j += 1
    return string,j


def asa_exchangemask(mask_b):
    try:
        exchange_mask = lambda mask: sum(bin(int(i)).count('1') for i in mask.split('.'))
    except:
        print('911')
    mask_d = str(exchange_mask(mask_b))
    return mask_d


def asa_addr_trans(list,j):
    #object network ZJLKF_10.7.30.0_24
    # subnet 10.7.30.0 255.255.255.0
    #object network VPN_10.120.254.0
    # host 10.120.254.13

    words=list[j].split()
    addrname=words[2]
    j+=1
    temp='address '+addrname+'\n'
    while(j<len(list)):
        words = list[j].split()  # 第二行，定义内容部分
        if 'subnet' in words:
            ipnet=words[1]
            netmask=asa_exchangemask(words[2])
            temp+=' ip ' +ipnet + '/' + netmask+'\n'

            query = "insert into address(name,type,net) values(?,?,?);"
            tmplist = [addrname, 'ip', ipnet + '/' + netmask]
            insert2table_new(query, tmplist)

        elif 'host' in words:
            ip=words[1]
            temp+=' ip '+ip+'/32\n'

            query = "insert into address(name,type,net) values(?,?,?);"
            tmplist = [addrname, 'ip', ip + '/32']
            insert2table_new(query, tmplist)


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

def asa_addr_group_trans(srcfile,j):
#object-group network DM_INLINE_NETWORK_1
 # group-object PT04AC
 # network-object host 10.190.51.19

    words = srcfile[j].split()
    addr_group_name = words[2]
    j += 1
    temp = 'address ' + addr_group_name + '\n'
    while (j < len(srcfile)):
        words = srcfile[j].split()  # 下一行，定义内容部分
        #group-object PT04AC
        if ('network-object' not in words ) and ('group-object' not in words ):
            break
        elif ('object' in words ):
            member = words[2]

            query = "insert into addr_group(addr_group_name,member) values(?,?);"
            tmplist = [addr_group_name, member]
            insert2table_new(query, tmplist)

            temp += ' member ' + member + '\n'
        elif 'group-object' in words:
            member = words[1]

            query = "insert into addr_group(addr_group_name,member) values(?,?);"
            tmplist = [addr_group_name, member]
            insert2table_new(query, tmplist)

            temp += ' member ' + member + '\n'
        elif 'description' in words:
            temp += srcfile[j]
        elif 'host' in words:
            # network-object host PT02DI-SF1-10.190.57.89

            ip = words[2]
            #先判断是否包含有英文字母，
            p = 0
            for l in ip:
                if l.isalpha():#有英文字母，
                    p = 1
                    break
            if p == 1:#有英文字母，
                query = "insert into addr_group(addr_group_name,member) values(?,?);"
                tmplist = [addr_group_name, ip]
                insert2table_new(query, tmplist)

                temp += ' member ' + ip + '\n'
            else:
                query = "insert into addr_group(addr_group_name,member,ipaddr) values(?,?,?);"
                tmplist = [addr_group_name, 'ip',ip+'/32']
                insert2table_new(query, tmplist)
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
    return temp,j

def service_trans(alist,j):
    temp = ''
    words = alist[j].split()
    # object service tcp-61060
    #  service tcp source range 1 65535 destination eq 61060
    # object service tcp_12335，版本8.4（7）23
    #  service tcp destination eq 12335
    service_name = words[2]
    j += 1
    while (j < len(alist)):
        words = alist[j].split()  # 第二行，定义内容部分

        pattern1 = re.compile(r'service (tcp|udp) source range (\d+) (\d+) destination eq (\d+)')
        match1 = pattern1.search(alist[j])

        pattern2 = re.compile(r'service (tcp|udp) destination eq (\d+)')
        match2 = pattern2.search(alist[j])

        pattern3 = re.compile(r'service (tcp|udp) destination eq')
        match3 = pattern3.search(alist[j])

        pattern4 = re.compile(r'service (tcp|udp) source range')
        match4 = pattern4.search(alist[j])

        if (not match3) and (not match4):#'service (tcp|udp) destination eq'不在这一行中，则结束循环。
            break

        if match1:  # service tcp source range 1 65535 destination eq 61060
            prot = words[1]
            port = words[8]
        elif match2:
            prot = words[1]
            port = words[4]

        # 查port在表中对应的端口号，
        if not port:
            continue
        elif port.isdigit():  # port中全是数字，则这是表示端口的，
            # servname = prot + '-' + port
            # 将此作为新服务，插入到表中
            query = "insert into service_s(servname,proto,dstport) values(?,?,?);"
            tmplist = [service_name, prot, port]
            insert2table_new(query, tmplist)
            temp += ' service ' + service_name + '\n'
            temp += prot + ' dst-port ' + port + '\n'
        else:  # 去表中查对应的hillstone名字，这时port中一般是英文，比如ftp、ssh等，
            query = 'select  distinct hillservname from predeservmatch where origservname="%s";' % port
            temp1 = fetchallfrom(query)  # temp1=[(443,)]
            if temp1:
                port = list(temp1[0])[0]
                temp += ' service ' + port + '\n'

        if 'description' in words:
            temp += alist[j]
        elif 'destination range' in alist[j]:
            portstart = words[4]
            portend = words[5]
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

	# object service tcp_12335，版本8.4（7）23
	# service tcp destination eq 12335

	# object-group service PT02DI_services_1
	# service-object tcp destination eq 50000
	# service-object tcp destination eq 60000
    words = alist[j].split()#object-group service PT02DI_services_1
    service_group_name = words[2]
    prot = ''
    temp = 'servgroup ' + service_group_name + '\n'
    if 'tcp' in words or 'udp' in words or 'tcp-udp' in words:#判断是不是直接定义型的服务组，
        '''
        object-group service DM_INLINE_TCP_28 tcp
          port-object eq 8083
          port-object eq https
        object-group service 3G-PAD-service tcp-udp
            port-object eq 7778
            port-object eq 7004
        '''
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
                    if '-' in prot:
                        query = "insert into service_s(servname,proto,dstport) values(?,?,?);"
                        tmplist = [servname, 'tcp', port]
                        insert2table_new(query, tmplist)
                        tmplist = [servname, 'udp', port]
                        insert2table_new(query, tmplist)
                    else:
                        query = "insert into service_s(servname,proto,dstport) values(?,?,?);"
                        tmplist = [servname, prot, port]
                        insert2table_new(query, tmplist)

                    query = "insert into service_group(servg_name,member) values(?,?);"
                    tmplist = [service_group_name, servname]
                    insert2table_new(query, tmplist)

                    temp += ' service ' + servname + '\n'
                else:  # 去表中查对应的hillstone名字，这时port中一般是英文，比如ftp、ssh等，
                    query = 'select  distinct hillservname from predeservmatch where origservname="%s";' % port
                    temp1 = fetchallfrom(query)  # temp1=[(443,)]
                    if temp1:
                        port = list(temp1[0])[0]

                        query = "insert into service_group(servg_name,member) values(?,?);"
                        tmplist = [service_group_name, port]
                        insert2table_new(query, tmplist)

                        temp += ' service ' + port + '\n'
            elif 'group-object' in words:
                servname = words[1]
                query = "insert into service_group(servg_name,member) values(?,?);"
                tmplist = [service_group_name, servname]
                insert2table_new(query, tmplist)

            elif 'description' in words:
                temp += alist[j]
            elif 'range' in words:
                portstart = words[2]
                portend = words[3]
                servname = prot + '-' + portstart + '-' + portend

                if not portstart.isdigit():  # port中不是数字，
                    # 将portstart，比如是ftp-data替换为20，
                    query = 'select  distinct dstport1 from predeservmatch where origservname="%s";' % portstart
                    temp1 = fetchallfrom(query)  # temp1=[(443,)]
                    if temp1:
                        portstart = list(temp1[0])[0]

                if not portend.isdigit():  # port中不是数字，
                    query = 'select  distinct dstport1 from predeservmatch where origservname="%s";' % portend
                    temp1 = fetchallfrom(query)  # temp1=[(443,)]
                    if temp1:
                        portend = list(temp1[0])[0]

                query = "insert into service_range(servname,proto,dstport1,dstport2) values(?,?,?,?);"
                tmplist = [servname, prot, portstart, portend]
                insert2table_new(query, tmplist)

                query = "insert into service_group(servg_name,member) values(?,?);"
                tmplist = [service_group_name, servname]
                insert2table_new(query, tmplist)

                temp += ' service ' + servname + '\n'
            elif 'port-object' not in words:
                break
            j += 1
    else:
        j += 1
        while (j < len(alist)):
            words = alist[j].split()  # 第二行，定义内容部分
            if not words:#如果这一行是空行。
                break

            pattern1 = re.compile(r'service (tcp|udp) source range (\d+) (\d+) destination eq (\d+)')
            match1 = pattern1.search(alist[j])

            pattern2 = re.compile(r'(service-object) (tcp|udp) destination eq ')
            match2 = pattern2.search(alist[j])

            pattern3 = re.compile(r' group-object ')
            match3 = pattern3.search(alist[j])

            pattern4 = re.compile(r' service-object icmp ')
            match4 = pattern4.search(alist[j])

            pattern6 = re.compile(r' service-object object ')
            match6 = pattern6.search(alist[j])

            #service-object tcp destination range 9070 9086
            #service-object tcp-udp destination range 161 162
            pattern5 = re.compile(r' service-object (tcp|udp|tcp-udp) destination range ')
            match5 = pattern5.search(alist[j])

            if match1:#service tcp source range 1 65535 destination eq 61060
                prot = words[1]
                port = words[8]
            elif match2:
                prot = words[1]
                port = words[4]
            elif match5:
                #service-object tcp destination range 9070 9086
                # service-object tcp-udp destination range 161 162
                prot = words[1]
                port1 = words[4]
                port2 = words[5]
                servname = prot + '-' + port1 + '-' + port2

                if '-' in prot:
                    query = "insert into service_range(servname,proto,dstport1,dstport2) values(?,?,?,?);"
                    tmplist = [servname, 'tcp', port1, port2]
                    insert2table_new(query, tmplist)
                    tmplist = [servname, 'udp', port1, port2]
                    insert2table_new(query, tmplist)
                else:
                    # 将此作为新服务，插入到表中
                    query = "insert into service_range(servname,proto,dstport1,dstport2) values(?,?,?,?);"
                    tmplist = [servname, prot, port1, port2]
                    insert2table_new(query, tmplist)

                query = "insert into service_group(servg_name,member) values(?,?);"
                tmplist = [service_group_name, servname]
                insert2table_new(query, tmplist)

                temp += ' service ' + servname + '\n'
                j += 1
                continue
            elif match3:
                servname = words[1]
                query = "insert into service_group(servg_name,member) values(?,?);"
                tmplist = [service_group_name, servname]
                insert2table_new(query, tmplist)
                j += 1
                continue
            elif match6:
                servname = words[2]
                query = "insert into service_group(servg_name,member) values(?,?);"
                tmplist = [service_group_name, servname]
                insert2table_new(query, tmplist)
                j += 1
                continue

            elif match4:
                port = 'ICMP'
                query = "insert into service_group(servg_name,member) values(?,?);"
                tmplist = [service_group_name, port]
                insert2table_new(query, tmplist)
                j += 1
                continue

            #查port在表中对应的端口号，
            if not port:
                j += 1
                continue
            elif port.isdigit():#port中全是数字，则这是表示端口的，
                servname = prot + '-' + port
                #将此作为新服务，插入到表中
                query = "insert into service_s(servname,proto,dstport) values(?,?,?);"
                tmplist = [servname, prot, port]
                insert2table_new(query, tmplist)
                temp += ' service ' + servname + '\n'

                query = "insert into service_group(servg_name,member) values(?,?);"
                tmplist = [service_group_name,servname]
                insert2table_new(query, tmplist)
            else:#去表中查对应的hillstone名字，这时port中一般是英文，比如ftp、ssh等，
                query = 'select  distinct hillservname from predeservmatch where origservname="%s";' % port
                temp1=fetchallfrom(query)#temp1=[(HTTPS,)]
                if temp1:
                    port=list(temp1[0])[0]

                    query = "insert into service_group(servg_name,member) values(?,?);"
                    tmplist = [service_group_name, port]
                    insert2table_new(query, tmplist)

                    temp += ' service ' + port + '\n'

            if 'description' in words:
                temp += alist[j]
            elif 'destination range' in alist[j]:
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
        #object-group DM_INLINE_NETWORK_391 any
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
        # 172.26.149.32 255.255.255.224 172.26.141.0 255.255.255.0
        #host 172.25.241.56 host 172.26.156.1
        #10.44.0.0 255.255.0.0 host 172.26.140.3
        #object PMO_21F_IP object-group 21F_BL_UAT_IP
        #object-group OBJ-BaoLeiJi-1 host 10.20.65.13
        #object-group OBJ-WangYinDD-RE-1 10.0.0.0 255.0.0.0
        # 21.237.0.0 255.255.0.0 object-group pmo_mobl_svr
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
                # object-group OBJ-WangYinDD-RE-1 10.0.0.0 255.0.0.0
                dstip = alist[7] + '/' + asa_exchangemask(alist[8])
                string2 = ' src-addr ' + srcip + '\n dst-ip ' + dstip + '\n'
        else:
            srcip=alist[5]+'/'+ asa_exchangemask(alist[6])
            if alist[7] == 'any':
                pass
            elif alist[7] == 'host':
                dstip = alist[8] + '/32'
                string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
            elif alist[7] == 'object' or alist[7] == 'object-group':
                # 21.237.0.0 255.255.0.0 object-group pmo_mobl_svr
                dstip = alist[8]
                string2 = ' src-ip ' + srcip + '\n dst-addr ' + dstip + '\n'
            else:
                dstip = alist[7] + '/' + asa_exchangemask(alist[8])
                string2 = ' src-ip ' + srcip + '\n dst-ip ' + dstip + '\n'
    return string2





def asa_acl_aftertcpudp(alist,proto):
    words = alist.split()
    #alist:
    #access-list outside_acl extended permit tcp any host 22.237.188.132 eq 445
    #access-list outside_acl extended permit tcp object PMO_21F_IP object-group 21F_BL_UAT_IP eq 50000
    #access-list outside_access_in extended permit tcp host 123.138.28.20 object-group ZJXQD-WEB object-group DM_INLINE_TCP_131
    string3=''
    serviceend=''
    global string4
    service=''

    pattern = re.compile(r'host ((\d+)\.(\d+)\.(\d+)\.(\d+)) object-group ((\w*)(-*)(\w*)) object-group ')
    match = pattern.search(alist)

    if match:
        service = words[10]
        # string3 += asa_acl_src_dst_addr(words, (len(words) - 3))
        # (len(words) - 3)是地址串中最后一个元素的下标，即目的地址的下标，
        string3 += ' src-ip ' + words[6] + '/32\n'
        string3 += ' dst-addr ' + words[8] + '\n'
        string3 += ' service ' + service + '\n'

    elif 'eq' in words:
        m = words.index('eq')
        string3 = string3 + asa_acl_src_dst_addr(words, (m - 1))  # 源目的地址部分，交给地址转换函数

        port = words[m + 1]#下一步到2个表中查此端口对应的服务名字，
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

        if 'time-range' in words:
            m = words.index('time-range')
            schedule = words[m + 1]
            string3 = string3 + ' schedule ' + schedule + '\n'
    elif 'range' in words:
        # extended permit tcp any host 172.26.158.2 range www 81
        # extended permit tcp host 30.32.14.220 host 30.39.252.198 range ssh telnet
        m = words.index('range')
        string3 = string3 + asa_acl_src_dst_addr(words, (m - 1))  # 交给地址转换函数

        portstart = words[m+1]
        portend = words[m+2]
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

        service = portstart + '-' + portend  # words[m+2]是range中的结束端口
        string4 +=  service + '\n'
        service= proto +'-'+service
        query = "insert into service_range(servname,proto,dstport1,dstport2) values(?,?,?,?);"
        tmplist = [service, proto, portstart, portend]
        insert2table_new(query, tmplist)


        string3 = string3 + ' service ' + service + '\n'
        if 'time-range' in words:
            m = words.index('time-range')
            schedule = words[m + 1]
            string3 = string3 + ' schedule ' + schedule + '\n'
    elif 'time-range' in words:  # 这一行没有端口，是tcp-any，
        # extended permit tcp host 172.26.73.52 host 172.26.153.17 time-range 20181231
        m = words.index('time-range')
        service = 'tcp-any'
        string3 = string3 + asa_acl_src_dst_addr(words, (m - 1))  # 交给地址转换函数
        string3 = string3 + ' service ' + service + '\n'
        schedule = words[m + 1]
        string3 = string3 + ' schedule ' + schedule + '\n'
    elif 'object-group' in words:
#access-list OAS-OUTSIDE-ACL extended deny tcp 10.20.190.0 255.255.255.0 host 10.20.64.10 object-group GBDK-PORT
        # if words.index('object-group') == (len(words)-2):
        if words[len(words)-2] == 'object-group':
            #倒数第二个元素是object-group，则这个是服务，
            service = words[(len(words)-1)]#最后一个元素是具体服务簿，
            string3 += asa_acl_src_dst_addr(words, (len(words) - 3))
            #(len(words) - 3)是地址串中最后一个元素的下标，即目的地址的下标，
            string3 = string3 + ' service ' + service + '\n'
    else:
        # tcp 172.26.149.32 255.255.255.224 172.26.141.0 255.255.255.0
        # tcp any any
        # tcp 10.20.190.0 255.255.255.0 host 10.20.64.10 object-group GBDK-PORT
        if words[4]=='tcp':
            service = 'tcp-any'
        else:
            service = 'udp-any'
        string3 = string3 + asa_acl_src_dst_addr(words, (len(words) - 1))
        string3 = string3 + ' service ' + service + '\n'

    return string3


def asa_trans_extend_acl(alist,j):
    string = ''
    servicestart = ''
    srczone = ''
    dstzone = ''
    #access-list dmz_access_in extended permit ip object-group DM_INLINE_NETWORK_391 any inactive
    while (j < len(alist)):
        words = alist[j].split()  #
        query = "insert into line(line) values(?);"
        tmplist = [str(j)]
        insert2table_new(query, tmplist)

        if 'extended' not in words:
            break
        m = words.index('extended')
        aclname = words[m - 1]
        action = words[m + 1]
        # string += '#This is ' + aclname + '\n'
        # string += '#Thist is line'+ str(j+1) +'\n'

        # string += 'rule id ' + str(j+1)+ '\n' \
        #           ' action ' + action + '\n'
        if 'inactive' in words:
            string += 'rule\n'+ \
                    ' disable\n'+ \
                    ' action ' + action + '\n'
            words.remove('inactive')
        else:
                    # string += 'rule\n' + \        # 如果不需要ruleid，就用这行。
            string += 'rule id ' + str(j + 1) + '\n' \
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
            #access-list outside_acl extended permit ip 21.237.0.0 255.255.0.0 object-group pmo_mobl_svr log inactive
            service = 'any'
            if 'time-range' in words:
                m = words.index('time-range')
                string = string + asa_acl_src_dst_addr(words, (m- 1))
                string = string + ' service ' + service + '\n'
                schedule = words[m + 1]
                string = string + ' schedule ' + schedule + '\n'
            elif 'log' in words:
                #21.237.0.0 255.255.0.0 object-group pmo_mobl_svr log
                m = words.index('log')
                string = string + asa_acl_src_dst_addr(words, (m - 1))
                string = string + ' service ' + service + '\n'
                string = string + ' log session-start\n' + \
                    ' log session-end\n'
            else:
                string = string + asa_acl_src_dst_addr(words, (len(words) - 1))
                string = string + ' service ' + service + '\n'
            string = string + 'exit\n\n'
        elif words[k] == 'tcp':# 判断下标为4的元素是tcp
            #eg.permit tcp host 172.26.136.148 any eq https time-range 20171231
            #eg.permit tcp 172.26.149.32 255.255.255.224 172.26.141.0 255.255.255.0
            #access-list outside_acl extended permit tcp object PMO_21F_IP object-group 21F_BL_UAT_IP eq 50000
            string = string + asa_acl_aftertcpudp(alist[j],words[k])
            string = string + 'exit\n\n'
        #print(list[j])
        elif words[k] == 'udp': # 判断下标为4的元素是udp
            #print('653')
            string = string + asa_acl_aftertcpudp(alist[j],words[k])
            string = string + 'exit\n\n'
        elif words[k] == 'object-group':
#access-list outside_acl extended permit object-group QUOSPAP_SVC object UAT_IP_OSP object-group QUOSPAP_SVR
#access-list outside_access_in extended permit object-group DM_INLINE_SERVICE_22 any host 10.190.173.28
            service=words[k+1]#下标为5的元素是服务，

            pattern = re.compile(r'extended (permit|deny) object-group ((\w*)(\d*)) any host ')
            match = pattern.search(alist[j])
            #access-list outside_access_in extended permit object-group sxwifi-group any object sxwifi-10.190.178.139
            pattern2 = re.compile(r'extended (permit|deny) object-group ((\w*)(-*)(\w*)(\d*)) any (object|object-group) ')
            match2 = pattern2.search(alist[j])

            # access-list outside_access_in extended permit tcp object-group DM_INLINE_NETWORK_269 object-group DM_INLINE_NETWORK_270 object-group DM_INLINE_TCP_117
            pattern3 = re.compile(r'extended (permit|deny) (tcp|udp) object-group ((\w*)(\d*)) (object|object-group) ((\w*)(\d*)) (object|object-group)')
            match3 = pattern3.search(alist[j])

            #access-list dmz_access_in extended permit object-group DM_INLINE_SERVICE_10 host 10.190.177.230 object-group REQ051058_EX
            pattern4 = re.compile(r'extended (permit|deny) object-group ((\w*)(\d*)) host ((\d+)\.(\d+)\.(\d+)\.(\d+)) (object|object-group)')
            match4 = pattern4.search(alist[j])

            if match:
                string += ' src-addr any\n'
                string += ' dst-ip ' + words[8] + '/32\n'
                string += ' service ' + words[5] + '\n'
                string += 'exit\n\n'
                j += 1
                continue
            elif match2:
                string += ' src-addr any\n'
                string += ' dst-addr ' + words[8] + '\n'
                string += ' service ' + words[5] + '\n'
                string += 'exit\n\n'
                j += 1
                continue
            elif match3:
                string += ' src-addr ' + words[6] + '\n'
                string += ' dst-addr ' + words[8] + '\n'
                string += ' service ' + words[10] + '\n'
                string += 'exit\n\n'
                j += 1
                continue
            elif match4:
                string += ' src-ip ' + words[7] + '/32\n'
                string += ' dst-addr ' + words[9] + '\n'
                string += ' service ' + words[5] + '\n'
                string += 'exit\n\n'
                j += 1
                continue

            #下面有待改进为上面的调用函数形式。
            if words[k+2] =='object' or words[k+2] =='object-group':# 下标为6的元素是源地址，object或object-group
                #object-group QUOSPAP_SVC object UAT_IP_OSP object-group QUOSPAP_SVR
                string += ' src-addr '+ words[k+3] + '\n'
            else:
                #object-group QUOSPAP_SVC 192.168.2.0 255.255.255.0 object-group QUOSPAP_SVR
                string += ' src-ip '+ words[k+2] + '/' + asa_exchangemask(words[k+3]) + '\n'
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
    words = alist[j].split()
    #nat (inside,nat_network) source static buixpgw1 buixpgw1_nat
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

    # query = 'select * from service_s group by servname having count(servname)>=1;'
    query = 'select max(id),servname,proto,dstport from service_s group by servname,proto,dstport having id is not null;'
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



    qurey = "CREATE TABLE IF NOT EXISTS line(id integer primary key autoincrement, \
                    line TEXT);"
    creat_table(qurey)

    qurey = "CREATE TABLE IF NOT EXISTS address(id integer primary key autoincrement, \
                    name TEXT, \
                    type TEXT, \
                    net TEXT);"
    creat_table(qurey)

    qurey = "CREATE TABLE IF NOT EXISTS addr_group(id integer primary key autoincrement, \
                    addr_group_name TEXT, \
                    member TEXT, \
                    ipaddr TEXT);"
    creat_table(qurey)


    qurey = "CREATE TABLE IF NOT EXISTS service_s(id integer primary key autoincrement, \
                servname TEXT, \
                proto TEXT, \
                dstport TEXT);"
    creat_table(qurey)

    qurey = "CREATE TABLE IF NOT EXISTS service_group(id integer primary key autoincrement, \
                servg_name TEXT, \
                member TEXT);"
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
    schedu_count = 0
    addr_book_count = 0
    addr_book_group_count = 0
    service_count = 0
    servgroup_count = 0
    standard_acl_count = 0
    extended_acl_count = 0
    i =0
    while (i < len(srcfile)):
        words = srcfile[i].split()#当前行存储在列表words中，

        query = "insert into line(line) values(?);"
        tmplist = [str(i)]
        insert2table_new(query, tmplist)

        if 'time-range' in words and 'access-list' not in words:
            (schedu_str_temp,i)  = asa_trans_schedu( srcfile,i )
            schedu_str  += schedu_str_temp
            schedu_count += 1
        elif 'interface' in words and len(words)==2:
            (inter_temp,i) = asa_interface_trans(srcfile,i)
            inter_config += inter_temp
        elif 'object' in words and 'network' in words:#地址转换
            (addr_book_temp,i)= asa_addr_trans(srcfile,i)
            addr_book += addr_book_temp
            addr_book_count += 1
        elif 'object-group' in words and 'network' in words:#地址组转换
            (addr_book_group_temp,i) = asa_addr_group_trans(srcfile, i)
            addr_book_group += addr_book_group_temp
            addr_book_group_count += 1
        elif 'object service ' in srcfile[i]:#服务的转换
            (service_temp, i) = service_trans(srcfile, i)
            service_group += service_temp
            service_count += 1
        elif ('object-group' in words or 'object' in words) and 'service' in words:#服务组转换
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

			#object service tcp_12335，版本8.4（7）23
 			# service tcp destination eq 12335
			#object-group service PT02DI_services_1
 			# service-object tcp destination eq 50000
 			# service-object tcp destination eq 60000

            (service_temp, i) = service_group_trans(srcfile, i)
            service_group += service_temp
            servgroup_count += 1
        elif 'access-list' in words and ('standard' in words ):#标准ACL转换，
            pass
            #standard_acl = standard_acl + asa_trans_standard_acl(words)
        elif 'access-list' in words and ('extended' in words):#扩展ACL转换，
            # break
            (acl_temp,i) = asa_trans_extend_acl(srcfile,i)
            extended_acl += acl_temp
            extended_acl_count += 1
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


    newfileuri = filepath + '/'+origfilename+'_转换的各模块内容数量统计_' + temptime + '.txt'
    statistic = '' + \
        '转换了' + str(schedu_count) + '个时间表，\n' + \
        '转换了' + str(addr_book_count) + '个地址簿，\n' + \
        '转换了' + str(addr_book_group_count) + '个地址组，\n' + \
        '转换了' + str(servgroup_count) + '个服务组，\n' + \
        '转换了' + str(standard_acl_count) + '个标准ACL(安全策略)，\n' + \
        '转换了' + str(extended_acl_count) + '个扩展ACL(安全策略)。'
    writefile(newfileuri,statistic)

    return 'OK'
