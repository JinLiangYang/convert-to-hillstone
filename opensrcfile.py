#-*- coding: utf8 -*-
from tkinter.filedialog import askopenfilename
import os


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
    f=open(fileuri,'r',encoding='utf-8')
    listsrcfile=f.readlines()
    f.close
    return listsrcfile
