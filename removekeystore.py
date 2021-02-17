Cellname="?????k"                                                                               
NodeName="???a"                                                                                 
#a=AdminTask.help('-commands')                                                                     
def RemoveCertificate():                                                                           
                                                                                                   
   print "###########################################################################"             
   print "Remove unused certificate"                                                               
   print "Security > SSL certificate and key management > Key stores and certificates"             
   print "###########################################################################"             
   keystoreName="KeyStore_1478679828039"                              
   AdminTask.deleteKeyStore('-keyStoreName', ' + keystoreName  + ')                                
                                                                                                   
def ListKeystores():                                                                               
                                                                                                   
   print "###########################################################################"             
   print "Listing keystores"                                                                       
   print "###########################################################################"             
   listKeystore=AdminTask.listKeyStores('-all true')                                               
   print listKeystore                                                                              
                                                                                                   
#RemoveCertificate()                                                                               
#AdminConfig.save()                                                                                
