def getSdkForNode():                                                    
 wnodes = ["w????e","w???ode","w???ode"]                         
 for v in wnodes:                                                       
  wsdk = AdminTask.getNodeDefaultSDK('-nodeName ' + v )                 
  print "Default SDK for " + v + ":" + wsdk                             
                                                                        
def setSdkForNode():                                                    
  wnodes = ["w???ode","w????de","w????ode"]                        
  j = "1.8_64"                                                          
  for v in wnodes:                                                      
   print "Set " + j + " for " + v                                       
   AdminTask.setNodeDefaultSDK('-nodeName ' + v + ' -sdkName ' + j )    
                                                                        
setSdkForNode()                                                         
AdminConfig.save()                                                      
getSdkForNode()                                                         
