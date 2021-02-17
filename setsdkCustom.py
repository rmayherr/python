import os,sys                                                              
                                                                           
#filename with absolute path                                               
WF = "/tmp/SDKsettings.txt"                                                
#Server names which need to be set                                         
SR = ["aa","bb","cc","nodeagent","dmgr"]                                
#SDK settings                                                              
x = "1.8_64"                                                               
y = "1.8_31"                                                               
z = "1.7_31"                                                               
                                                                           
                                                                           
#wlog prints current SDK of servers to an USS file                         
def wlog(t):                                                               
 try:                                                                      
  f = open(WF,"a")                                                         
  f.write(t)                                                               
  f.write("\n")                                                            
  f.close()                                                                
 finally:                                                                  
  f.close()                                                                
                                                                           
#Query current SDK of Application Servers                                  
def getAS(nd):                                                             
  print "servers on node " + nd                                            
#Look for servers on node                                                  
  a=AdminServerManagement.listServers("APPLICATION_SERVER", nd)            
#Loop in array of servers                                                  
  for i in a:                                                              
   sn = i[0:i.find("(")]                                                   
#Determine whether H???OS server 
   if (sn[5:6] == "b" and sn[-1] == "w"):                                  
    print "H????s server!!!"                                               
    l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + sn)     
    print "SDK for " + sn + " is " + l                                     
    wlog(nd + "," + sn[-3:] + "," + l[-9:-3])                              
   else:                                                                   
    l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + sn)     
    print "SDK for " + sn + " is " + l                                     
    wlog(nd + "," + sn[-3:] + "," + l[-9:-3])                              
                                                                           
#Set SDK for Application Servers                                           
def setAS(nd):                                                             
#Look for servers on node                                                  
  a=AdminServerManagement.listServers("APPLICATION_SERVER", nd)            
#Loop in array of servers                                                  
  for i in a:                                                              
#Set SDK for servers reside in array SR variable                           
   for j in SR:                                                            
    sn = i[0:i.find("(")]                                                  
#Determine whether servers match                                           
    if (sn[-3:] == j):                                                     
#Determine whether H???S server (bjw,bnw)                                 
      if (sn[-3:] == "bjw" or sn[-3:] == "bnw"):                           
       print "H????s server!!!"                                            
       print "Set " + y + " on " + nd + " for " + sn                       
       AdminTask.setServerSDK('-nodeName ' +nd+ ' -serverName ' +sn+ '\    
    -sdkName ' + y)                                                        
#Determine whether H?????S server (bzw)                                     
      elif (sn[-3:] == "bzw"):                                             
       print "H???s server!!!"                                            
       print "Set " + z + " on " + nd + " for " + sn                       
       AdminTask.setServerSDK('-nodeName ' +nd+ ' -serverName ' +sn+ '\    
    -sdkName ' + z)                                                        
      else:                                                                
       print "Set " + x + " on " + nd + " for " + sn                       
       AdminTask.setServerSDK('-nodeName ' +nd+ ' -serverName ' +sn+ '\    
    -sdkName ' + x)                                                        
                                                                           
def getIDs():                                                              
  a = ""                                                                   
#Query cell config                                                         
  cell = AdminConfig.list('Cell').split()                                  
  for j in cell:                                                           
   #print "Cell name " + AdminConfig.showAttribute(j, 'name')              
#Query node configs                                                        
   n = AdminConfig.list('Node', j).split()                                 
   for i in n:                                                             
#Query node names                                                          
   #print i                                                                
    a = AdminConfig.showAttribute(i, 'name') + " " + a                     
  return a                                                                 
                                                                           
def getSdkForNode(nd):                                                     
#Query current SDK for nodes                                               
  wsdk = AdminTask.getNodeDefaultSDK('-nodeName ' + nd )                   
  print "Default SDK for " + nd + ":" + wsdk                               
                                                                           
def setSdkForNode(nd):                                                     
#Set Java8 64bit for nodes                                                 
  j = "1.8_64"                                                             
  print "Set " + j + " for " + nd                                          
  AdminTask.setNodeDefaultSDK('-nodeName ' + nd + ' -sdkName ' + j )       
                                                                           
def getServers(nd):                                                        
#Look for dmgr or nodeagent                                                
  for i in SR:                                                             
   if (nd[4:5] == "0" and i == "dmgr"):                                    
    l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + i)      
    print "SDK for " + i + " is " + l                                      
    wlog(nd + "," + i + "," + l[-9:-3])                                    
   if (nd[4:5] == "1" and i == "nodeagent"):                               
    l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + i)      
    print "SDK for " + i + " is " + l                                      
    wlog(nd + "," + i + "," + l[-9:-3])                                    
   if (nd[4:5] == "2" and i == "nodeagent"):                               
    l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + i)      
    print "SDK for " + i + " is " + l                                      
    wlog(nd + "," + i + "," + l[-9:-3])                                    
                                                                         
def setServers(nd):                                                      
#Look for dmgr or nodeagent                                              
  for i in SR:                                                           
   if (nd[4:5] == "0" and i == "dmgr"):                                  
       print "Set " + x + " on " + nd + " for " + i                      
       AdminTask.setServerSDK('-nodeName ' +nd+ ' -serverName ' +i+ '\   
    -sdkName ' + x)                                                      
   if (nd[4:5] == "1" and i == "nodeagent"):                             
       print "Set " + x + " on " + nd + " for " + i                      
       AdminTask.setServerSDK('-nodeName ' +nd+ ' -serverName ' +i+ '\   
    -sdkName ' + x)                                                      
   if (nd[4:5] == "2" and i == "nodeagent"):                             
       print "Set " + x + " on " + nd + " for " + i                      
       AdminTask.setServerSDK('-nodeName ' +nd+ ' -serverName ' +i+ '\   
    -sdkName ' + x)                                                      
                                                                         
#Query the current settings for servers and nodes                        
b = getIDs()                                                             
for i in b.split(" "):                                                   
 if (i != ""):                                                           
  getAS(i)                                                               
  getSdkForNode(i)                                                       
  getServers(i)                                                          
                                                                         
#Set java SDK                                                            
for i in b.split(" "):                                                   
 if (i != ""):                                                           
  setAS(i)                                                               
  setSdkForNode(i)                                                       
  setServers(i)                                                          
                                                                         
#AdminConfig.save()                                                      

