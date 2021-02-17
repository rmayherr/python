def getServers(nd):                                                            
  print "servers on node " + nd                                                
  a=AdminServerManagement.listServers("APPLICATION_SERVER", nd)                
  for i in a:                                                                  
   sn = i[0:i.find("(")]                                                       
   if (sn[5:6] == "b" and sn[-1] == "w"):                                      
    print "Helios server!!!"                                                   
    l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + sn)         
    print "SDK for " + sn + " is " + l                                         
   else:                                                                       
    l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + sn)         
    print "SDK for " + sn + " is " + l                                         
                                                                               
def setServers(nd):                                                            
  j = "1.8_64"                                                                 
  k = "1.8_31"                                                                 
  a=AdminServerManagement.listServers("APPLICATION_SERVER", nd)                
  for i in a:                                                                  
   sn = i[0:i.find("(")]                                                       
   if (sn[5:6] == "b" and sn[-1] == "w"):                                      
    print "Helios server!!!"                                                   
    print "Set " + k + " on " + nd + " for " + sn                              
   else:                                                                       
    print "Set " + j + " on " + nd + " for " + sn                              
    AdminTask.setServerSDK('-nodeName ' + nd + ' -serverName ' + sn + '\       
  -sdkName ' + j)                                                              
                                                                               
def getIDs():                                                                  
  a = ""                                                                       
  #Get cell config                                                             
  cell = AdminConfig.list('Cell').split()                                      
  for j in cell:                                                               
   #print "Cell name " + AdminConfig.showAttribute(j, 'name')                  
   #Get node configs                                                           
   n = AdminConfig.list('Node', j).split()                                     
   for i in n:                                                                 
    #Get node names                                                            
    a = AdminConfig.showAttribute(i, 'name') + " " + a                         
  return a                                                                     
                                                                               
def getSdkForNode(nd):                                                         
  wsdk = AdminTask.getNodeDefaultSDK('-nodeName ' + nd )                       
  print "Default SDK for " + nd + ":" + wsdk                                   
                                                                               
def setSdkForNode(nd):                                                         
  j = "1.8_64"                                                                 
  print "Set " + j + " for " + nd                                              
  AdminTask.setNodeDefaultSDK('-nodeName ' + nd + ' -sdkName ' + j )           
                                                                               
                                                                               
b = getIDs()                                                                   
for i in b.split(" "):                                                         
 if (i != ""):                                                                 
  #print i                                                                     
  getServers(i)                                                                
  getSdkForNode(i)                                                 
for i in b.split(" "):                      
 if (i != ""):                              
  #print i                                  
  setServers(i)                             
  setSdkForNode(i)                          
                                            
#AdminConfig.save()                         
