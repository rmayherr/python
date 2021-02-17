#Servers which need to be set                                                
SR = ["aaa","bbb"]                                                           
#Query current SDK of servers                                                
def getServers(nd):                                                          
  print "servers on node " + nd                                              
#Look for servers on node                                                    
  a=AdminServerManagement.listServers("APPLICATION_SERVER", nd)              
#Loop in array of servers                                                    
  for i in a:                                                                
   sn = i[0:i.find("(")]                                                     
#Determine whether H???OS server                                
   if (sn[5:6] == "b" and sn[-1] == "w"):                                    
    print "H???? server!!!"                                                 
    l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + sn)       
    print "SDK for " + sn + " is " + l                                       
   else:                                                                     
    l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + sn)       
    print "SDK for " + sn + " is " + l                                       
                                                                             
#Set SDK for servers                                                         
def setServers(nd):                                                          
  x = "1.8_64"                                                               
  y = "1.8_31"                                                               
  z = "1.7_31"                                                               
#Look for servers on node                                                    
  a=AdminServerManagement.listServers("APPLICATION_SERVER", nd)              
#Loop in array of servers                                                    
  for i in a:                                                                
#Determine whether H????OS server (bjw,bnw)                                   
   sn = i[0:i.find("(")]                                                     
   if (sn[-3:] == "bjw" or sn[-3:] == "bnw"):                                
    print "H????s server!!!"                                                 
    print "Set " + y + " on " + nd + " for " + sn                            
    AdminTask.setServerSDK('-nodeName ' +nd+ ' -serverName ' +sn+ '\         
  -sdkName ' + y)                                                            
#Determine whether bzw server                                                
   if (sn[-3:] == "bzw"):                                                    
    print "H???s server!!!"                                                 
    print "Set " + z + " on " + nd + " for " + sn                            
    AdminTask.setServerSDK('-nodeName ' +nd+ ' -serverName ' +sn+ '\         
  -sdkName ' + z)                                                            
#Set SDK for servers reside in array SR variable                             
   for j in SR:                                                              
    if (sn[-3:] == j):                                                       
     print "Set " + x + " on " + nd + " for " + sn                           
     AdminTask.setServerSDK('-nodeName ' +nd+ ' -serverName ' +sn+ '\        
  -sdkName ' + z)                                                            

def getIDs():                                                            
  a = ""                                                                 
  #Getting cell config                                                   
  cell = AdminConfig.list('Cell').split()                                
  for j in cell:                                                         
   #print "Cell name " + AdminConfig.showAttribute(j, 'name')            
   #Getting node configs                                                 
   n = AdminConfig.list('Node', j).split()                               
   for i in n:                                                           
    #Getting node names                                                  
    a = AdminConfig.showAttribute(i, 'name') + " " + a                   
  return a                                                               
                                                                         
def getSdkForNode(nd):                                                   
  #Getting current SDK for nodes                                         
  wsdk = AdminTask.getNodeDefaultSDK('-nodeName ' + nd )                 
  print "Default SDK for " + nd + ":" + wsdk                             
                                                                         
def setSdkForNode(nd):                                                   
  #Setting Java8 64bit for nodes                                         
  j = "1.8_64"                                                           
  print "Set " + j + " for " + nd                                        
  AdminTask.setNodeDefaultSDK('-nodeName ' + nd + ' -sdkName ' + j )     
                                                                         
                                                                         
#Getting the current settings for servers and nodes                      
b = getIDs()                                                             
for i in b.split(" "):                                                   
 if (i != ""):                                                           
  #print i                                                               
  getServers(i)                                                          
  getSdkForNode(i)                                                       
                                                                         
#Setting java8 31bit or 64bit for servers and nodes accordingly          
for i in b.split(" "):                                                   
 if (i != ""):                                                           
  #print i                                                               
  setServers(i)                                                          
  setSdkForNode(i)                                                       
                                                                         
#AdminConfig.save()                                                      
                                                                             
                                                                             

