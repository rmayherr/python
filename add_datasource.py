as_name = "bzw"                                                         
pname = "Derby JDBC Provider(XA)"                                       
jn = "jdbc/DefaultEJBTimerDataSource"                                   
dbname="${USER_INSTALL_ROOT}/databases/EJBTimers/${SERVER}/EJBTimerDB"  
cln="com.ibm.websphere.rsadapter.DerbyDataStoreHelper"                  
                                                                        
def create_jdbc_provider(nm, s):                                        
  AdminTask.createJDBCProvider('-scope Node='+nm+',Server='+s+ \        
  ' -databaseType Derby -providerType "Derby JDBC Provider" \           
  -implementationType "XA data source" -name '+pname+ \                 
  ' -description "Derby embedded XA JDBC Provider." \                   
  -classpath ${DERBY_JDBC_DRIVER_PATH}/derby.jar -nativePath ""')       
                                                                        
def getIDs():                                                           
  a = ""                                                                
  #Getting cell config                                                  
  cell = AdminConfig.list('Cell').split()                               
  for j in cell:                                                        
   #print "Cell name " + AdminConfig.showAttribute(j, 'name')           
   #Getting node configs                                                
   n = AdminConfig.list('Node', j).split()                              
   for i in n:                                                          
    #Getting node names                                                 
    a = AdminConfig.showAttribute(i, 'name') + " " + a                  
  return a                                                              
                                                                        
def getServers(nd):                                                     
#Look for servers on node                                               
  a=AdminServerManagement.listServers("APPLICATION_SERVER", nd)         
#Loop in array of servers                                               
  for i in a:                                                           
   sn = i[0:i.find("(")]                                                
#Catch server defined in as_name variable                               
   if (sn[5:] == as_name.lower()):                                      
   #create_jdbc_provider(nd,sn)                                         
    id = AdminConfig.getid('/Server:'+sn+'/JDBCProvider:'+pname+ \      
    '/')                                                                
    AdminTask.createDatasource(id,'-name "'+pname+'" -jndiName ' + \    
    jn + ' -dataStoreHelperClassName '+cln+' -xaRecoveryAuthAlias \     
 -configureResourceProperties [[databaseName java.lang.String '+ \      
    dbname+']]')                                                        
#   AdminConfig.list('Datasource',AdminConfig.getid('/Server:'+sn+'/')) 
                                                                        
#start script                                                           
b = getIDs()                                                            
for i in b.split(" "):                                                  
 if (i != ""):                                                          
  #print i                                                              
  getServers(i)                                                         
AdminConfig.save()                                                      