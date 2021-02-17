def get51Servers():                                                         
  n = "wxa51node"                                                           
  print "servers on node " + n                                              
  a=AdminServerManagement.listServers("APPLICATION_SERVER", n)              
  for i in a:                                                               
   sn = i[0:i.find("(")]                                                    
   l=AdminTask.getServerSDK('-nodeName ' + n + ' -serverName ' + sn)        
   print "SDK for " + sn + " is " + l                                       
                                                                            
def set51Servers():                                                         
  n = "wxa51node"                                                           
  j = "1.8_64"                                                              
  a=AdminServerManagement.listServers("APPLICATION_SERVER", n)              
  for i in a:                                                               
   sn = i[0:i.find("(")]                                                    
   print "Set " + j + " on " + n + " for " + sn                             
   AdminTask.setServerSDK('-nodeName ' + n + ' -serverName ' + sn + '\      
 -sdkName ' + j)                                                            
                                                                            
set51Servers()                                                              
AdminConfig.save()                                                          
get51Servers()                                                              
