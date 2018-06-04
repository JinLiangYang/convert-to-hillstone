#coding:utf-8
#2017-0918，添加netscreen转换，
#2017-0922,添加addnetmask2addrbook转换，
#2017-1225，添加asa转换，ASA版本9.5
#2018-0115,添加东软配置转换，
#2018-0319,修改netscreen转换，

import tkinter
from tkinter import *
from tkinter.filedialog import askopenfilename
from convert_topsec import *
from convert_asa import *
from convert_junos import *
from convert_excel import *
from convert_netscreen import *
from addnetmask2addrbook import *
from opensrcfile import *
from convert_excel_dnat import *
from convert_excel_snat import *
from convert_excel_transaddress import *
from creatdb import *
from convert_neusoft import *



def choose2fir():
    filewin = Toplevel(root)
    label = Label(filewin, text="请先选择原设备和原文件！！！")
    label.pack()

def selectsrcfile_btnClicked():#选择原文件，按钮
    fileuri=selectsrcfile()##返回原文件所在路径+文件名
    # listsfile = os.path.split(fname)#listsfile[0]是原文件的路径，
    # fname = askopenfilename(filetypes=(("All  files", "*.*"), ("HTML files", "*.html;*.htm"), ("All files", "*.*")))
    srcfilepath_label.config(text=fileuri)#让标签显示“原文件所在路径+文件名”
    #下一步将值传递给‘开始转换’按钮，见第40行，

def trans_btnclicked():#转换配置函数

    fileuri=srcfilepath_label.cget('text')

    # 提前创建预定义服务表
    filepath = os.path.split(fileuri)[0]
    creatdb_new2(fileuri)
    creat_predfserv_match_tb()
    creat_preservicetb()

    # if originaldeviceis.cget('text') and srcfilepath_label.cget('text'):
    #     done_label.config(text='正在转换配置，请等待......')
    #     if originaldeviceis.cget("text") == "CISCO":
    #         done_label.config(text=isciscoasa(fileuri))
    #     elif originaldeviceis.cget("text") == "JUNOS":
    #         done_label.config(text=isjunos(fileuri))
    #     elif originaldeviceis.cget("text") == "TOPSEC":
    #         done_label.config(text=istopsec(fileuri))
    #     elif originaldeviceis.cget("text") == "Neusoft":
    #         done_label.config(text=is_neusoft(fileuri))
    #     elif originaldeviceis.cget("text") == "NETSCREEN":
    #         done_label.config(text=isnetscreen(fileuri))
    #     elif originaldeviceis.cget("text") == "F5":
    #         pass
    #     elif originaldeviceis.cget("text") == "HUAWEI":
    #         done_label.config(text=istopsec(fileuri))
    #     elif originaldeviceis.cget("text") == "H3C":
    #         pass
    #     elif originaldeviceis.cget("text") == "ADD/NETMASK":
    #         done_label.config(text=addnetmask2addrbook(fileuri))
    #     elif originaldeviceis.cget("text") == "EXCEL":
    #         isexcel()
    #     elif originaldeviceis.cget("text") == "EXCEL-(DNAT)":
    #         done_label.config(text=isexcel_dnat(fileuri))
    #     elif originaldeviceis.cget("text") == "EXCEL-(SNAT)":
    #         done_label.config(text=isexcel_snat(fileuri))
    #     elif originaldeviceis.cget("text") == "EXCEL-(ADDR)":
    #         done_label.config(text=excel_transaddress(fileuri))
    #     else:
    #         pass
    # else:
    #     choose2fir()




    try:
        if originaldeviceis.cget('text') and srcfilepath_label.cget('text'):
            done_label.config(text='正在转换配置，请等待......')
            if originaldeviceis.cget("text") == "CISCO":
                done_label.config(text=isciscoasa(fileuri))
            elif originaldeviceis.cget("text") == "JUNOS":
                done_label.config(text=isjunos(fileuri))
            elif originaldeviceis.cget("text") == "TOPSEC":
                done_label.config(text=istopsec(fileuri))
            elif originaldeviceis.cget("text") == "Neusoft":
                done_label.config(text=is_neusoft(fileuri))
            elif originaldeviceis.cget("text") == "NETSCREEN":
                done_label.config(text=isnetscreen(fileuri))
            elif originaldeviceis.cget("text") == "F5":
                pass
            elif originaldeviceis.cget("text") == "HUAWEI":
                done_label.config(text=istopsec(fileuri))
            elif originaldeviceis.cget("text") == "H3C":
                pass
            elif originaldeviceis.cget("text") == "ADD/NETMASK":
                done_label.config(text=addnetmask2addrbook(fileuri))
            elif originaldeviceis.cget("text") == "EXCEL":
                isexcel()
            elif originaldeviceis.cget("text") == "EXCEL-(DNAT)":
                done_label.config(text=isexcel_dnat(fileuri))
            elif originaldeviceis.cget("text") == "EXCEL-(SNAT)":
                done_label.config(text=isexcel_snat(fileuri))
            elif originaldeviceis.cget("text") == "EXCEL-(ADDR)":
                done_label.config(text=excel_transaddress(fileuri))
            else:
                pass
        else:
            choose2fir()
    except:
        pass
        # done_label.config(text='程序出错了!!!\n'+ \
        #                   '请将原配置文件发送至 jlyang@hillstonenet.com\n'+ \
        #                        '和114744896@qq.com\n'+ \
        #                        '多谢！')

