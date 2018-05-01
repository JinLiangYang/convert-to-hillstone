#coding:utf-8
from en_mouth_to_num import *
import time
from opensrcfile import *
import os
from creatdb import *
from convert_asa import asa_exchangemask


def neusoft_snat(alist,j):
#policy snat ShengCaiZhenGWK iplist 10.48.0.0-10.51.255.255 iplist 210.99.1.34 napt enable
#policy snat GuangYuanSheBao iplist 10.50.194.21 iplist 192.168.204.6 napt enable
#policy snat RenHangGongJiaoICKa netmask 10.52.0.0 255.252.0.0 iplist 9.80.41.56 napt enable
    words = alist[j].split()
    snat_name = words[2]
    srcaddrname = 'snat_' + snat_name + '_srcip'
    dstaddrname = 'snat_' + snat_name + '_dstip'
    type = ''
    ip1 = ''
    ip2 = ''
    if words[3]=='iplist':#源地址，
        ip1=words[4]    #srcip
        if '-' in ip1:
            type = 'range'
            ip1_list =ip1.split('-')
            ip1 = ip1_list[0]
            ip2 = ip1_list[1]
        else:
            type = 'ip'
            ip1 += '/32'
    elif words[3] == 'netmask':
        type = 'ip'
        ip1 = words[4] + '/' + asa_exchangemask(words[5])
    query = "insert into addrbok_in_snat(addrname,type,ip1,ip2) values(?,?,?,?);"
    tmplist = [srcaddrname, type, ip1, ip2]
    insert2table_new(query, tmplist)
#####################################################
#下面是目的地址
    if 'napt' in words:
        mode = 'dynamicport'
        m=words.index('napt')
        trans_to_ip = words[m-1]+'/32'
    status = ''
    if 'disable' in words:
        status = 'disable'
    j += 1
    while (j < len(alist)):
        words = alist[j].split()  # 第二行，定义内容部分
        if snat_name not in words:
            break
        if 'output-interface' in words:
            m = words.index('output-interface')
            eif = words[m+1]
            service = 'any'

        if 'dip' in words:#目的地址，
            #policy snat RenHangGongJiaoICKa matching dip netmask 9.80.40.114 255.255.255.255
            if 'netmask' in words:
                m = words.index('netmask')
                type = 'ip'
                dip = words[m+1] + '/' + asa_exchangemask(words[m+2])
            else:
                m = words.index('dip')
                type = 'ip'
                dip = words[m + 1]+'/32'
            query = "insert into addrbok_in_snat(addrname,type,ip1) values(?,?,?);"
            tmplist = [dstaddrname, type, dip]
            insert2table_new(query, tmplist)
        if 'append' in words and 'before' in words:#源地址
            if 'ip' in words:
                m = words.index('ip')
                if (m+2) == len(words):#policy snat GuangYuanSheBao append before ip 10.50.192.136
                    type = 'ip'
                    ip1 = words[m+1] + '/32'
                    query = "insert into addrbok_in_snat(addrname,type,ip1) values(?,?,?);"
                    tmplist = [srcaddrname, type, ip1]
                    insert2table_new(query, tmplist)
                else:#ip后面跟的是2个元素，表示范围。
            #policy snat ShiCaiZhen append before ip 10.48.0.0 10.51.255.255
                    type = 'range'
                    ip1 = words[m+1]
                    ip2 = words[m+2]
                    query = "insert into addrbok_in_snat(addrname,type,ip1,ip2) values(?,?,?,?);"
                    tmplist = [srcaddrname, type, ip1,ip2]
                    insert2table_new(query, tmplist)
            elif 'netmask' in words:
                #policy snat ShengCaiZheng append before netmask 10.48.0.0 255.252.0.0
                m = words.index('netmask')
                type = 'ip'
                ip1 = words[m+1]
                ip2 = words[m + 2]
                query = "insert into addrbok_in_snat(addrname,type,ip1,ip2) values(?,?,?,?);"
                tmplist = [srcaddrname, type, ip1, ip2]
                insert2table_new(query, tmplist)
        j += 1

    query = "insert into snat(srcaddr,dstaddr,service,eif,trans_to,mode,status) values(?,?,?,?,?,?,?);"
    tmplist = [srcaddrname, dstaddrname, service, eif, trans_to_ip, mode,status]
    insert2table_new(query, tmplist)
    j -= 1
    return j



