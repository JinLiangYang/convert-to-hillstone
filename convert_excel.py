import xlrd
import time


def isexcel():
    global bk
    tempstr=''
    bk = xlrd.open_workbook(fname)
    label.config(text=fname)
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
