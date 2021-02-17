######################################################################
# Configure ciphers on different levels in order to harden security  #
#                                                                    #
# Author                                                             #
# Roland Mayherr                                                     #
#                                                                    #
# Modification                                                       #
#   20200902 Creation date                                           #
######################################################################
elem =  'NodeDefaultSSLSettings', 'CellDefaultSSLSettings',\          
        'XDADefaultSSLSettings'                                       
                                                                      
c = "??"                                                              
                                                                      
for i in elem:                                                        
 if i == 'NodeDefaultSSLSettings':                                    
  for j in range(1,2):                                                
   AdminTask.modifySSLConfig('-alias '+i+\                            
' -scopeName (cell):wx'+c+'cell:(node):wx'+c+str(j)+'node' \          
' -sslProtocol TLSv1.2 -securityLevel CUSTOM' \                       
' -enabledCiphers "' \                                                
'SSL_DHE_RSA_WITH_AES_128_GCM_SHA256' \                               
' SSL_DHE_RSA_WITH_AES_256_GCM_SHA384' \                              
' SSL_ECDHE_RSA_WITH_AES_128_GCM_SHA256' \                            
' SSL_ECDHE_RSA_WITH_AES_256_GCM_SHA384"')                            
 else:                                                                
  AdminTask.modifySSLConfig('-alias '+i+\                             
' -scopeName (cell):wx'+c+'cell' \                                    
' -sslProtocol TLSv1.2 -securityLevel CUSTOM' \                       
' -enabledCiphers "' \                                                
'SSL_DHE_RSA_WITH_AES_128_GCM_SHA256' \                               
' SSL_DHE_RSA_WITH_AES_256_GCM_SHA384' \                              
' SSL_ECDHE_RSA_WITH_AES_128_GCM_SHA256' \                            
' SSL_ECDHE_RSA_WITH_AES_256_GCM_SHA384"')                            