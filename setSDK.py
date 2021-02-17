def getSdkForNode():                                                      
 wnodes = ["w????de","????node","???,ode"]                           
 for v in wnodes:                                                         
  wsdk = AdminTask.getNodeDefaultSDK('-nodeName ' + v )                   
  print "Default SDK for " + v + ":" + wsdk                               
                                                                          
def setSdkForNode():                                                      
  wnodes = ["w????de","????node","???,ode"]                           
  j = "1.8_64"                                                            
  for v in wnodes:                                                        
   print "Set " + j + " for " + v                                         
   AdminTask.setNodeDefaultSDK('-nodeName ' + v + ' -sdkName ' + j + ' \  
 -clearServerSDKs true')                                                  
                                                                                                
                                                                        
 def get51Servers():                                                    
   n = "wxxxde"                                                      
   print "servers on node " + n                                         
   a=AdminServerManagement.listServers("APPLICATION_SERVER", n)         
   for i in a:                                                          
    sn = i[0:i.find("(")]                                               
    l=AdminTask.getServerSDK('-nodeName ' + n + ' -serverName ' + sn)   
    print "SDK for " + sn + " is " + l                                  
                                                                        
 def get52Servers():                                                    
   n = "wxasssssde"                                                      
   print "servers on node " + n                                         
   a=AdminServerManagement.listServers("APPLICATION_SERVER", n)         
   for i in a:                                                          
    sn = i[0:i.find("(")]                                               
    l=AdminTask.getServerSDK('-nodeName ' + n + ' -serverName ' + sn)   
    print "SDK for " + sn + " is " + l                                                                                                                                                  
                                                   
def set51Servers():                                                    
  n = "wssssde"                                                      
  j = "1.8_64"                                                         
  a=AdminServerManagement.listServers("APPLICATION_SERVER", n)         
  for i in a:                                                          
   sn = i[0:i.find("(")]                                               
   print "Set " + j + " on " + n + " for " + sn                        
   AdminTask.setServerSDK('-nodeName ' + n + ' -serverName ' + sn + '\ 
 -sdkName ' + j)                                                       
                                                                                                                    
    
/data/WebSphere/wxadomain/wxa50node/dm/bin >./managesdk.sh -listEnabledProfileAll
/data/WebSphere/wxadomain/wxa50node/dm/bin >./managesdk.sh -getNewProfileDefault
																		-getCommandDefault
/data/WebSphere/wxadomain/wxa51node/as/profiles/default/bin/managesdk.sh -enableProfileAll -sdkname $JVM -enableServers -user -password


