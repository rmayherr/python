                                                                             
def get51Servers():                                                          
  global nd                                                                  
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
                                                                             
def set51Servers():                                                          
  global nd                                                                  
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
  global nd                                                                  
  nodeid = "1"                                                               
  cell = AdminConfig.list('Cell').split()                                    
  for j in cell:                                                             
   n = AdminConfig.list('Node', j).split()                                   
   for i in n:                                                               
    c = AdminConfig.showAttribute(j, 'name')                                 
    nn = AdminConfig.showAttribute(i, 'name')                                
    if (nn[4:5] == nodeid):                                                  
     nd = nn                                                                 