def test_btnclicked():
    print(originaldeviceis.cget("text"))#获得标签当前的text值。

def option1():
    originaldeviceis.config(text=var.get())

def option2():
    originaldeviceis.config(text=var.get())

def option3():
    originaldeviceis.config(text=var.get())

def option4():
    originaldeviceis.config(text=var.get())

def option5():
    originaldeviceis.config(text=var.get())

def option6():
    originaldeviceis.config(text=var.get())

def option7():
    originaldeviceis.config(text=var.get())

def option8():
    originaldeviceis.config(text=var.get())

def option9():
    originaldeviceis.config(text=var.get())

def option10():
    originaldeviceis.config(text=var.get())

def option11():
    originaldeviceis.config(text=var.get())

def option12():
    originaldeviceis.config(text=var.get())

def option13():
    updatelog = Toplevel(root)
    logtext =''
    logtext +='2018-05-28,更新ASA转换：\n'+ \
        '能正确转换如下配置：\n'+ \
        'access-list outside_acl extended permit object-group dev_eip_odc_svc object-group dev_eip_odc host 22.237.192.49\n'
    label = Label(updatelog, text=logtext)
    label.pack()


root=tkinter.Tk()
root.title("Trans to Hillstone --by jlyang ver_18.05.28")

var = tkinter.StringVar()
menubar = Menu(root)

filemenu = Menu(menubar, tearoff=0)
#menubar.add_cascade(label="原设备类型", menu=filemenu)
filemenu.add_radiobutton(label="CISCO",  command=option1,variable =var)
filemenu.add_radiobutton(label="JUNOS", command=option2,variable =var)
filemenu.add_radiobutton(label="TOPSEC", command=option7,variable =var)
filemenu.add_radiobutton(label="Neusoft", command=option12,variable =var)
filemenu.add_radiobutton(label="NETSCREEN", command=option3,variable =var)
filemenu.add_radiobutton(label="ADD/NETMASK", command=option8,variable =var)
filemenu.add_radiobutton(label="F5", command=option4,variable =var)
filemenu.add_radiobutton(label="HUAWEI", command=option5,variable =var)
filemenu.add_radiobutton(label="EXCEL-(ADX)", command=option6,variable =var)
filemenu.add_radiobutton(label="EXCEL-(DNAT)", command=option9,variable =var)
filemenu.add_radiobutton(label="EXCEL-(SNAT)", command=option10,variable =var)
filemenu.add_radiobutton(label="EXCEL-(ADDR)", command=option11,variable =var)

#filemenu.add_separator()
#filemenu.add_radiobutton(label="Exit", command=root.quit)
menubar.add_cascade(label="原设备类型", menu=filemenu)
menubar.add_command(label="更新日志",command=option13)

# 创建主菜单，每个菜单对应的回调函数都是hello
#menubar.add_radiobutton(label='CISCO',command=hello)
#for k in ['Python', 'PHP', 'CPP', 'C', 'Java', 'JavaScript', 'VBScript']:
#    # 绑定变量与回调函数，指定的变量vLang将这几项划为一组
#    menubar.add_radiobutton(label=k, command=hello, variable=vLang)

#for item in ['Python', 'PHP', 'CPP', 'C', 'Java', 'JavaScript', 'VBScript']:
#    menubar.add_command(label=item, command=hello)
# 将root的menu属性设置为menubar
#
#labelHello = tk.Label(root, text = "Press the button...", height = 5, width = 20, fg = "blue")
label4=tkinter.Label(root,text='注意：要转换的原配置文件请使用UTF-8编码的TXT!   \n' + \
                               '1、点击“原设备类型”，\n'+ \
                               '2、点击“选择原文件”，\n'+ \
                               '3、点击“开始转换”，   \n'+ \
                               '4、在原文件文件夹中查看转换后的配置文件。',bg='yellow')
label4.grid(row=0,column=1,sticky=W)

label=tkinter.Label(root,text='要转换的是：',bg='cyan')
label.grid(row=1,sticky=E)

originaldeviceis=tkinter.Label(root,text='',bg='cyan')#显示选择的原产品，标签
originaldeviceis.grid(row=1,column=1,sticky=W)

srcfilepath_label=tkinter.Label(root,text='')#原文件的路径
srcfilepath_label.grid(row=2,column=1)

selectsrcfile_btn = tkinter.Button(root, text = "选择原文件", command = selectsrcfile_btnClicked,width='11')
selectsrcfile_btn.grid(row=2,column=0)

done_label=tkinter.Label(root,text='还未转换完!',bg='gold')
done_label.grid(row=3,column=1)

trans_btn=tkinter.Button(root,text='开始转换',command=trans_btnclicked,width='11')
trans_btn.grid(row=3,column=0)

#test_btn=tkinter.Button(root,text='test',command=test_btnclicked,width='11')
#test_btn.grid(row=4,column=0)

quit=tkinter.Button(root,text='退出！',command=root.quit,fg='red',width='11')
quit.grid(column=0)

root['menu'] = menubar
root.mainloop()
