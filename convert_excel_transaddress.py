import xlrd
import time
import os
import IPy
from trans import *


def exchangemask(mask_b):
    exchange_mask = lambda mask: sum(bin(int(i)).count('1') \
                                     for i in mask.split('.'))
    mask_d = str(exchange_mask(mask_b))
    return mask_d



def excel_transaddress(fileuri):
    global bk
    tempstr=''
    bk = xlrd.open_workbook(fileuri)
    filepath = os.path.split(fileuri)[0]
    # label.config(text=fname)
    shxrange = range(bk.nsheets)
    # ----------------
    # 获取第一个表
    sh = bk.sheets()[3]  # 通过索引顺序获取第4个sheet
    # ----------------
    # 获取行数
    nrows = sh.nrows
    # -----------
    # 获取列数
    ncols = sh.ncols
    # print("nrows %d, ncols %d" % (nrows, ncols))
    # ---------------
    # 获取第一行第一列数据


    startline=1#要查找的第一行，
    endline=nrows #要查找的最后一行，

    cell_value = ''
    addr_config=''
    description=''
    mutisrcip=''
    mutidstip=''

    for i in range(startline, endline):  # 循环这些行，
        addressname = sh.cell_value(i,1) #第2列是地址簿的名字，
        ipaddress = sh.cell_value(i,2) #第3列是具体地址，
        description = sh.cell_value(i,3)#第4列是备注，
        if type(ipaddress) is float:
            ipaddress=int(ipaddress)
            ipaddress=str(ipaddress)
        if type(addressname) is float:
            addressname=int(addressname)
            addressname=str(addressname)
        addr_config += 'address ' + addressname + '\n'
        if '\n' in ipaddress :
            mutiipaddress=ipaddress.split('\n')
        elif ';' in ipaddress:
            mutiipaddress=ipaddress.split(';')
        if  mutiipaddress:#如果列表非空，
            for mutiip in mutiipaddress:
                if '-' in mutiip:
                    ipranglist=mutiip.split('-')
                    addr_config+=' range '+ipranglist[0]+' '+ipranglist[1]+'\n'
                    ipranglist=[]
                else:
                    mutiip=mutiip.replace('/',' ')
                    addr_config+=' ip '+mutiip+'\n'
            addr_config+='exit\n'
            mutiipaddress = []
        else:
            if '-' in ipaddress:
                ipranglist = ipaddress.split('-')
                addr_config += ' range ' + ipranglist[0] + ' ' + ipranglist[1] + '\n'
                ipranglist=[]
            else:
                ipaddress = ipaddress.replace('/', ' ')
                addr_config+=' ip '+ipaddress+'\n'
            addr_config += 'exit\n'

    temptime = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    filecol3 = open(filepath + '/addressconfig' + temptime + '.txt', 'w')
    filecol3.writelines(addr_config)
    filecol3.close()
    #以上，将4、5列合并，并输出到文件中
    #exit()
    done_label = '转换完成!'
    return done_label
'''
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
    '''


