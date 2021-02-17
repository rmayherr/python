######################################################################
# Create Keystore and new SSL configuration at specified level       #
# Modifications:                                                     #
#   20200623  C49677 Create keystore and ssl config functions        #
######################################################################
                                                                      
#Variable section                                                     
#                                                                     
#Keystore definition                                                  
#Cell name                                                            
c = "??cell"                                                        
#Keystore name                                                        
ksn = "CellDefaultServiceTokenKeyring"                                
#Keyring name                                                         
krn = "safkeyring:///???n"                            
#Keystore type                                                        
kt = "JCERACFKS"                                                      
#Description                                                          
desc = "'Default Service Token Keyring for " + c + "'"                
#                                                                     
#SSL definition                                                       
#Name                                                                 
ssln = "CellDefaultServiceTokenSettings"                              
#Protocol                                                             
p = "SSL_TLSv2"                                                       
                                                                      
                                                                      
#Function queries servers on nodes and alter their configuration      
def do_config():                                                      
  global c                                                            
  global ksn                                                          
  global krn                                                          
  global kt                                                           
  global desc                                                         
  global ssln                                                         
  global p                                                            
                                                                      
#Create Keystore for specific server                                  
  AdminTask.createKeyStore('-keyStoreName '+ksn+' -scopeName '\       
'(cell):'+c+' -keyStoreLocation '+krn+' -keyStoreType '+kt+\          
' -keyStoreDescription '+desc+' -keyStoreStashFile false '\           
'-keyStoreInitAtStartup false -keyStoreReadOnly true '\               
'-keyStoreUsage SSLKeys')                                             
  AdminTask.listKeyStores('-all true -keyStoreUsage SSLKeys ')        
                                                                      
#Create JSSE                                                          
  AdminTask.createSSLConfig('-alias '+ssln+' -type JSSE '\            
'-scopeName (cell):'+c+' -keyStoreName '+ksn+\                        
' -keyStoreScopeName (cell):'+c+' -trustStoreName '+ksn+\             
' -trustStoreScopeName (cell):'+c+' -sslProtocol '+p)                 
  AdminTask.listSSLConfigs('-all true -displayObjectName true ')      

                                  
def main():                       
  do_config()                     
                                  
                                  
main()                                                                                                  
                                                                     