def neusoft_dnat(alist,j):
    dnat = ''
    words= alist[j].split()
    m= words.index('dnat')
    descrip = words[m+1]
    if 'tcp' in words:
        n = words.index('tcp')
    elif 'udp' in words:
        n = words.index('udp')
    proto = words[n]
    pubip = words[n-1]
    pubport = words[n+1]
    privip = words[n+2]
    privport = words[n+3]
    servname = proto + '-' + pubport

    query = "insert into service(servname,proto,dst_port,dstport1) values(?,?,?,?);"
    tmplist = [servname, proto, 'dst-port', pubport]
    insert2table_new(query, tmplist)

    status = words[n+4]
    if status == 'enable':
        status =''
    dnat = 'dnatrule from any to '+pubip+'/32'+ \
           ' service '+servname+ \
           ' trans-to '+privip+'/32 '+privport+' '+status+' description '+descrip+'\n'

    return dnat



def neusoft_bnat(alist,j):
    bnat = ''
    words= alist[j].split()
    m= words.index('mip')
    descrip = words[m+1]
    pubip = words[m+3]
    privip = words[m+2]
    status = words[m+4]
    if status == 'disable':
        return bnat
    bnat = 'bnatrule virtual ip '+pubip+'/32'+ \
           ' real ip '+privip+'/32 description '+descrip+'\n'
    return bnat




def neusoft_policy(alist,j):
    policy = ''
    words = alist[j].split()
    try:
        n = words.index('permit')
        status = words[n + 1]
    except:
        print(j)
    ruleid = words[n+2]

    m = words.index('access')
    descrip = words[m + 1]
    action = 'permit'
    service = 'any'
    srczone = words[m+2]
    dstzone = words[m + 4]
###########################################
    #源ip
    srcip = words[m+3]
    #policy access POI_GJJ1 OUT 172.16.51.134,172.16.51.34-172.16.51.36,172.16.51.63 IN 10.232.51.251 any permit enable 352
    if ',' in srcip:
        srciplist = srcip.split(',')
        for asrcip in srciplist:
            if '-' in asrcip:
                asrciplist = asrcip.split('-')
                query = "insert into addrbok(addrname,type,ip1,ip2) values(?,?,?,?);"
                tmplist = [asrcip, 'range', asrciplist[0], asrciplist[1]]
                insert2table_new(query, tmplist)
                query = "insert into policy(ruleid,src_addr) values(?,?);"
                tmplist = [ruleid, asrcip]
                insert2table_new(query, tmplist)
            else:
                query = "insert into policy(ruleid,src_ip) values(?,?);"
                tmplist = [ruleid, asrcip + '/32']
                insert2table_new(query, tmplist)
    elif '-' in srcip:
        srciplist = srcip.split('-')
        query = "insert into addrbok(addrname,type,ip1,ip2) values(?,?,?,?);"
        tmplist = [srcip, 'range', srciplist[0], srciplist[1]]
        insert2table_new(query, tmplist)
        query = "insert into policy(ruleid,src_addr) values(?,?);"
        tmplist = [ruleid, srcip]
        insert2table_new(query, tmplist)
    elif srcip != 'any':
        query = "insert into policy(ruleid,src_ip) values(?,?);"
        tmplist = [ruleid, srcip + '/32']
        insert2table_new(query, tmplist)
#####################################
    #目的ip
    dstip = words[m+5]
    #policy access PDO_JiaoGuanJu IN 192.168.193.8 OUT 192.168.1.8,192.168.1.9 any permit enable 29
    if ',' in dstip:
        dstiplist = dstip.split(',')
        for adstip in dstiplist:
            if '-' in adstip:
                adstiplist = adstip.split('-')
                for abdstip in adstiplist:
                    query = "insert into policy(ruleid,dst_ip) values(?,?);"
                    tmplist = [ruleid, abdstip + '/32']
                    insert2table_new(query, tmplist)
            else:
                query = "insert into policy(ruleid,dst_ip) values(?,?);"
                tmplist = [ruleid, adstip + '/32']
                insert2table_new(query, tmplist)
    elif '-' in dstip:
        dstiplist = dstip.split('-')
        for adstip in dstiplist:
            query = "insert into policy(ruleid,dst_ip) values(?,?);"
            tmplist = [ruleid, adstip + '/32']
            insert2table_new(query, tmplist)
    elif dstip != 'any':
        query = "insert into policy(ruleid,dst_ip) values(?,?);"
        tmplist = [ruleid, dstip + '/32']
        insert2table_new(query, tmplist)
