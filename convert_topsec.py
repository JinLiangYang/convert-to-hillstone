from opensrcfile import *
import time

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
    output = \
    'address ' + addrname + '\n' \
    ' ip ' + net + ' '+ mask + '\n' \
    'exit\n'
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


def transpolicy(list):
    '''
    ID 8594 firewall policy add action accept dstarea 'SSN区交换机(202.105.50.157) ' src 'H:SSN隔离区:技术中心门户系统 '  vsid 0
    ID 8572 firewall policy add action accept src 'H:电子口岸:运维:远端服务器 H:电子口岸:运维:远端广域网地址 ' dst 'H:SSN隔离区:发展对外MQ数据交互 ' service 'tcp-1404 PING '  vsid 0
    :param list:
    :return:
    '''

    m=list.index('action')
    action=list[m+1]
    ruleid=list[m-4]
    output='rule id ' +ruleid+ '\n'
    if action=='accept':
        action='permit'
        output+=' action '+action+'\n'
    else:
        output += ' action deny\n'
    if 'no' in list:
        output += ' disable\n'
    if 'srcarea' in list:
        m=list.index('srcarea')
        srczone=list[m+1].replace('\'','')
        output +=' src-zone ' + srczone +'\n'
    if 'dstarea' in list:
        m=list.index('dstarea')
        dstzone=list[m+1].replace('\'','')
        output +=' dst-zone ' + dstzone +'\n'
    #开始有多个取值了：
    if 'src' in list:
        srca_list=findall_inpolicy('src',list)
        for srca in srca_list:
            output += ' src-addr ' + srca + '\n'
    else:
        output += ' src-addr any\n'
    if 'dst' in list:
        dsta_list = findall_inpolicy('dst', list)
        for dsta in dsta_list:
            output += ' dst-addr ' + dsta + '\n'
    else:
        output += ' dst-addr any\n'
    if 'service' in list:
        service_list=findall_inpolicy('service',list)
        for serv in service_list:
            output+=' service '+serv+'\n'
    else:
        output += ' service any\n'
    ##识别结束。
    output +='exit\n'
    return output

def trans_nat(list):
    '''
    ID 8425 nat policy add orig_src 'H:数据中心:WGTEST ' orig_dst 'H:广州卓志:数据交换主机11.251 H:广州卓志:FTP ' trans_src test:卓志NAT地址 enable no  vsid 0
    :param list:
    :return:
    '''
    src_list=[]
    dst_list=[]
    service_list=[]
    output=''
    nattype=''
    transtoaddr=''
    m=list.index('nat')
    ruleid=list[m-1]
    if 'orig_src' in list :
        src_list=findall_inpolicy('orig_src',list)
    elif 'srcarea' in list:
        m = list.index('srcarea')
        src_list.append(list[m+1].replace('\'',''))
    ###
    if 'orig_dst' in list:
        dst_list=findall_inpolicy('orig_dst',list)
    elif 'dstarea' in list:
        m = list.index('dstarea')
        dst_list.append(list[m+1].replace('\'',''))
    ###
    if 'orig_service' in list:
        service_list=findall_inpolicy('orig_service',list)
    else:
        service_list.append('any')
    ###
    if 'trans_src' in list:
        m=list.index('trans_src')
        transtoaddr=list[m+1]
        nattype='snatrule'
    elif 'trans_dst' in list:
        m=list.index('trans_dst')
        transtoaddr=list[m+1]
        nattype='dnatrule'
    ###
    if 'enable' in list:
        disable='disable'
    else:
        disable= ''
    for srcaddr in src_list:
        for dstaddr in dst_list:
            for service in service_list:
                output +=nattype+' id '+ruleid+' from '+srcaddr+' to '+dstaddr+ \
                ' service '+service+' trans-to '+transtoaddr+' '+disable+'\n'
    return output

def istopsec(fname):
    temp=''
    listsrcfile=openfile(fname)
    # temp=listsrcfile[0]
    current_row=0
    while(current_row<len(listsrcfile)):
        words = listsrcfile[current_row].split()
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
        elif 'firewall policy add action' in listsrcfile[current_row]:
            temp += transpolicy(words)
        elif 'nat policy add' in listsrcfile[current_row]:
            temp += trans_nat(words)
        current_row+=1
    newfilename = ''
    newfilename = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    newfilename = os.path.split(fname)[0] + '/' + newfilename + '.txt'  # 新文件为源文件在同一个文件夹下
    writefile(newfilename,temp)
    done_label='转换完成!'
    return done_label

