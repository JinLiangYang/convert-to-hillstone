from opensrcfile import *
import time
from creatdb import *
import IPy
import re
from allrangeip import *

def isIP(str):
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(str):
        return True
    else:
        return False

def exchangemask(mask_b):
    try:
        exchange_mask = lambda mask: sum(bin(int(i)).count('1') for i in mask.split('.'))
    except:
        print('911')
    mask_d = str(exchange_mask(mask_b))
    return mask_d


def transaddr_host(list):
    '''
    e.g:
    ID 8040 define host add name H:SSN隔离区:开发:MAP:食品溯源 ipaddr '202.105.50.148 ' vsid 0
    '''
    m=list.index('name')
    addrname=list[m+1]
    ip=list[m+3]
    ip=ip.replace('\'','')
    output= \
    'address '+addrname+'\n' \
    ' ip '+ip+'/32'+'\n' \
    'exit\n'
    query = "insert into address_host(name,type,ip) values(?,?,?);"
    tmplist2 = [addrname, 'ip', ip+'/32']
    insert2table_new(query, tmplist2)

    return output

def transaddr_subnet(list):
    '''
    ID 8041 define subnet add name 子网:广东局:广东局网段 ipaddr 10.44.0.0 mask 255.255.0.0 vsid 0
    :param list:
    :return:
    '''
    m = list.index('name')
    addrname = list[m + 1]
    net = list[m + 3]#网段
    m=list.index('mask')
    mask=list[m+1]
    mask=exchangemask(mask)
    net += '/' + mask
    output = \
    'address ' + addrname + '\n' \
    ' ip ' + net + '\n' \
    'exit\n'

    query = "insert into address_host(name,type,ip) values(?,?,?);"
    tmplist2 = [addrname, 'ip', net]
    insert2table_new(query, tmplist2)

    return output

def transaddr_range(list):
    '''
    ID 8001 define range add name any ip1 0.0.0.0 ip2 255.255.255.255 vsid 0
    :param list:
    :return:
    '''
    m = list.index('name')
    addrname = list[m + 1]
    if addrname=='any':
        return '\n'
    m=list.index('ip1')
    startip=list[m+1]
    endip=list[m+3]
    output = \
    'address ' + addrname + '\n' \
    ' range ' + startip + ' '+ endip + '\n' \
    'exit\n'

    query = "insert into address_range(name,type,ip1,ip2) values(?,?,?,?);"
    tmplist2 = [addrname, 'range', startip,endip]
    insert2table_new(query, tmplist2)


    return output

def transaddr_group(list):
    '''
    ID 8059 define group_address add name G:内网:网管部 member 'H:内网:网管部:xph ' vsid 0
    :param list:
    :return:
    '''
    m=list.index('name')
    addrgrvp_name=list[m+1]
    m=list.index('member')
    member=list[m+1]
    output = \
    'address ' + addrgrvp_name + '\n' \
    ' member ' + member + '\n' \
    'exit\n'
    return output

def transservice(list):
    '''
    ID 8066 define service add name SS:电子监管:8080 protocol 6 port 8080 vsid 0
    ID 8126 define service add name SS:正贸k3:9000-9600 protocol 6 port 9000 port2 9600 vsid 0
    :param list:
    :return:
    '''
    m = list.index('name')
    service_name=list[m+1]
    # try:
    m = list.index('protocol')
    # except:
    #     print(list)
    #     exit()
    protocol=list[m+1]
    if protocol=='6':
        protocol='tcp'
    elif protocol=='17':
        protocol='udp'
    m = list.index('port')
    startport=list[m+1]
    output='service '+service_name+'\n' \
    ' '+protocol+' dst-port '+startport
    if 'port2' in list:
        m=list.index('port2')
        endport=list[m+1]
        output+=' '+endport
    output +='\n' \
    'exit\n'
    return output


def findall_inpolicy(target,list):#找出policy中的多个源地址或多个服务，放在列表中，
    '''
    从target往后一个个判断，然后写入target_list中。
    ID 8572 firewall policy add action accept src 'H:电子口岸:运维:远端服务器 H:电子口岸:运维:远端广域网地址 ' dst 'H:SSN隔离区:发展对外MQ数据交互 ' service 'tcp-1404 PING '  vsid 0
    :param list:
    :return:
    '''
    target_list=[]
    m=list.index(target)
    target_list.append(list[m + 1].replace('\'', ''))
    n = 2
    while 1:
        if list[m + n] == '\'':
            break
        else:
            target_list.append(list[m + n])
        n += 1
    return  target_list


