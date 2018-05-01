



def gene_addr(ip):
    #根据地址范围生成地址薄，192.168.131.37-192.168.131.47
    iplist=ip.split('-')
    ipstart=iplist[0]
    ipend=iplist[1]
    ipendlist=ipend.split('.')
    addressname=ipstart+'-'+ipendlist[3]

    return 0

def snatrule(ruleid,srcip,dstip,service,transip,description,afterport=''):
    snatconfig=''
    if afterport=='':
        snatconfig += 'snatrule '+ ' from ' + srcip + ' to ' + \
                      dstip + ' service ' + service + \
                      ' trans-to ' + transip + ' mode dynamicport '+ \
                      ' log description ' + description + '\n'
    else:
        snatconfig += 'snatrule ' + ' from ' + srcip + ' to ' + \
                      dstip + ' service ' + service + \
                      ' trans-to ' + transip + ' port ' + afterport + \
                      ' mode dynamicport '+' log description ' + description + '\n'
    return snatconfig


