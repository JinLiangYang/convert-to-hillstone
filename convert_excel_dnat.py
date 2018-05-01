import xlrd
import time
import os


def isexcel_dnat(fileuri):
    global bk
    tempstr=''
    bk = xlrd.open_workbook(fileuri)
    filepath = os.path.split(fileuri)[0]
    # label.config(text=fname)
    shxrange = range(bk.nsheets)
    # ----------------
    # 获取第一个表
    global sh
    sh = bk.sheets()[0]  # 通过索引顺序获取第一个sheet
    # ----------------
    # 获取行数
    nrows = sh.nrows
    # -----------
    # 获取列数
    ncols = sh.ncols
    print("nrows %d, ncols %d" % (nrows, ncols))
    # ---------------
    # 获取第一行第一列数据

    startline=1#要查找的第一行，
    endline=706 #要查找的最后一行，

    cell_value = ''
    dnatconfig=''

    for i in range(startline, endline):  # 循环这些行，
        cell_value_col1 = sh.cell_value(i,1) #第2列是规则名字，
        cell_value_col2 = sh.cell_value(i,2) #第3列是源地址，
        if cell_value_col2=='any':
            pass
        elif '-' in cell_value_col2:
            pass
        elif cell_value_col2.isalpha():
            pass
        else:
            cell_value_col2=cell_value_col2.replace(' ','')
            cell_value_col2 += '/32'
        cell_value_col3 = sh.cell_value(i,3) #第4列是源地址被转换后的地址，
        cell_value_col4 = sh.cell_value(i,4) #第5列是公开地址，
        if cell_value_col4=='any':
            pass
        else:
            cell_value_col4=cell_value_col4.replace(' ','')
            cell_value_col4 += '/32'
        cell_value_col6 = sh.cell_value(i,6) #第7列是公开的服务，
        cell_value_col5 = sh.cell_value(i,5) #第6列是内网服务器地址，
        if '-' in cell_value_col5 or '_' in cell_value_col5:
            pass
        else:
            cell_value_col5=cell_value_col5.replace(' ','')
            cell_value_col5 += '/32'
        cell_value_col7 = sh.cell_value(i,7) #第8列是内网服务器开放端口，
        cell_value_col9 = sh.cell_value(i,9) #第10列是这条规则是否生效，
        cell_value_col10 = sh.cell_value(i,10) #第11列是这条规则的备注，
        if cell_value_col10 =='':
            description=cell_value_col1
        else:
            description=cell_value_col1+'_'+cell_value_col10
        if type(cell_value_col6) is float:
            cell_value_col6=int(cell_value_col6)
            cell_value_col6=str(cell_value_col6)
        if '\n' in cell_value_col6:
            openservicelist=cell_value_col6.split('\n')
            for openservice in openservicelist:
                dnatconfig += 'dnatrule from ' + cell_value_col2 + ' to ' + \
                              cell_value_col4 + ' service ' + openservice + \
                              ' trans-to ' + cell_value_col5 + \
                              ' log description ' + description + '\n'
        else:
            openservice=cell_value_col6
            dnatconfig += 'dnatrule from ' + cell_value_col2 +' to '+ \
                cell_value_col4 + ' service '+openservice + \
                ' trans-to ' + cell_value_col5 + \
                ' log description ' + description + '\n'
    temptime=time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    filecol3 = open(filepath + '/dnat_config_' + temptime + '.txt', 'w', encoding='utf-8')
    filecol3.writelines(dnatconfig)
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