def transpolicy(alist,k):
    '''
    ID 8594 firewall policy add action accept dstarea 'SSN区交换机(202.105.50.157) ' src 'H:SSN隔离区:技术中心门户系统 '  vsid 0
    ID 8572 firewall policy add action accept src 'H:电子口岸:运维:远端服务器 H:电子口岸:运维:远端广域网地址 ' dst 'H:SSN隔离区:发展对外MQ数据交互 ' service 'tcp-1404 PING '  vsid 0
    :param list:
    :return:
    '''
    words = alist[k].split()#当前行，在words列表中。
    m=words.index('action')
    action=words[m+1]
    ruleid=words[m-4]
    output = ''
    status = ''
    src_zone = ''
    dst_zone = ''
    src_addr = 'any'
    dst_addr = 'any'
    service = ''

    if action=='accept':
        action = 'permit'
    else:
        action = 'deny'
    if 'no' in words:
        status = 'disable'
    if 'srcarea' in words:
        m=words.index('srcarea')
        src_zone=words[m+1].replace('\'','')
    if 'dstarea' in words:
        m=words.index('dstarea')
        #dstarea 'SSN区交换机(202.105.50.157) ' src
        dst_zone=words[m+1].replace('\'','')#去掉安全域带的单引号，
        # output +=' dst-zone ' + dstzone +'\n'

    #开始有多个取值了：
    if 'src' in words:
        srca_list=findall_inpolicy('src',words)
        if len(srca_list) == 1:
            src_addr = srca_list[0]
        else:
            src_addr = ','.join(srca_list)
        # output += ' src-addr ' + srca + '\n'
    if 'dst' in words:
        dsta_list = findall_inpolicy('dst', words)
        if len(dsta_list) == 1:
            dst_addr = dsta_list[0]
        else:
            dst_addr = ','.join(dsta_list)
        # output += ' dst-addr any\n'
    if 'service' in words:
        service_list=findall_inpolicy('service',words)
        if len(service_list) == 1:
            service = service_list[0]
        else:
            service = ','.join(service_list)

    query = "insert into policy(ruleid,status,action,src_zone,dst_zone,src_addr,dst_addr,service) values(?,?,?,?,?,?,?,?);"
    tmplist2 = [ruleid,status,action,src_zone,dst_zone,src_addr,dst_addr,service]
    insert2table_new(query, tmplist2)

    return k


def find_pubip(a_string):
    pubip_list = []

    # 找出list(atuple)[7]（地址簿名字）中有哪些ip。并找出它们对应的DNAT中的公网ip。
    query = 'select ip from address_host where name="%s";' % a_string
    temp2 = fetchallfrom(query)  # temp2=[(1,)]

    query = 'select dst_addr,trans_to from dnat ;'
    temp3 = fetchallfrom(query)  # temp3=[(pubip,privip)]

    if temp2:  # 如果策略中的地址簿名字在address_host中。
        dst_prvi_ip_in_orig_policy = ''.join(temp2[0])
        if temp3:
            for ip_tuple in temp3:  # ip_tuple=(pubip,privip)
                ip_tuple_list = list(ip_tuple)  # ip_tuple_list=[pubip,privip]
                pubip = ip_tuple_list[0]
                privip = ip_tuple_list[1]

                # 还需要判断privip是ip地址，还是地址簿。
                if isIP(privip):
                    pass
                else:
                    query = 'select ip from address_host where name="%s";' % privip
                    temp5 = fetchallfrom(query)  # temp5=[(1,)]
                    if temp5:
                        privip = ''.join(temp5[0])
                if privip in IPy.IP(dst_prvi_ip_in_orig_policy):
                    pubip_list.append(pubip)
                    # policy_rule += ' dst-ip ' + pubip + '/32\n'
        else:
            pass
    else:  # 如果策略中的地址簿名字在address_host中找不到，就去address_range中查找。
        query = 'select ip1,ip2 from address_range where name="%s";' % a_string
        temp4 = fetchallfrom(query)  # temp4=[(ip1,ip2)]
        if temp4:
            dst_prvi_ip1_in_orig_policy = list(temp4[0])[0]
            dst_prvi_ip2_in_orig_policy = list(temp4[0])[1]
            # 原策略中包含的原目的地址有,从ip1到ip2。
            dst_priv_ip_list = show_all_range_ip(dst_prvi_ip1_in_orig_policy, dst_prvi_ip2_in_orig_policy)
            if temp3:
                # for a_dst_priv_ip in dst_priv_ip_list:
                for ip_tuple in temp3:  # ip_tuple=(pubip,privip)
                    ip_tuple_list = list(ip_tuple)  # ip_tuple_list=[pubip,privip]
                    pubip = ip_tuple_list[0]
                    privip = ip_tuple_list[1]
                    # 还需要判断privip是ip地址，还是地址簿。
                    if isIP(privip):
                        pass
                    else:
                        query = 'select ip from address_host where name="%s";' % privip
                        temp5 = fetchallfrom(query)  # temp5=[(1,)]
                        if temp5:
                            privip = ''.join(temp5[0])
                    # if privip in IPy.IP(a_dst_priv_ip):
                    if privip in dst_priv_ip_list:
                        pubip_list.append(pubip)
                        # policy_rule += ' dst-ip ' + pubip + '/32\n'
        else:
            pass

    return pubip_list


