#coding:utf-8
import os
import time
from creatdb import *
from opensrcfile import *


def find_ip_frdb(a_string):
    ip_list = []

    query = 'select ip from address_delete where name="%s";' % a_string
    temp = fetchallfrom(query)  # temp=[(1,)]

    if temp:  # 如果这个地址簿名存在于address_delete中。
        ip_tmp_list = list(temp[0])
        ip_list.append(ip_tmp_list[0])

    return ip_list


def modify_v4_address(fileuri):
    srcfile = openfile(fileuri)  # 打开原配置
    filepath = os.path.split(fileuri)[0]
    origfilename = os.path.split(fileuri)[1]

    qurey = "CREATE TABLE IF NOT EXISTS address_delete(id integer primary key autoincrement, \
        name TEXT, \
        ip TEXT);"
    creat_table(qurey)

    delete_address = ''

    current_row = 0
    while (current_row < len(srcfile)):
        k = current_row +1
        j = current_row +2
        if 'address id ' in srcfile[current_row] and 'lan' in srcfile[current_row]:
            '''
            address id 3 "lan-10.10.8.0/24"
                ip 10.10.8.0/24
            exit
            address id 2979 "host-10.151.136.97"
                description "huanghao"
                ip 10.151.136.97/32
            exit
            '''
            if 'description' in srcfile[k]:
                k += 1
                j += 1
            if 'exit' in srcfile[k]:
                current_row = k+1
                continue
            elif 'ip' in srcfile[k] and 'exit' in srcfile[j]:
                delete_address += srcfile[current_row]
                delete_address += srcfile[k]
                delete_address += srcfile[j]
                words = srcfile[current_row].split()
                words_k = srcfile[k].split()
                address_name = words[3].replace('"','')
                address_ip = words_k[1]

                query = "insert into address_delete(name,ip) values(?,?);"
                tmplist = [address_name, address_ip]
                insert2table_new(query, tmplist)

                srcfile[current_row] = ''
                srcfile[k-1]=''
                srcfile[k] = ''
                srcfile[j] = ''

                current_row = j+1
                continue
        elif 'address id ' in srcfile[current_row]:
            '''
            address id 6 "113.108.186.70/32"
                ip 113.108.186.70/32
            exit
            '''
            if 'description' in srcfile[k]:
                # srcfile[k]=''
                k += 1
                j += 1
            if 'exit' in srcfile[k]:
                current_row = k + 1
                continue
            elif r'/32' in srcfile[k] and 'exit' in srcfile[j]:
                delete_address += srcfile[current_row]
                delete_address += srcfile[k]
                delete_address += srcfile[j]

                words = srcfile[current_row].split()
                words_k = srcfile[k].split()
                address_name = words[3].replace('"','')
                address_ip = words_k[1]

                query = "insert into address_delete(name,ip) values(?,?);"
                tmplist = [address_name, address_ip]
                insert2table_new(query, tmplist)

                srcfile[current_row] = ''
                srcfile[k-1] = ''
                srcfile[k] = ''
                srcfile[j] = ''

                current_row = j + 1
                continue
            else:#替换地址组中的成员为ip。
                '''
                address id 2874 "_plc489_saddr_"
                  ip 10.140.0.0/16
                  ip 10.142.130.0/24
                  ip 10.148.44.0/23
                  ip 10.151.83.0/24
                  ip 10.151.88.0/24
                  ip 10.151.92.0/24
                  member "lan-10.154.154.0/24"
                  ip 10.154.161.0/24
                  ip 10.154.165.0/24
                exit
                '''
                while 1:
                    words = srcfile[k].split()
                    if 'exit' in words:
                        # current_row = k +1
                        break
                    elif 'member' in words:
                        member = words[1].replace('"','')
                        temp_ip_list = find_ip_frdb(member)
                        if (len(temp_ip_list) > 0):
                            srcfile[k] = '  ip ' + temp_ip_list[0] + '\n'
                    k += 1

                current_row = k + 1
                continue

        # '''

        elif 'natrule id ' in srcfile[current_row]  and 'trans-to' in srcfile[current_row]:
            words = srcfile[current_row].split()
            m = words.index('from')
            srcaddr = words[m+1].replace('"','')
            dstaddr = words[m+3].replace('"','')

            n = words.index('trans-to')
            if 'address-book' in srcfile[current_row]:
                trans_to = words[n+2].replace('"','')
            else:
                trans_to = words[n+1].replace('"','')

            if srcaddr == 'Any':
                pass
            else:
                temp_ip_list = find_ip_frdb(srcaddr)
                if (len(temp_ip_list)>0):
                    srcfile[current_row] = srcfile[current_row].replace(srcaddr,temp_ip_list[0])
                    srcfile[current_row] = srcfile[current_row].replace('"','')

            if dstaddr == 'Any':
                pass
            else:
                temp_ip_list = find_ip_frdb(dstaddr)
                if (len(temp_ip_list) > 0):
                    srcfile[current_row] = srcfile[current_row].replace(dstaddr, temp_ip_list[0])
                    srcfile[current_row] = srcfile[current_row].replace('"', '')

            temp_ip_list = find_ip_frdb(trans_to)
            if (len(temp_ip_list) > 0):
                srcfile[current_row] = srcfile[current_row].replace(trans_to, temp_ip_list[0])
                srcfile[current_row] = srcfile[current_row].replace('"', '')
        # '''
        elif 'policy-global' in srcfile[current_row]:
            while 1:
                current_row += 1
                words = srcfile[current_row].split()

                if 'src-addr ' in srcfile[current_row]:
                    m = words.index('src-addr')
                    srcaddr = words[m+1].replace('"','')
                    if srcaddr == 'Any':
                        pass
                    else:
                        temp_ip_list = find_ip_frdb(srcaddr)
                        if (len(temp_ip_list) > 0):
                            srcfile[current_row] = '  src-ip ' + temp_ip_list[0] + '\n'
                elif 'dst-addr ' in srcfile[current_row]:
                    m = words.index('dst-addr')
                    dstaddr = words[m + 1].replace('"', '')
                    if dstaddr == 'Any':
                        pass
                    else:
                        temp_ip_list = find_ip_frdb(dstaddr)
                        if (len(temp_ip_list) > 0):
                            srcfile[current_row] = '  dst-ip ' + temp_ip_list[0] + '\n'
                elif 'tcp-syn-check' in srcfile[current_row]:
                    break

        current_row += 1


    current_row = 0
    while (current_row < len(srcfile)):
        k = current_row +1
        j = current_row +2
        if 'address id ' in srcfile[current_row] and 'lan' in srcfile[current_row]:
            if 'description' in srcfile[k]:
                k += 1
                j += 1
            if 'exit' in srcfile[k]:
                current_row = k+1
                continue
            elif 'ip' in srcfile[k] and 'exit' in srcfile[j]:
                current_row = j+1
                continue
        elif 'address id ' in srcfile[current_row]:
            '''
            address id 6 "113.108.186.70/32"
                ip 113.108.186.70/32
            exit
            '''
            if 'description' in srcfile[k]:
                # srcfile[k]=''
                k += 1
                j += 1
            if 'exit' in srcfile[k]:
                current_row = k + 1
                continue
            elif r'/32' in srcfile[k] and 'exit' in srcfile[j]:
                current_row = j + 1
                continue
            else:#替换地址组中的成员为ip。
                '''
                address id 2874 "_plc489_saddr_"
                  ip 10.140.0.0/16
                  ip 10.142.130.0/24
                  ip 10.148.44.0/23
                  ip 10.151.83.0/24
                  ip 10.151.88.0/24
                  ip 10.151.92.0/24
                  member "lan-10.154.154.0/24"
                  ip 10.154.161.0/24
                  ip 10.154.165.0/24
                exit
                '''
                while 1:
                    words = srcfile[k].split()
                    if 'exit' in words:
                        # current_row = k +1
                        break
                    elif 'member' in words:
                        member = words[1].replace('"','')
                        temp_ip_list = find_ip_frdb(member)
                        if (len(temp_ip_list) > 0):
                            srcfile[k] = '  ip ' + temp_ip_list[0] + '\n'
                    k += 1

                current_row = k + 1
                continue
        current_row += 1




    temptime = time.strftime('%Y_%m%d_%H%M', time.localtime(time.time()))
    newfileuri = fileuri + '_delete_address_' + temptime + '.txt'  # 新文件为源文件在同一个文件夹下
    writefile(newfileuri,delete_address)

    newfileuri = fileuri + '_new_config_' + temptime + '.txt'  # 新文件为源文件在同一个文件夹下
    srcfile_str = ''.join(srcfile)
    writefile(newfileuri,srcfile_str)


    return 0