#########################################################
    j += 1
    srcip2 =''
    dstip2 = ''
    service2 = ''
    while(j<len(alist)):
        words = alist[j].split()
        if descrip not in words:
            break
        if 'sourceip' in words:
            if 'netmask' in words:
                #policy access POD_HuaRun339 sourceip 192.168.10.10 netmask 255.255.255.255
                m=words.index('sourceip')
                try:
                    srcip2 = words[m+1] + '/' + asa_exchangemask(words[m+3])
                    query = "insert into policy(ruleid,src_ip) values(?,?);"
                    tmplist = [ruleid, srcip2]
                    insert2table_new(query, tmplist)
                except:
                    print(j)
            elif 'object' in words:
                m = words.index('object')
                srcip2 = words[m+1]
                query = "insert into policy(ruleid,src_addr) values(?,?);"
                tmplist = [ruleid, srcip2]
                insert2table_new(query, tmplist)
        elif 'desip' in words:
            if 'object' in words:
                m = words.index('object')
                dstip2 = words[m+1]
                query = "insert into policy(ruleid,dst_addr) values(?,?);"
                tmplist = [ruleid, dstip2]
                insert2table_new(query, tmplist)
            elif 'netmask' in words:
                #policy access POD_HuaRun339 desip 192.168.10.10 netmask 255.255.255.255
                m=words.index('netmask')
                try:
                    dstip2 = words[m-1] + '/' + asa_exchangemask(words[m+1])
                    query = "insert into policy(ruleid,dst_ip) values(?,?);"
                    tmplist = [ruleid, dstip2]
                    insert2table_new(query, tmplist)
                except:
                    print(j)
 ##############################################################################
        elif 'protocol' in words and 'protocol-object' in words:
            m = words.index('protocol-object')
            service2 = words[m+1]
            query = "insert into policy(ruleid,service) values(?,?);"
            tmplist = [ruleid, service2]
            insert2table_new(query, tmplist)
        elif 'protocol tcp' in alist[j]:
            m = words.index('tcp')
            dstport = words[m+2]
            if '-' in dstport:
                dstportlist = dstport.split('-')
                if dstportlist[0] == '1' and dstportlist[1] == '65535':
                    pass
                else:
                    service2 = 'tcp-' + dstportlist[0] +'-'+dstportlist[1]
                    query = "insert into service(servname,proto,dst_port,dstport1,dstport2) values(?,?,?,?,?);"
                    tmplist = ['tcp-'+ dstportlist[0] +'-'+dstportlist[1], 'tcp', 'dst-port', dstportlist[0],dstportlist[1]]
                    insert2table_new(query, tmplist)
                    query = "insert into policy(ruleid,service) values(?,?);"
                    tmplist = [ruleid, service2]
                    insert2table_new(query, tmplist)
            else:
                service2 = 'tcp-' + dstport
                query = "insert into service(servname,proto,dst_port,dstport1) values(?,?,?,?);"
                servname ='tcp-'+dstport
                tmplist = [servname, 'tcp', 'dst-port',dstport]
                insert2table_new(query, tmplist)
                query = "insert into policy(ruleid,service) values(?,?);"
                tmplist = [ruleid, service2]
                insert2table_new(query, tmplist)
        elif 'protocol' in words:
            pass