def topsec_build_policy_fromdb():
    policy_rule = ''
    srcaddr_list = []
    dstaddr_list = []
    service_list = []

    query = 'select * from policy ;'
    temp1 = fetchallfrom(query)  # temp1=[()]
    if temp1:
        for atuple in temp1:
            # atuple=(id,ruleid,status,action,src_zone,dst_zone,src_addr,dst_addr,service)
            policy_rule += 'rule id ' + list(atuple)[1] + '\n'
            if list(atuple)[2]:#list(atuple)[2]是status,非空时。
                policy_rule += ' ' + list(atuple)[2] + '\n'
            policy_rule += ' action ' + list(atuple)[3] + '\n'
            if list(atuple)[4]:  # list(atuple)[4]是源安全域,非空时。
                policy_rule += ' src-zone ' + list(atuple)[4] + '\n'
            if list(atuple)[5]:  # list(atuple)[5]是目的安全域,非空时。
                policy_rule += ' dst-zone ' + list(atuple)[5] + '\n'
            if ',' in list(atuple)[6]:#源地址有多个时。
                srcaddr_list = (list(atuple)[6]).split(',')
                for srcaddr_x in srcaddr_list:
                    policy_rule += ' src-addr ' + srcaddr_x + '\n'
            else:
                policy_rule += ' src-addr ' + list(atuple)[6] + '\n'

            ####目的地址，
            if ',' in list(atuple)[7]:#目的地址有多个时。
                dstaddr_list = (list(atuple)[7]).split(',')
                for dstaddr_x in dstaddr_list:
                    policy_rule += ' dst-addr ' + dstaddr_x + '\n'
                    pubip_list_t = find_pubip(dstaddr_x)
                    if pubip_list_t:
                        for pubip in pubip_list_t:
                            policy_rule += ' dst-ip ' + pubip + '/32\n'
            else:#目的地址只有1个时。
                policy_rule += ' dst-addr ' + list(atuple)[7] + '\n'
                pubip_list_t = find_pubip(list(atuple)[7])
                if pubip_list_t:
                    for pubip in pubip_list_t:#pubip有可能也是一个地址簿。

                        policy_rule += ' dst-ip ' + pubip + '/32\n'


            '''
############################
                #找出list(atuple)[7]中有哪些ip。并找出它们对应的DNAT中的公网ip。
                query = 'select ip from address_host where name="%s";' % list(atuple)[7]
                temp2 = fetchallfrom(query)  # temp2=[(1,)]

                query = 'select dst_addr,trans_to from dnat ;'
                temp3 = fetchallfrom(query)  # temp3=[(pubip,privip)]

                if temp2:#如果策略中的地址簿名字在address_host中。
                    dst_prvi_ip_in_orig_policy = ''.join(temp2[0])
                    if temp3:
                        for ip_tuple in temp3:#ip_tuple=(pubip,privip)
                            ip_tuple_list = list(ip_tuple)#ip_tuple_list=[pubip,privip]
                            pubip = ip_tuple_list[0]
                            privip = ip_tuple_list[1]

                            #还需要判断privip是ip地址，还是地址簿。
                            if isIP(privip):
                                pass
                            else:
                                query = 'select ip from address_host where name="%s";' % privip
                                temp5 = fetchallfrom(query)  # temp5=[(1,)]
                                if temp5:
                                    privip = ''.join(temp5[0])
                            if privip in IPy.IP(dst_prvi_ip_in_orig_policy):
                                policy_rule += ' dst-ip ' + pubip + '/32\n'
                    else:
                        pass
                else:#如果策略中的地址簿名字在address_host中找不到，就去address_range中查找。
                    query = 'select ip1,ip2 from address_range where name="%s";' % list(atuple)[7]
                    temp4 = fetchallfrom(query)  # temp4=[(ip1,ip2)]
                    if temp4:
                        dst_prvi_ip1_in_orig_policy = list(temp4[0])[0]
                        dst_prvi_ip2_in_orig_policy = list(temp4[0])[1]
                        #原策略中包含的原目的地址有,从ip1到ip2。
                        dst_priv_ip_list = show_all_range_ip(dst_prvi_ip1_in_orig_policy,dst_prvi_ip2_in_orig_policy)
                        if temp3:
                            for a_dst_priv_ip in dst_priv_ip_list:
                                for ip_tuple in temp3:  # ip_tuple=(pubip,privip)
                                    ip_tuple_list = list(ip_tuple)  # ip_tuple_list=[pubip,privip]
                                    pubip = ip_tuple_list[0]
                                    privip = ip_tuple_list[1]
                                    # 还需要判断privip是ip地址，还是地址簿。
                                    if isIP(privip):
                                        pass
                                    else:
                                        query = 'select ip from address_host where name="%s";' % privip
                                        temp5 = fetchallfrom(query)  # temp5=[(1,)]
                                        if temp5:
                                            privip = ''.join(temp5[0])
                                    if privip in IPy.IP(a_dst_priv_ip):
                                        policy_rule += ' dst-ip ' + pubip + '/32\n'
                    else:
                          pass

#######################################
            '''

            if ',' in list(atuple)[8]:#服务有多个时。
                service_list = (list(atuple)[8]).split(',')
                for service_x in service_list:
                    policy_rule += ' service ' + service_x + '\n'
            else:
                policy_rule += ' service ' + list(atuple)[8] + '\n'

            policy_rule += 'exit\n'

    return policy_rule

