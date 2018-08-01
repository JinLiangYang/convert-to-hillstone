#coding:utf-8
import os
import time
from creatdb import *
from opensrcfile import *
# 1、读取service的各个元素到数据库表中，表有7个字段
# 2、取：去重取出表中的service name，放入list中，
# 3、遍历list中每个元素，按元素名从表中取出servicename后的所有字段，
# 4、遍历所有字段，转换为hillstone配置格式，
#2、将各个模块的元素分别写入到对应的表中，
# 3、源文件读取完后，分别读取表，然后写入新文件中，



def extractservice(list,x):
    qurey = "CREATE TABLE IF NOT EXISTS service(id integer primary key autoincrement, \
        servicename TEXT,protocoltype    TEXT, \
        srcport1    TEXT, \
        srcport2    TEXT, \
        dstport1    TEXT, \
        dstport2    TEXT);"

    creat_table(qurey)

    words=list[x].split()
    m = words.index('service')  # 获得’‘索引值
    servicename = words[m + 1].replace('"','')  # 获得service名称
    protocoltype=words[m+3] #获得协议类型，tcp/udp/icmp
    n = words.index('src-port')
    strsrcport = words[n + 1]
    tmplist = strsrcport.split('-')
    srcport1 = tmplist[0]
    srcport2 = tmplist[1]
    strdstport = words[n + 3]
    tmplist = strdstport.split('-')
    dstport1 = tmplist[0]
    dstport2 = tmplist[1]
    tuple=(servicename,protocoltype,srcport1,srcport2,dstport1,dstport2)
    insert2table_service(tuple)
    return x

def extract_vip(list,x):
    qurey = "CREATE TABLE IF NOT EXISTS vip(id integer primary key autoincrement, \
    ingressif   TEXT, \
    publicip TEXT, \
    publicport    TEXT, \
    priviteport    TEXT, \
    priviteip    TEXT);"


    creat_table(qurey)

    words = list[x].split()
    m=words.index('vip')
    ingressif=words[m-1]#入接口
    publicip=words[m+1]
    if '+' in words:
        m+=1
    publicport=words[m+2]#没有引号
    priviteport=words[m+3]#有引号
    priviteport = priviteport.strip('"')
    priviteip=words[m+4]
    qurey="insert into vip(ingressif,publicip,publicport,priviteport,priviteip) values(?,?,?,?,?);"
    tmplist=[ingressif,publicip,publicport,priviteport,priviteip]
    insert2table_new(qurey,tmplist)
    return x


def extract_policynat(alist,k):
    words = alist[k].split()  # 当前行，在words列表中。

    return k


def fetch_vip():
    #
    config = ''
    query="select * from vip;"
    viplist=fetchallfrom(query)#每个元素都是元组，
    for item in viplist:#item是元组，
        itemls=list(item)#将元组转换为列表，
        ingressif=itemls[1]#入接口，
        publicip=itemls[2]#公网地址，
        publicport=itemls[3]#开放的公网端口，下一步要判断在自定义中还是在预定义中，还是要再创建一个新的服务，
        #
        query='select servicename from service where dstport1="%s";' % publicport
        serv_name_list=fetchallfrom(query)
        if serv_name_list:
            for item_serv_name in serv_name_list:
                item_serv_name_list = list(item_serv_name)
                publicport_serv_name=item_serv_name_list[0]
        else:
            publicport_serv_name='需要新建'
        privateport=itemls[4]
        privateip=itemls[5]
        config += 'nat\n dnatrule from any to '+publicip+' service '+publicport_serv_name+' trans-to '+privateip+' port '+privateport+' log\nexit\n'
    return config

def isnetscreen(fileuri):

    srcfile=openfile(fileuri)#打开原配置
    filepath=os.path.split(fileuri)[0]

    # creatdb_new2(filepath)#创建新数据库，
    # creat_preservicetb()
    i = 0
    print(len(srcfile))  # srcfile[len(srcfile)-1]是最后一行
    while (i < len(srcfile)):
        if ('set service ' in srcfile[i] and 'dst-port' in srcfile[i]):#转换服务
            i = extractservice(srcfile,i)
        #转换VIP成DNAT
        elif ('set interface ' in srcfile[i] and ' vip ' in srcfile[i] and 'interface-ip' not in srcfile[i]):#转换VIP
            i = extract_vip(srcfile,i)
        elif ('policy' in words and 'from' in words and 'nat' in words):#转换带nat的安全策略
            #print('759')
            i = extract_policynat(srcfile,i)
        elif ('policy' in words and 'from' in words):#转换安全策略
            i = extract_transpolicy(srcfile,i)
        i = i + 1

    newconfig=''
    newconfig+=fetch_service()#SERVER定义
    newconfig+=fetch_vip()#dnat输出，

    # newfilename = ''
    newfiletime = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    # listsfile = os.path.split(fname)  # 将路径和文件名分开
    newfileuri = filepath + '/' + newfiletime + '.txt'  # 新文件为源文件在同一个文件夹下

    writefile(newfileuri,newconfig)

    # ed = open(newfileuri, 'w',encoding='utf-8')  # 打开转换后的文件
    # ed.writelines(newconfig)
    # # ed.writelines(addrgroupstr)
    # # ed.writelines(output)
    # ed.close()

    done_label = '转换完成!'
    return done_label