#####################################################################################
        elif 'log on' in alist[j]:
            query = "insert into policy(ruleid,log) values(?,?);"
            tmplist = [ruleid, 'log session-start']
            insert2table_new(query, tmplist)
            tmplist = [ruleid, 'log session-end']
            insert2table_new(query, tmplist)
        j += 1

    if srcip == 'any' and srcip2 =='':
        srcip2 = 'any'
        query = "insert into policy(ruleid,src_addr) values(?,?);"
        tmplist = [ruleid, srcip2]
        insert2table_new(query, tmplist)

    if dstip == 'any' and dstip2 =='':
        query = "insert into policy(ruleid,dst_addr) values(?,?);"
        tmplist = [ruleid, dstip]
        insert2table_new(query, tmplist)

    if service2=='':
        query = "insert into policy(ruleid,service) values(?,?);"
        tmplist = [ruleid, service]
        insert2table_new(query, tmplist)
##############################################################################################################

    query = "insert into policy(ruleid,status,action,src_zone,dst_zone,descrip) values(?,?,?,?,?,?);"
    tmplist = [ruleid,status,action,srczone,dstzone,descrip]
    insert2table_new(query, tmplist)

    j -= 1
    return j


def neusoft_build_policy_fromdb():
    policy = ''
    #从policy表中取出所有不重复的ruleid，
    query = 'select distinct ruleid from policy;'
    temp = fetchallfrom(query)
    if temp:
        for atuple in temp:#atuple是元组，是一个ruleid，
            ruleid = list(atuple)[0]
            policy += 'rule id '+ruleid+'\n'
            query = 'select distinct status from policy where ruleid="%s";' % ruleid
            temp1 = fetchallfrom(query)
            if temp1:
                for atuple in temp1:
                    atuplelist = list(atuple)
                    status = atuplelist[0]
                    if status and status == 'disable':
                        policy += ' '+status +'\n'

            query = 'select distinct action from policy where ruleid="%s";' % ruleid
            temp1 = fetchallfrom(query)
            if temp1:
                for atuple in temp1:
                    atuplelist = list(atuple)
                    action = atuplelist[0]
                    if action:
                        policy += ' action '+action + '\n'

            query = 'select distinct src_zone from policy where ruleid="%s";' % ruleid
            temp1 = fetchallfrom(query)
            if temp1:
                for atuple in temp1:
                    atuplelist = list(atuple)
                    srczone = atuplelist[0]
                    if srczone:
                        policy += ' src-zone ' + srczone + '\n'

            query = 'select distinct dst_zone from policy where ruleid="%s";' % ruleid
            temp1 = fetchallfrom(query)
            if temp1:
                for atuple in temp1:
                    atuplelist = list(atuple)
                    dstzone = atuplelist[0]
                    if dstzone:
                        policy += ' dst-zone ' + dstzone + '\n'

            query = 'select distinct src_ip from policy where ruleid="%s";' % ruleid
            temp1 = fetchallfrom(query)
            if temp1:
                for atuple in temp1:
                    atuplelist = list(atuple)
                    srcip = atuplelist[0]
                    if srcip:
                        try:
                            policy += ' src-ip ' + srcip + '\n'
                        except:
                            print(srcip)

            query = 'select distinct src_addr from policy where ruleid="%s";' % ruleid
            temp1 = fetchallfrom(query)
            if temp1:
                for atuple in temp1:
                    atuplelist = list(atuple)
                    srcaddr = atuplelist[0]
                    if srcaddr:
                        policy += ' src-addr ' + srcaddr + '\n'

            query = 'select distinct dst_ip from policy where ruleid="%s";' % ruleid
            temp1 = fetchallfrom(query)
            if temp1:
                for atuple in temp1:
                    atuplelist = list(atuple)
                    dstip = atuplelist[0]
                    if dstip:
                        policy += ' dst-ip ' + dstip + '\n'

            query = 'select distinct dst_addr from policy where ruleid="%s";' % ruleid
            temp1 = fetchallfrom(query)
            if temp1:
                for atuple in temp1:
                    atuplelist = list(atuple)
                    dstaddr = atuplelist[0]
                    if dstaddr:
                        policy += ' dst-addr ' + dstaddr + '\n'

            query = 'select distinct service from policy where ruleid="%s";' % ruleid
            temp1 = fetchallfrom(query)
            if temp1:
                for atuple in temp1:
                    atuplelist = list(atuple)
                    service = atuplelist[0]
                    if service:
                        policy += ' service ' + service + '\n'

            query = 'select distinct log from policy where ruleid="%s";' % ruleid
            temp1 = fetchallfrom(query)
            if temp1:
                for atuple in temp1:
                    atuplelist = list(atuple)
                    log = atuplelist[0]
                    if log:
                        policy += ' ' + log + '\n'

            query = 'select distinct descrip from policy where ruleid="%s";' % ruleid
            temp1 = fetchallfrom(query)
            if temp1:
                for atuple in temp1:
                    atuplelist = list(atuple)
                    descrip = atuplelist[0]
                    if descrip:
                        policy += ' description ' + descrip + '\n'

            policy += 'exit\n'

    return policy