def topsec_build_dnat_fromdb():
    dnatrule = 'nat\n'

    query = 'select * from dnat ;'
    temp1 = fetchallfrom(query)  # temp1=[()]
    if temp1:
        for atuple in temp1:  # atuple=(id,ruleid,inif,src_addr,dst_addr,service,trans_to,status)
            if list(atuple)[2]:#如果有入接口项，
                dnatrule += 'dnatrule id ' + list(atuple)[1] + \
                            ' ingress-interface ' + list(atuple)[2] + \
                            ' from ' + list(atuple)[3] + \
                            ' to ' + list(atuple)[4] + \
                            ' service ' + list(atuple)[5] + \
                            ' trans-to ' + list(atuple)[6] + \
                            ' ' + list(atuple)[7] + '\n'
            else:
                dnatrule += 'dnatrule id ' + list(atuple)[1] + \
                            ' from ' + list(atuple)[2] + \
                            ' to ' + list(atuple)[3] + \
                            ' service ' + list(atuple)[4] + \
                            ' trans-to ' + list(atuple)[5] + \
                            ' ' + list(atuple)[6] + '\n'

    dnatrule += 'exit\n'
    return dnatrule

def topsec_build_snat_fromdb():
    snatrule = 'nat\n'

    query = 'select * from snat ;'
    temp1 = fetchallfrom(query)  # temp1=[()]
    if temp1:
        for atuple in temp1:  # atuple=(id,ruleid,src_addr,dst_addr,service,eif,trans_to,status)
            if list(atuple)[5]:#如果有出接口项，
                snatrule += 'snatrule id ' + list(atuple)[1] + \
                            ' from ' + list(atuple)[2] + \
                            ' to ' + list(atuple)[3] + \
                            ' service ' + list(atuple)[4] + \
                            ' eif ' + list(atuple)[5] + \
                            ' trans-to ' + list(atuple)[6] + \
                            ' ' + list(atuple)[7] + '\n'
            else:
                snatrule += 'snatrule id ' + list(atuple)[1] + \
                            ' from ' + list(atuple)[2] + \
                            ' to ' + list(atuple)[3] + \
                            ' service ' + list(atuple)[4] + \
                            ' trans-to ' + list(atuple)[5] + \
                            ' ' + list(atuple)[6] + '\n'

    snatrule += 'exit\n'
    return snatrule


