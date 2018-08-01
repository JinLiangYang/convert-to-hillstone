import IPy


def show_all_range_ip(ipa,ipb):
    range_allip_list = []

    ipa_list = ipa.split('.')
    ipb_list = ipb.split('.')

    if IPy.IP(ipa) > IPy.IP(ipb):
        return 0
    elif IPy.IP(ipa) == IPy.IP(ipb):
        range_allip_list.append(ipa)
        return range_allip_list
    else:
        range_allip_list.append(ipa)
        ipa1 = int(ipa_list[0])
        ipa2 = int(ipa_list[1])
        ipa3 = int(ipa_list[2])
        ipa4 = int(ipa_list[3])
        i = ipa4
        while(i<256):
            ipa4 += 1
            ipa1 = str(ipa1)
            ipa2 = str(ipa2)
            ipa3 = str(ipa3)
            ipa4 = str(ipa4)
            ipa_temp_list = [ipa1,ipa2,ipa3,ipa4]
            ipa_temp = '.'.join(ipa_temp_list)
            if IPy.IP(ipa_temp) == IPy.IP(ipb):
                range_allip_list.append(ipa_temp)
                k = 1#第四段就查找完。不需要再遍历第3段。
                return range_allip_list
            else:
                range_allip_list.append(ipa_temp)
            ipa4 = int(ipa4)
            i += 1
    # print(range_allip_list)
    return range_allip_list


if __name__ == '__main__':

    ipa='192.168.2.2'
    ipb='192.168.2.255'
    templist=show_all_range_ip(ipa,ipb)
    print(templist)
    pass