def neusoft_build_addrbok_fromdb():
    addrbok = ''
    addrbok_ip = ''
    query = 'select distinct addrname from addrbok;'
    temp1 = fetchallfrom(query)  # temp1=[(xxx,),(xxxx,)]，取出所有的addrname，
    if temp1:
        for atuple in temp1:
            addrname = list(atuple)[0]
            query = 'select type,ip1,ip2 from addrbok where addrname="%s" group by type,ip1,ip2;' % addrname
            temp2 = fetchallfrom(query)  # temp2=[(1,),(5,)]
            if temp2:
                for atuple in temp2:
                    alist = list(atuple)
                    if None in alist:
                        alist.remove(None)
                    addrbok_ip += ' '+' '.join(alist) + '\n'
                addrbok += 'address ' + addrname + '\n' + \
                           addrbok_ip + 'exit\n'
                addrbok_ip = ''
    return addrbok


def neusoft_build_service_fromdb():
    service = ''
    service_text = ''
    query = 'select distinct servname from service;'
    temp1 = fetchallfrom(query)  # temp1=[(xxx,),(xxxx,)]，取出所有的servname,
    if temp1:
        for atuple in temp1:
            servname = list(atuple)[0]
            query = 'select proto,dst_port,dstport1,dstport2 from service where servname="%s" group by proto,dst_port,dstport1,dstport2;' % servname
            temp2 = fetchallfrom(query)  # temp2=[(1,),(5,)]
            if temp2:
                for atuple in temp2:
                    alist = list(atuple)
                    if None in alist:
                        alist.remove(None)
                    service_text += ' '+' '.join(alist) + '\n'
                service += 'service ' + servname + '\n' + \
                           service_text + 'exit\n'
                service_text = ''

    return service

def neusoft_fetch_onesnataddrbok_fromdb(addrname):
    addrbok = ''
    addrbok_ip =''
    query = 'select id from addrbok_in_snat where addrname="%s" ;' % addrname
    temp1 = fetchallfrom(query)  # temp1=[(1,),(5,)]，取出所有的id号，
    if temp1:
        for atuple in temp1:
            id = list(atuple)[0]
            query = 'select type,ip1,ip2 from addrbok_in_snat where id="%s" ;' % id
            temp2 = fetchallfrom(query)  # temp2=[(1,),(5,)]
            if temp2:
                for atuple in temp2:
                    alist = list(atuple)
                    if None in alist:
                        alist.remove(None)
                    addrbok_ip += ' '+' '.join(alist)+'\n'
        addrbok += 'address '+addrname+'\n' + \
            addrbok_ip +'exit\n'
    return addrbok


