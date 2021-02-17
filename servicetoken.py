c = ""                                                                     
def getIDs():                                                              
  global c                                                                 
  a = ""                                                                   
#Query cell config xml                                                     
  cell = AdminConfig.list('Cell').split()                                  
#Gain cell name                                                            
  c = cell[0].split('(')[0]                                                
  for j in cell:                                                           
#Query node config xml                                                     
   n = AdminConfig.list('Node', j).split()                                 
   for i in n:                                                             
#Query node names                                                          
    a = AdminConfig.showAttribute(i, 'name') + " " + a                     
  return a                                                                 
                                                                           
def getAS(nd):                                                             
  global c                                                                 
#Look for servers on node                                                  
  a=AdminServerManagement.listServers("APPLICATION_SERVER", nd)            
#Loop in array of servers                                                  
  for i in a:                                                              
#Gain server names                                                         
    sn = i[0:i.find("(")]                                                  
#Matching server on node                                                   
    if (sn == "wxa91wxt"):                                                 
      print("Cell:"+ c +" Node:" + nd + " Server:" + sn)                   
                                                                           
#Create Keystore for specific server                                       
      AdminTask.createKeyStore('-keyStoreName '+sn+'_test -scopeName '\    
'(cell):'+c+':(node):'+nd+':(server):'+sn+' -keyStoreLocation '\           
'safkeyring:///Keyring.ServiceTokens -keyStoreType JCERACFKS '\            
'-keyStoreInitAtStartup false -keyStoreReadOnly true '\                    
'-keyStoreStashFile false -keyStoreUsage SSLKeys ')                        
      AdminTask.listKeyStores('-all true -keyStoreUsage SSLKeys ')         
                                                                           
#Create JSSE                                                               
      AdminTask.createSSLConfig('-alias '+sn+'_test -type JSSE '\          
'-scopeName (cell):'+c+':(node):'+nd+':(server):'+sn+' -keyStoreName '\    
+sn+'_test -keyStoreScopeName (cell):'+c+':(node):'+nd+':(server):'\       
+sn+' -trustStoreName '+sn+'_test -trustStoreScopeName (cell):'+c+\        
':(node):'+nd+':(server):'+sn)                                             
      AdminTask.listSSLConfigs('-all true -displayObjectName true ')       
                                                                           
#Define outbound endpoint policy                                           
      AdminTask.createDynamicSSLConfigSelection(\                          
'-dynSSLConfigSelectionName '\                                             
+sn+'_test -scopeName (cell):'+c+':(node):'+nd+':(server):'+sn+\           
' -dynSSLConfigSelectionInfo *,u390ss4.ao.nl.abnamro.com,9443 '\           
'-dynSSLConfigSelectionDescription AAB_customisation '\                    
'-sslConfigName '+sn+'_test -sslConfigScope (cell):'+c+':(node):'+nd+\     
':(server):'+sn)                                                           
AdminTask.listDynamicSSLConfigSelections('-all true ')                     
                                                                           
def main():                                                
 b = getIDs()                                              
 for i in b.split(" "):                                    
  if (i != ""):                                            
   getAS(i)                                                
                                                           
main()                                                        
AdminConfig.save()                                         
syncNodes()                                                