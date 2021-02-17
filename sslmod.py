######################################################################       
# Change SSL settings in Websphere by changing keyring location      #       
#                                                                    #       
#                                                                    #       
#                                                                    #       
# Author                                                             #       
# Roland Mayherr                                                     #       
#                                                                    #       
# Modification                                                       #       
#   20210129 Creation date                                           #       
######################################################################       
                                                                             
cname="xxll"                                                             
nname="??node"                                                            
nname2="??node"                                                           
ksn="NodeDefaultKeyStore"                                                    
                                                                             
def change_keystore_node51():                                                
  AdminTask.modifyKeyStore(' -keyStoreName ' + ksn +\                        
' -scopeName (cell):' + cname + ':(node):' + nname +\                        
' -keyStoreLocation safkeyring://userid/ringname '\                         
'-keyStoreType JCERACFKS -keyStoreReadOnly true')                            
                                                                             
def change_keystore_node52():                                                
  AdminTask.modifyKeyStore(' -keyStoreName ' + ksn +\                        
' -scopeName (cell):' + cname + ':(node):' + nname2 +\                       
' -keyStoreLocation safkeyring://userid/ringname '\                         
'-keyStoreType JCERACFKS -keyStoreReadOnly true')                            
                                                                             
change_keystore_node51()                                                     
change_keystore_node52()                                                     
                                                                             