def trans_nat(alist,k):#传入整个配置文件的列表和行号，
    '''
    ID 8425 nat policy add orig_src 'H:数据中心:WGTEST ' orig_dst 'H:广州卓志:数据交换主机11.251 H:广州卓志:FTP ' trans_src test:卓志NAT地址 enable no  vsid 0
    ID 8076 nat policy add orig_src '10.12.0.0 10.13.0.0 10.14.0.0 10.15.0.0 10.16.0.0 ' orig_dst '10.12.6.5 ' trans_src 银监IP trans_dst 19.100.250.129  vsid 0

    :param list:
    :return:
    '''
    words = alist[k].split()
    src_list=[]
    inif = ''
    eif = ''
    dst_list=[]
    service_list=[]
    src_addr = 'any'
    dst_addr = 'any'
    status = ''
    if 'enable' in words:
        status='disable'

    m=words.index('nat')
    ruleid=words[m-1]

    if 'trans-src' in words:
        src_list = findall_inpolicy('orig-src', words)
        if len(src_list) == 1:
            src_addr = src_list[0]
        else:
            pass
        m = words.index('trans-src')
        trans_to = words[m + 1]
        if 'orig-dst' in words:
            dst_list=findall_inpolicy('orig-dst',words)
        if 'dstvlan' in words:
            m = words.index('dstvlan')
            eif = words[m + 1].replace('\'', '')

        query = "insert into snat(ruleid,src_addr,dst_addr,service,eif,trans_to,status) values(?,?,?,?,?,?,?);"
        tmplist2 = [ruleid, src_addr, 'any', 'any',eif,trans_to,status]
        insert2table_new(query, tmplist2)
    elif 'trans-dst' in words:
        dst_list = findall_inpolicy('orig-dst', words)
        if len(dst_list) == 1:
            dst_addr = dst_list[0]
        else:
            pass
        m = words.index('trans-dst')
        trans_to = words[m + 1]
        if 'orig-src' in words:
            src_list = findall_inpolicy('orig-src', words)
            if len(dst_list) == 1:
                src_addr = src_list[0]
        if 'srcvlan' in words:
            m = words.index('srcvlan')
            inif = words[m + 1].replace('\'', '')

        query = "insert into dnat(ruleid,inif,src_addr,dst_addr,service,trans_to,status) values(?,?,?,?,?,?,?);"
        tmplist2 = [ruleid,inif, src_addr, dst_addr, 'any', trans_to, status]
        insert2table_new(query, tmplist2)



