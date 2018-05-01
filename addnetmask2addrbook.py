#coding:utf-8
import os
import time
from creatdb import *
from opensrcfile import *

def exchangemask(string):
    exchange_mask = lambda mask: sum(bin(int(i)).count('1') \
                                     for i in mask.split('.'))
    string1 = exchange_mask(string)
    return string1


def addnetmask2addrbook(filepathname):
    srcfile=openfile(filepathname)
    filepath=os.path.split(filepathname)[0]

    qurey= "CREATE TABLE addrname_addnetmask(id integer primary key autoincrement, \
    addrbookname TEXT,addrbookname_new TEXT);"
    creatdb_new(filepath,qurey)

    newconfig=''

    i=0
    while (i<len(srcfile)):#替换地址簿及组这一部分
        #1、判断是域名的还是ip地址的，判断words[4]即可，
        #set address "Untrust" "10.200.65.12" 10.200.65.12 255.255.255.255 "玄武监控机"
        #set address "Untrust" "api.jpush.cn" api.jpush.cn
        # 2、
        if ('set address ' in srcfile[i]):#这一行是地址簿定义，
            words=srcfile[i].split()
            iporhost=words[4]
            for h in iporhost:
                flaga=0
                if h.isalpha() is True:# 如果包含有字母，则
                    flaga=1
                    break
            addrbook_name=words[3]#需要将名字写入数据库中，名字外面有双引号，
            if flaga==0:#地址簿是ip地址类型的，
                for j in addrbook_name:
                    flag = 0
                    if j.isalpha() is True:  # 如果地址簿的名字中包含有字母或中文，则
                        flag = 1
                        break
                if flag==0:#地址簿的名字中不包含字母或中文
                    if r'/' not in addrbook_name:#如果地址簿的名字中也没有/,则需要加/
                        netmask=words[5]
                        netmask='/' + str(exchangemask(netmask))
                        addrbook_name_new = addrbook_name[:-1]

                        addrbook_name_new += netmask + '"'#新地址名字外面是有双引号的，
                        qurey="insert into addrname_addnetmask(addrbookname,addrbookname_new) values(?,?);"
                        list_tmp=[addrbook_name,addrbook_name_new]
                        insert2table_new(qurey,list_tmp)
                        words[3] = addrbook_name_new
                        srcfile[i]=' '.join(words)
                        newconfig += srcfile[i] + '\n'
                    else:
                        newconfig += srcfile[i]
                else:#地址簿的名字中包含有字母或中文，则
                    #set address "Untrust" "coremail工程" 218.107.63.246 255.255.255.255
                    #还需要将原名字，调整为描述，
                    addrbook_name_new='"'+words[4]
                    netmask = words[5]
                    netmask = '/' + str(exchangemask(netmask))

                    addrbook_name_new += netmask + '"'#新地址名字外面是有双引号的，
                    qurey = "insert into addrname_addnetmask(addrbookname,addrbookname_new) values(?,?);"
                    list_tmp = [addrbook_name, addrbook_name_new]
                    insert2table_new(qurey, list_tmp)
                    words[3] = addrbook_name_new
                    try:
                        descrip=words[6]
                        descrip=descrip[:-1]
                        descrip+='_'+addrbook_name[1:]
                        words[6]=descrip
                    except:
                        words.append(addrbook_name)
                    srcfile[i] = ' '.join(words)
                    newconfig += srcfile[i] + '\n'
            else:#如果是域名类型的地址簿，
                newconfig += srcfile[i]
        elif ('set group address ' in srcfile[i]):
            break
        else:
            newconfig+=srcfile[i]
        i+=1
    #取出所有旧的名字，
    qurey="select addrbookname from addrname_addnetmask;"
    addrbook_name_list=fetchallfrom(qurey)#每个列表成员都是元组类型，

    while(i < len(srcfile)):#替换策略中的这一部分，
        if ('set alarm threshold ' in srcfile[i]):#策略替换完，
            break
        elif ('set group service ' in srcfile[i] or 'set vpn ' in srcfile[i]):
            newconfig += srcfile[i]
            i+=1
            continue
        for b in addrbook_name_list:
            c=list(b)[0]
            flag=0
            if c in srcfile[i]:
                # flag=1
                # break
        # if flag==1:
                words=srcfile[i].split()#将当前行转换为列表，
                m=words.index(c)
                #找出新的名字，
                qurey="select addrbookname_new from addrname_addnetmask where addrbookname='%s';" %c
                addrbook_name_new_list = fetchallfrom(qurey)
                addrbook_name_new=list(addrbook_name_new_list[0])[0]
                words[m]=addrbook_name_new
                srcfile[i]=' '.join(words)+'\n'
        newconfig += srcfile[i]
        # else:
        #     newconfig += srcfile[i]
        i+=1

    while (i < len(srcfile)):#不再查找替换策略后的部分
        newconfig += srcfile[i]
        i+=1

    newfilename = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    # listsfile = os.path.split(fname)  # 将路径和文件名分开
    newfilename = filepath + '/' + newfilename + '.txt'  # 新文件为源文件在同一个文件夹下
    writefile(newfilename,newconfig)


    done_label = '转换完成!'
    return done_label