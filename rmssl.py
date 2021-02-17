Cellname="???rk"                                                                                      
NodeName="???dea"                                                                                        
def Query():                                                                                              
  #a=AdminTask.help('-commands')                                                                          
  a=AdminConfig.list('KeyStore')                                                                          
  print a                                                                                                 
def RemoveCertificate():                                                                                  
                                                                                                          
   print "###########################################################################"                    
   print "Remove unused certificate"                                                                      
   print "Security > SSL certificate and key management > Key stores and certificates"                    
   print "###########################################################################"                    
   key="(ce??????????e_1478679828039)"                                            
   AdminTask.deleteKeyStore('-keyStoreName ' + key  + '')                                                 
                                                                                                          
def ListKeystores():                                                                                      
                                                                                                          
   print "###########################################################################"                    
   print "Listing keystores"                                                                              
   print "###########################################################################"                    
   listKeystore=AdminTask.listKeyStores('-all true')                                                      
   print listKeystore                                                                                     
                                                                                                          
def RemoveKeystores2():                                                                                   
                                                                                                          
   print "###########################################################################"                    
   print "Removing keystores"                                                                             
   print "###########################################################################"                    
   key="(cel?????????ore_1478679828039)"                                            
   AdminConfig.remove(key)                                                                                
                                                                                                          
#Query()                                                                                                  
#RemoveCertificate()                                                                                      
#ListKeystores()                                                                                          
RemoveKeystores2()                                                                                        
print "Saving configuration"                                                                              
AdminConfig.save()                                                                                        