############另一版本的话：
    if 'trans_src' in words:
        #ID 8090 nat policy add dstarea '电信1 ' trans_src eth11  vsid 0
        if 'orig_src' in words:
            src_list = findall_inpolicy('orig_src', words)
            if len(src_list) == 1:
                src_addr = src_list[0]
            else:
                pass
        else:
            pass
        m = words.index('trans_src')
        trans_to = words[m + 1]
        if 'orig_dst' in words:
            dst_list = findall_inpolicy('orig_dst', words)
        if 'dstvlan' in words:
            m = words.index('dstvlan')
            eif = words[m + 1].replace('\'', '')
        query = "insert into snat(ruleid,src_addr,dst_addr,service,eif,trans_to,status) values(?,?,?,?,?,?,?);"
        tmplist2 = [ruleid, src_addr, 'any', 'any', eif, trans_to, status]
        insert2table_new(query, tmplist2)
    elif 'trans_dst' in words:
        dst_list = findall_inpolicy('orig_dst', words)
        if len(dst_list) == 1:
            dst_addr = dst_list[0]
        else:
            pass
        m = words.index('trans_dst')
        trans_to = words[m + 1]
        if 'orig_src' in words:
            src_list = findall_inpolicy('orig_src', words)
            if len(dst_list) == 1:
                src_addr = src_list[0]
        if 'srcvlan' in words:
            m = words.index('srcvlan')
            inif = words[m + 1].replace('\'', '')
        query = "insert into dnat(ruleid,inif,src_addr,dst_addr,service,trans_to,status) values(?,?,?,?,?,?,?);"
        tmplist2 = [ruleid, inif, src_addr, dst_addr, 'any', trans_to, status]
        insert2table_new(query, tmplist2)





            # m=words.index('trans_dst')
        # transtoaddr=words[m+1]
        # nattype='dnatrule'
    ###


    # for srcaddr in src_list:
    #     for dstaddr in dst_list:
    #         for service in service_list:
    #             output +=nattype+' id '+ruleid+' from '+srcaddr+' to '+dstaddr+ \
    #             ' service '+service+' trans-to '+transtoaddr+' '+'\n'
    return k

def istopsec(fileuri):
    temp=''

    srcfile = openfile(fileuri)  # 打开原配置
    filepath = os.path.split(fileuri)[0]
    origfilename = os.path.split(fileuri)[1]

    qurey = "CREATE TABLE IF NOT EXISTS address_host(id integer primary key autoincrement, \
    name TEXT, \
    type TEXT, \
    ip TEXT);"
    creat_table(qurey)


    qurey = "CREATE TABLE IF NOT EXISTS address_range(id integer primary key autoincrement, \
    name TEXT, \
    type TEXT, \
    ip1 TEXT, \
    ip2 TEXT);"
    creat_table(qurey)

    qurey = "CREATE TABLE IF NOT EXISTS dnat(id integer primary key autoincrement, \
    ruleid TEXT, \
    inif TEXT, \
    src_addr TEXT, \
    dst_addr TEXT, \
    service TEXT, \
    trans_to TEXT, \
    status TEXT);"
    creat_table(qurey)

    qurey = "CREATE TABLE IF NOT EXISTS snat(id integer primary key autoincrement, \
                        ruleid TEXT, \
                        src_addr TEXT, \
                        dst_addr TEXT, \
                        service TEXT, \
                        eif TEXT, \
                        trans_to TEXT, \
                        status TEXT);"
    creat_table(qurey)

    qurey = "CREATE TABLE IF NOT EXISTS policy(id integer primary key autoincrement, \
                            ruleid TEXT, \
                            status TEXT, \
                            action TEXT, \
                            src_zone TEXT, \
                            dst_zone TEXT, \
                            src_addr TEXT, \
                            dst_addr TEXT, \
                            service TEXT);"
    creat_table(qurey)

    current_row=0
    while(current_row<len(srcfile)):
        words = srcfile[current_row].split()
        if 'define' in words and 'add' in words:
            if 'host' in words  and 'ipaddr' in words:
                temp+=transaddr_host(words)
            if 'subnet' in words  and 'ipaddr' in words:
                temp+=transaddr_subnet(words)
            if 'range' in words and 'ip1' in words:
                temp += transaddr_range(words)
            if 'group_address' in words:
                temp += transaddr_group(words)
            if 'service' in words:
                temp += transservice(words)
            # if 'group_service' in words:
            #     # try:
            #     temp += transservice(words)
            #     # except:
            #     #     print(words)
        elif 'firewall policy add action' in srcfile[current_row]:
            current_row = transpolicy(srcfile,current_row)
        elif 'nat policy add' in srcfile[current_row]:
            current_row = trans_nat(srcfile,current_row)
        current_row+=1

    temptime = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    newfileuri = fileuri + '_new_config_' + temptime + '.txt'  # 新文件为源文件在同一个文件夹下

    temp += topsec_build_snat_fromdb()
    temp += topsec_build_dnat_fromdb()
    temp += topsec_build_policy_fromdb()

    writefile(newfileuri,temp)

    done_label='转换完成!'
    return done_label