def neusoft_build_snat_fromdb():
    snatrule = ''

    query = 'select seq from sqlite_sequence where name="snat" ;'
    temp1 = fetchallfrom(query)  # temp1=[()]
    sequen = list(temp1[0])[0]
    k=1
    while(k<=sequen):
        #开始取每一项，
        query = 'select srcaddr from snat where id="%s";'  % k
        temp2 = fetchallfrom(query)  # temp2=[()]
        # if temp2:
        #     snatrule += 'snatrule from '+list(temp2[0])[0]

        query = 'select dstaddr from snat where id="%s";' % k
        temp3 = fetchallfrom(query)  # temp3=[()]
        if temp3:
            snatrule = neusoft_fetch_onesnataddrbok_fromdb(list(temp2[0])[0]) + snatrule
            snatrule = neusoft_fetch_onesnataddrbok_fromdb(list(temp3[0])[0]) + snatrule
            snatrule += 'snatrule from ' + list(temp2[0])[0]
            snatrule += ' to '+list(temp3[0])[0]

        query = 'select service from snat where id="%s";' % k
        temp4 = fetchallfrom(query)  # temp4=[()]
        if temp4:
            snatrule += ' service ' + list(temp4[0])[0]

        query = 'select eif from snat where id="%s";' % k
        temp5 = fetchallfrom(query)  # temp5=[()]
        if temp5:
            snatrule += ' eif ' + list(temp5[0])[0]

        query = 'select trans_to from snat where id="%s";' % k
        temp6 = fetchallfrom(query)  # temp6=[()]
        if temp6:
            snatrule += ' trans-to ' + list(temp6[0])[0]

        query = 'select mode from snat where id="%s";' % k
        temp7 = fetchallfrom(query)  # temp7=[()]
        if temp7:
            snatrule += ' mode ' + list(temp7[0])[0]

        query = 'select status from snat where id="%s";' % k
        temp8 = fetchallfrom(query)  # temp8=[()]
        if temp8:
            snatrule += ' ' + list(temp8[0])[0]

        snatrule += '\n'
        k += 1


    return snatrule


def is_neusoft(fileuri):
    srcfile = openfile(fileuri)  # 打开原配置
    filepath = os.path.split(fileuri)[0]
    origfilename = os.path.split(fileuri)[1]

    qurey = "CREATE TABLE IF NOT EXISTS addrbok_in_snat(id integer primary key autoincrement, \
                    addrname TEXT, \
                    type TEXT, \
                    ip1 TEXT, \
                    ip2 TEXT);"
    creat_table(qurey)
    qurey = "CREATE TABLE IF NOT EXISTS addrbok(id integer primary key autoincrement, \
                        addrname TEXT, \
                        type TEXT, \
                        ip1 TEXT, \
                        ip2 TEXT);"
    creat_table(qurey)


    qurey = "CREATE TABLE IF NOT EXISTS snat(id integer primary key autoincrement, \
                        srcaddr TEXT, \
                        dstaddr TEXT, \
                        service TEXT, \
                        eif TEXT, \
                        trans_to TEXT, \
                        mode TEXT, \
                        status TEXT);"
    creat_table(qurey)
    qurey = "CREATE TABLE IF NOT EXISTS service(id integer primary key autoincrement, \
                    servname TEXT, \
                    proto TEXT, \
                    dst_port TEXT, \
                    dstport1 TEXT, \
                    dstport2 TEXT);"
    creat_table(qurey)
    qurey = "CREATE TABLE IF NOT EXISTS policy(id integer primary key autoincrement, \
                        ruleid TEXT, \
                        status TEXT, \
                        action TEXT, \
                        src_zone TEXT, \
                        dst_zone TEXT, \
                        src_ip TEXT, \
                        src_addr TEXT, \
                        dst_ip TEXT, \
                        dst_addr TEXT, \
                        service TEXT, \
                        log TEXT, \
                        descrip TEXT);"
    creat_table(qurey)





    i =0
    policyconfig = ''
    dnat = ''
    bnat = ''
    while (i < len(srcfile)):
        words = srcfile[i].split()
        try:
            if 'policy' in words and 'snat'  in words:
                i = neusoft_snat(srcfile,i)
            if 'policy access ' in srcfile[i]:
                i = neusoft_policy(srcfile, i)
                pass
            if 'policy dnat ' in srcfile[i]:
                dnat += neusoft_dnat(srcfile, i)
            if 'policy mip ' in srcfile[i]:
                bnat += neusoft_bnat(srcfile, i)
            i += 1
        except:
            echo = '请检查第'+str(i+1)+'行'
            return echo

    temptime = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    newfileuri = filepath + '/'+origfilename+'_new_config_' + temptime + '.txt'

    addrbook = ''
    addrbook = neusoft_build_addrbok_fromdb()
    writefile(newfileuri, addrbook)

    service = ''
    service = neusoft_build_service_fromdb()
    writefile(newfileuri, service)

    snat = neusoft_build_snat_fromdb()
    writefile(newfileuri, snat)

    writefile(newfileuri,dnat)
    writefile(newfileuri,bnat)

    policyconfig = neusoft_build_policy_fromdb()
    writefile(newfileuri, policyconfig)
    return 'OK'