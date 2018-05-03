#-*- coding: utf8 -*-
from tkinter.filedialog import askopenfilename
import os
import chardet


#class opensrcfile(object):
def selectsrcfile():
    fileuri= askopenfilename(filetypes=(("All  files", "*.*"), ("HTML files", "*.html;*.htm"), ("All files", "*.*")))
    # listsfile = os.path.split(fname)
    return fileuri #返回原文件所在路径+文件名

def writefile(fileuri,string):
    f=open(fileuri,'a',encoding='utf-8')
    f.writelines(string)
    f.close()

def openfile(fileuri):
#判断文件是什么编码的，gbk,utf-8等，
    f = open(fileuri, 'rb')
    fencoding = chardet.detect(f.read())

    if fencoding['encoding'] == 'ascii':
        fcode = 'gbk'
    else:
        fcode = 'utf-8'
#判断结束。
    f=open(fileuri,'r',encoding=fcode)
    listsrcfile=f.readlines()
    f.close
    return listsrcfile
