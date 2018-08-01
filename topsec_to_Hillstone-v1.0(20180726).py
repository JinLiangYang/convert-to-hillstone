# -*- coding: utf-8 -*- 
###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import threading
import os
import datetime
from class_test import *

###########################################################################
## Class h3ctohillstone
###########################################################################

class h3ctohillstone ( wx.Frame,F_test ):
	
	def __init__( self ,parent,name):
		F_test.__init__(self, name)
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"天融信配置转换_Hillstone_v1.0", pos = wx.DefaultPosition, size = wx.Size( 887,673 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )
		
		tool_gbSizer = wx.GridBagSizer( 0, 0 )
		tool_gbSizer.SetFlexibleDirection( wx.BOTH )
		tool_gbSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.choice_source_file = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"选择需要转换的配置文件", u"*.*", wx.DefaultPosition, wx.Size( 500,-1 ), wx.FLP_DEFAULT_STYLE )
		tool_gbSizer.Add( self.choice_source_file, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 2 ), wx.ALL, 5 )
		
		self.totran = wx.ToggleButton( self, wx.ID_ANY, u"开始转换", wx.DefaultPosition, wx.DefaultSize, 0 )
		tool_gbSizer.Add( self.totran, wx.GBPosition( 1, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

		
		self.get_btn = wx.Button( self, wx.ID_ANY, u"导出配置", wx.DefaultPosition, wx.DefaultSize, 0 )
		tool_gbSizer.Add( self.get_btn, wx.GBPosition( 1, 4 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		self.get_btn.Enable( False )
		
		gbSizer2 = wx.GridBagSizer( 0, 0 )
		gbSizer2.SetFlexibleDirection( wx.BOTH )
		gbSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_textCtrl2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 400,300 ), wx.TE_MULTILINE )
		gbSizer2.Add( self.m_textCtrl2, wx.GBPosition( 2, 3 ), wx.GBSpan( 1, 2 ), wx.ALL, 5 )
		
		self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"转换后配置：", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2.Wrap( -1 )
		gbSizer2.Add( self.m_staticText2, wx.GBPosition( 1, 3 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"源文件信息：", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )
		gbSizer2.Add( self.m_staticText1, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		self.m_textCtrl1 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 400,300 ), wx.TE_MULTILINE )
		self.m_textCtrl1.SetMaxSize( wx.Size( 600,600 ) )
		
		gbSizer2.Add( self.m_textCtrl1, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		
		tool_gbSizer.Add( gbSizer2, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 4 ), wx.EXPAND, 5 )
		
		self.m_textCtrl3 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 830,150 ), wx.TE_MULTILINE )
		tool_gbSizer.Add( self.m_textCtrl3, wx.GBPosition( 4, 1 ), wx.GBSpan( 1, 4 ), wx.ALL, 5 )
		
		self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"信息输出：", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		tool_gbSizer.Add( self.m_staticText3, wx.GBPosition( 3, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )
		
		
		self.SetSizer( tool_gbSizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.choice_source_file.Bind( wx.EVT_FILEPICKER_CHANGED, self.getsrcfile )
		self.totran.Bind( wx.EVT_TOGGLEBUTTON, self.tran )
		self.get_btn.Bind( wx.EVT_BUTTON, self.get_newconfig )
	
	def __del__( self ):
		pass
	
	filelines=[]
	# Virtual event handlers, overide them in your derived class

	def tran(self,event):
		self.m_textCtrl2.AppendText(F_test.name)
		pass


# t=threading.Thread(target=trantohs, args=(self.m_textCtrl1.GetValue(),))
# t.start()
# self.m_textCtrl2.Clear()

# self.totran.Enable( False )
	

	def getsrcfile( self, event ):
		self.get_file()
		self.totran.Enable()
	
	
	def get_newconfig( self, event ):
		getconfig()
		
	
            
	def get_file(self):
		filepath=self.choice_source_file.GetPath()
		file=open(filepath,'r')
		bfile=file.read()
		global filelines
		self.filelines=bfile.split('\n')
		#print(self.filelines)
		self.m_textCtrl1.Clear()
		self.m_textCtrl1.AppendText(bfile)
		self.m_textCtrl3.Clear()
		self.m_textCtrl3.AppendText('待转换配置文件总行数：'+str(len(bfile.split('\n')))+'\n')




def trantohs(gs):
        err=open('nat_err.log','wb')
        sfile=gs.split('\n')
        i=0
        addrs_host_num=0
        addrs_subnet_num=0
        addrs_range_num=0
        service_num=0
        service_group_num=0
        address_group_num=0
        policy_num=0
        route_num=0
        nat_num=0
        dstnat_num=0
        real_dstip={}
        while i<len(sfile):
            line=sfile[i].split()
            #转换地址
            if 'define host add name' in sfile[i]:
                i=convert_host_address(sfile,i)
                addrs_host_num+=1
             #转换子网地址
            if 'define subnet add name' in sfile[i]:
                i=convert_subnet_range_address(sfile,i,'subnet')
                addrs_subnet_num+=1
             #转换地址范围
            if 'define range add name' in sfile[i]:
                i=convert_subnet_range_address(sfile,i,'range')
                addrs_range_num+=1
                #转换服务
            if 'define service add name'  in sfile[i]:
                i=convert_service(sfile,i)
                service_num+=1

               #转换服务组 
            if 'define group_service add name'  in sfile[i]:
                i=convert_service_group(sfile,i)
                service_group_num+=1

               #转换地址组 
            if 'define group_address add name'  in sfile[i]:
                i=convert_address_group(sfile,i)
                address_group_num+=1
                 #转换策略
            if 'firewall policy add'  in sfile[i]:
                i=convert_policy(sfile,i,real_dstip,err)
                policy_num+=1
               #转换静态路由
            if 'network route add dst'  in sfile[i]:
                i=convert_route(sfile,i)
                route_num+=1

                
               #转换NAT 
            if 'nat policy '  in sfile[i]:
                i=convert_nat(sfile,i,real_dstip,err)
                nat_num+=1                
            i+=1

            
        frame.m_textCtrl3.AppendText('转换主机地址：'+str(addrs_host_num)+' \n')
        frame.m_textCtrl3.AppendText('转换子网地址：'+str(addrs_subnet_num)+' 个\n')
        frame.m_textCtrl3.AppendText('转换地址范围：'+str(addrs_range_num)+' 个\n')
        frame.m_textCtrl3.AppendText('转换地址组：'+str(address_group_num)+' 个\n')
        frame.m_textCtrl3.AppendText('转换服务簿：'+str(service_num)+' 个\n')
        frame.m_textCtrl3.AppendText('转换服务组：'+str(service_group_num)+' 个\n')
        frame.m_textCtrl3.AppendText('转换策略：'+str(policy_num)+' 个\n')
        frame.m_textCtrl3.AppendText('转换路由：'+str(route_num)+' 个\n')
        frame.m_textCtrl3.AppendText('转换1to1 NAT：'+str(nat_num)+' 个\n')
        frame.m_textCtrl3.AppendText('转换dst NAT：'+str(dstnat_num)+' 个\n')
        frame.totran.Enable()
        frame.get_btn.Enable()
        err.close()


#############天融信转换函数##################
def getpolicy_element(find,line,addrdist={}):
        s=line.index(find)+1
        if find=='service':
                addr=''
        else:
                addr='-addr '
        frame.m_textCtrl2.AppendText(' '+find+addr+line[s][1:]+'\n')
        if find=='dst':
                if line[s][1:] in addrdist:
                        frame.m_textCtrl2.AppendText(' '+find+addr+addrdist[line[s][1:]]+'\n')                
        while s<line.index("'")-1:
                s+=1
                frame.m_textCtrl2.AppendText(' '+find+addr+line[s]+'\n')
                if find=='dst':
                        if line[s][1:] in addrdist:
                                frame.m_textCtrl2.AppendText(' '+find+addr+addrdist[line[s]]+'\n')         

        
#策略转换函数
def convert_policy(filelist,l,distaddr,err):
        try:
                line=filelist[l].split()
                frame.m_textCtrl2.AppendText('rule id '+line[1]+'\n' )
                if line[line.index('action')+1]=='accept':
                        frame.m_textCtrl2.AppendText(' action permit\n' )
                else:
                        frame.m_textCtrl2.AppendText(' action deny\n' )
                getpolicy_element('src',line)
                getpolicy_element('dst',line,distaddr)
                if 'service' not in line:
                        frame.m_textCtrl2.AppendText(' service any\n')
                else:
                        getpolicy_element('service',line)
                frame.m_textCtrl2.AppendText('exit\n')
        except:
                err.write(filelist[l].encode('UTF-8')+b'\n')
        return l
#创建nat地址组
def getaddr(find,line):
        s=line.index(find)+1
        if line[s+1]=="'":
                return line[s][1:]
        else:
                addr='nat_'+line[1]+'_group'
                frame.m_textCtrl2.AppendText('address nat_'+line[1]+'_group\n')
                frame.m_textCtrl2.AppendText(' menber '+line[s][1:]+'\n')
                while s<line.index("'")-1:
                        s+=1
                        frame.m_textCtrl2.AppendText(' member '+line[s]+'\n')        
                frame.m_textCtrl2.AppendText('exit\n') 
                return addr

#转换nat规则
def convert_nat(filelist,l,real_dstip,err):

        noconvert=[]
        if 'enable no' in filelist[l]:
                noconvert+=filelist[l]
                err.write( '禁用的规则：'.encode('UTF-8')+filelist[l].encode('UTF-8')+b'\n')
        else:
                try:
                        line=filelist[l].split()
                        
                        if 'trans_dst' in line:
                                real_dstip[line[line.index('trans_dst')+1]]=line[line.index('orig_dst')+1][1:]
                        srcaddr=getaddr('orig_src',line)
                        dstaddr=getaddr('orig_dst',line)
                        if 'trans_src' in line:
                                frame.m_textCtrl2.AppendText('snatrule from '+srcaddr+' to '+dstaddr+' trans-to address-book'+line[line.index('trans_src')+1]+' mode static\n ')
                        elif 'trans_dst' in line:
                                frame.m_textCtrl2.AppendText('dnatrule from '+srcaddr+' to '+dstaddr+' trans-to address-book'+line[line.index('trans_dst')+1]+'\n')
                except:
                        err.write( '未转换的规则：'.encode('UTF-8')+filelist[l].encode('UTF-8')+b'\n')
        
        
        return l

        
#地址转换函数
def convert_host_address(filelist,l):
    fileline=filelist[l].split()
    addr_name=fileline[6]
    frame.m_textCtrl2.AppendText('address '+addr_name+'\n')
    frame.m_textCtrl2.AppendText(' ip '+fileline[8][1:]+'/32\n')
    h=9
    while h<len(fileline):
            if "'" not in fileline[h]:
                    frame.m_textCtrl2.AppendText(' ip '+fileline[h]+'/32\n')
            else:
                    break
            h+=1
    frame.m_textCtrl2.AppendText('exit\n')   
    return l


#服务组转换函数 与conver_host_address雷同
def convert_service_group(filelist,l):
    fileline=filelist[l].split()
    serv_name=fileline[6]
    frame.m_textCtrl2.AppendText('servgroup '+serv_name+'\n')
    frame.m_textCtrl2.AppendText(' service '+fileline[8][1:]+'/32\n')
    h=9
    while h<len(fileline):
            if "'" not in fileline[h]:
                    frame.m_textCtrl2.AppendText(' service '+fileline[h]+'\n')
            else:
                    break
            h+=1
    frame.m_textCtrl2.AppendText('exit\n')   
    return l

#地址组转换函数
def convert_address_group(filelist,l):
    fileline=filelist[l].split()
    serv_name=fileline[6]
    frame.m_textCtrl2.AppendText('address '+serv_name+'\n')
    frame.m_textCtrl2.AppendText(' member'+fileline[8][1:]+'\n')
    h=9
    while h<len(fileline):
            if "'" not in fileline[h]:
                    frame.m_textCtrl2.AppendText(' member '+fileline[h]+'\n')
            else:
                    break
            h+=1
    frame.m_textCtrl2.AppendText('exit\n')   
    return l

#子网地址和地址范围转换函数
def convert_subnet_range_address(filelist,l,addrtype=''):
    fileline=filelist[l].split()
    addr_name=fileline[6]
    frame.m_textCtrl2.AppendText('address '+addr_name+'\n')
    if addrtype=='range':
            frame.m_textCtrl2.AppendText(' range '+fileline[8]+'/'+fileline[10]+'\n')
    else:
            frame.m_textCtrl2.AppendText(' ip '+fileline[8]+'/'+fileline[10]+'\n')
    frame.m_textCtrl2.AppendText(' exit\n')
    return l

#服务簿转换函数
def convert_service(filelist,l):
    fileline=filelist[l].split()
    if fileline[8]=='6':
            prot=' tcp dst-port '
    elif fileline[8]=='17':
            prot=' udp dst-port '
    else:
            prot=' icmp '
    frame.m_textCtrl2.AppendText('service '+fileline[6]+'\n')
    if fileline[11]=='vsid':
            frame.m_textCtrl2.AppendText(' '+prot+' '+fileline[10]+'\n')
    elif fileline[11]=='port2':
            frame.m_textCtrl2.AppendText(' '+prot+' '+fileline[10]+' '+fileline[12]+'\n')
    frame.m_textCtrl2.AppendText('exit\n')         
    return l


#转换路由
def convert_route(filelist,l):
        fileline=filelist[l].split()
        frame.m_textCtrl2.AppendText('ip route '+fileline[4]+' '+fileline[6]+' '+fileline[8]+'\n')
        return l
#############天融信转换函数结束##############################




#net staice


#策略转换函数
def convert_policy111(filelist,l):
    fileline=filelist[l].split()
    description=fileline[1]
    srczone=filelist[l+1]
    dstzone=filelist[l+2]
    frame.m_textCtrl2.AppendText('rule \n description '+description+'\n'+srczone+'\n'+dstzone+'\n')
    l=l+2
    while l<len(filelist):
        l+=1
        #print(i)
        subline=filelist[l].split()        
        #print(subline)
        if  '!' in filelist[l]:
            break
        elif 'src-ip' in filelist[l]:
            frame.m_textCtrl2.AppendText(' src-addr '+subline[1]+'\n')
        elif 'src-ip-group' in filelist[l]:
            frame.m_textCtrl2.AppendText(' src-addr '+subline[1]+'\n')
        elif 'dst-ip' in filelist[l]:
            frame.m_textCtrl2.AppendText(' dst-addr '+subline[1]+'\n')                
        elif 'dst-ip-group' in filelist[l]:
            frame.m_textCtrl2.AppendText(' dst-addr '+subline[1]+'\n')   
        elif 'pre-service' in filelist[l]:
            frame.m_textCtrl2.AppendText(' service '+subline[1]+'\n')                   
        elif 'usr-service' in filelist[l]:
            frame.m_textCtrl2.AppendText(' service '+subline[1]+'\n')    
        elif 'action pass' in filelist[l]:
            frame.m_textCtrl2.AppendText(' action permit'+'\n')
        elif 'state off' in filelist[l]:
            frame.m_textCtrl2.AppendText(' disable\n')
        
    return l

	
def convert_natstatic(filelist,l,nattype=''):
        fileline=filelist[l].split()
        ruleid=fileline[2]
        while l<len(filelist):
                l+=1
                subline=filelist[l].split()
                if '!' in filelist[l]:
                        break
                elif 'private' in filelist[l]:                        
                        private=subline[1]
                elif 'public' in filelist[l]:
                        publie=subline[1]
        frame.m_textCtrl2.AppendText('\n')
        frame.m_textCtrl2.AppendText('dnatrule id '+ruleid+' from Any to '+publie+' trans-to '+private+'\n')
        if nattype !='dst-nat':
                frame.m_textCtrl2.AppendText('snatrule id '+ruleid+' from '+private+' to "Any" service "Any" trans-to '+publie+' mode static\n')
        
        return l




def getconfig():
        config=frame.m_textCtrl2.GetValue()
        nowTime=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        newconfig=open('hillstone_config'+nowTime+'.txt','wb')
        newconfig.write(config.encode())
        newconfig.close()
        frame.m_textCtrl3.AppendText('文件导出成功！配置文件路径在：'+os.getcwd()+'\\hillstone_config'+nowTime+'.txt')

if __name__ == '__main__':
    app = wx.App(False)
    frame= h3ctohillstone(None,'a')
    frame.Show()
    app.MainLoop()
    pass
