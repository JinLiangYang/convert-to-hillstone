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

def neusoft_policy(alist,j):
    policy = ''
    words = alist[j].split()
    m = words.index('access')
    descrip = words[m + 1]
    action = 'permit'
    srczone = words[m+2]
    srcip = words[m+3]
    #policy access POI_GJJ1 OUT 172.16.51.134,172.16.51.34-172.16.51.36,172.16.51.63 IN 10.232.51.251 any permit enable 352
    if ',' in srcip:
        srciplist = srcip.split(',')

        srcip = '/32\n src-ip '.join(srciplist)

    elif '-' in srcip:
        pass

    dstzone = words[m+4]
    dstip = words[m+5]
    #policy access PDO_JiaoGuanJu IN 192.168.193.8 OUT 192.168.1.8,192.168.1.9 any permit enable 29

    if ',' in dstip:
        dstiplist = dstip.split(',')
        dstip = '/32\n dst-ip '.join(dstiplist)

    service = ' service any\n'
    try:
        n = words.index('permit')
        status = words[n + 1]
    except:
        print(j)
    ruleid = words[n+2]

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
                    srcip2 += ' src-ip ' + words[m+1] + '/' + asa_exchangemask(words[m+3]) + '\n'
                except:
                    print(j)
            elif 'object' in words:
                m = words.index('object')
                srcip2 += ' src-addr '+words[m+1] + '\n'
        elif 'desip' in words:
            if 'object' in words:
                m = words.index('object')
                dstip2 += ' dst-addr '+words[m+1] + '\n'
            elif 'netmask' in words:
                #policy access POD_HuaRun339 desip 192.168.10.10 netmask 255.255.255.255
                m=words.index('netmask')
                try:
                    dstip2 += ' dst-ip ' + words[m-1] + '/' + asa_exchangemask(words[m+1]) + '\n'
                except:
                    print(j)
            pass
        elif 'protocol' in words and 'protocol-object' in words:
            m = words.index('protocol-object')
            service2 += ' service ' + words[m+1] +'\n'
        elif 'protocol tcp' in alist[j]:
            m = words.index('tcp')
            dstport = words[m+2]
            if '-' in dstport:
                dstportlist = dstport.split('-')
                if dstportlist[0] == '1' and dstportlist[1] == '65535':
                    pass
                else:
                    service2 += ' service tcp-' + dstportlist[0] +'-'+dstportlist[1]+ '\n'
                    query = "insert into service(servname,proto,dst_port,dstport1,dstport2) values(?,?,?,?,?);"
                    tmplist = ['tcp-'+ dstportlist[0] +'-'+dstportlist[1], 'tcp', 'dst-port', dstportlist[0],dstportlist[1]]
                    insert2table_new(query, tmplist)
                    pass
            else:
                service2 += ' service tcp-' + dstport + '\n'
                query = "insert into service(servname,proto,dst_port,dstport1) values(?,?,?,?);"
                servname ='tcp-'+dstport
                tmplist = [servname, 'tcp', 'dst-port',dstport]
                insert2table_new(query, tmplist)
                pass
            pass
        elif 'protocol' in words:
            pass
        elif 'log on' in alist[j]:
            dstzone += '\n log session-start\n log session-end'
            # descrip = ' log session-start\n log session-end\n'+descrip
        j += 1


    if srcip == 'any' and srcip2 =='':
        srcip2 = ' src-addr any\n'
    elif srcip=='any':
        pass
    elif srcip2 =='':#srcip不为any,但srcip2为空时，
        #policy access PIO_ZHSer01 IN 187.67.0.20 OUT any any permit enable 3
        # policy access PIO_ZHSer01 protocol tcp 1-65535 1-65535
        # policy access PIO_ZHSer01 permit
        # policy access PIO_ZHSer01 log on
        srcip2 = ' src-ip ' +srcip+'/32\n'

    if dstip == 'any' and dstip2 =='':
        dstip2 = ' dst-addr any\n'
    elif dstip=='any':
        pass
    elif dstip2 =='':#dstip不是any而是ip地址,且dstip2为空时，
        #policy access PIO_ZHSer01 IN 187.67.0.20 OUT any any permit enable 3
        # policy access PIO_ZHSer01 protocol tcp 1-65535 1-65535
        # policy access PIO_ZHSer01 permit
        # policy access PIO_ZHSer01 log on
        dstip2 = ' dst-ip ' +dstip+'/32\n'


    if status == 'disable':
        status =' '+status+ '\n'
    else:
        status = ''
    if service2:
        service = service2
    policy += 'rule id '+ruleid +'\n'+ \
        status + \
        ' action ' + action + '\n'+ \
        ' src-zone ' + srczone + '\n'+ \
        ' dst-zone ' + dstzone + '\n'+ \
         srcip2 + \
         dstip2 + \
         service + \
        ' description ' + descrip + '\n'+ \
        'exit\n'




    j -= 1
    return policy,j


def neusoft_build_addrbok_fromdb():
    addrbok = ''


    return addrbok


def neusoft_fetch_onesnataddrbok_fromdb(addrname):
    addrbok = ''
    addrbok_ip =''
    query = 'select id from addrbok_in_snat where addrname="%s" ;' % addrname
    temp1 = fetchallfrom(query)  # temp1=[(1,),(5,)]
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
                    addrbok_ip += ' '.join(alist)+'\n'
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
                        src-zone TEXT, \
                        dst-zone TEXT, \
                        src-ip TEXT, \
                        src-addr TEXT, \
                        dst-ip TEXT, \
                        dst-addr TEXT, \
                        service TEXT, \
                        log TEXT, \
                        descrip TEXT);"
    creat_table(qurey)





    i =0
    policyconfig = ''
    while (i < len(srcfile)):
        words = srcfile[i].split()
        if 'policy' in words and 'snat'  in words:
            i = neusoft_snat(srcfile,i)
        if 'policy access ' in srcfile[i]:
            policytemp,i = neusoft_policy(srcfile, i)
            policyconfig += policytemp
            pass
        i += 1

    temptime = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    newfileuri = filepath + '/'+origfilename+'_new_config_' + temptime + '.txt'

    snat = neusoft_build_snat_fromdb()
    writefile(newfileuri, snat)
    writefile(newfileuri, policyconfig)
    return 'OK'