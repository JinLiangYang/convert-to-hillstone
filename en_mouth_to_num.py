#coding:utf-8

def en_mouth_to_num(string):
    en_mouth=['January','February','March','April','May','June','July','August','September','October','November','December']
    num_mouth=['01','02','03','04','05','06','07','08','09','10','11','12']
    m = en_mouth.index(string)
    temstring = num_mouth[m]
    return temstring
