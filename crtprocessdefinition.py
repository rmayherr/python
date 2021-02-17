######################################################################  
# Create java process definition                                     #  
# Modifications:                                                     #  
#   20210216  C49677 Creation date                                   #  
######################################################################  
c='xxxxxxxx'                                                            
nd='xxxxxxxx'                                                          
s='xxxxxxx'                                                            
kv={"server_SMF_server_activity_enabled": "1",                          
    "server_SMF_server_interval_enabled": "1",                          
    "server_SMF_container_activity_enabled": "1",                       
    "server_SMF_container_interval_enabled": "1",                       
    "server_SMF_interval_length": "0",                                  
    "server_SMF_request_activity_enabled": "1",                         
    "server_SMF_request_activity_CPU_detail": "0",                      
    "server_SMF_request_activity_timestamps": "0",                      
    "server_SMF_request_activity_security": "0",                        
    "server_SMF_request_activity_async": "0",                           
    "server_SMF_outbound_enabled": "1"                                  
   }                                                                    
#Query server xml                                                       
xmlid=AdminConfig.getid('/Cell:'+c+'/Node:'+nd+'/Server:'+s+'/')        
                                                                        
#Query Process definition, order is: 0 Control 1 Servant 2 Adjunct      
pdef=AdminConfig.list('JavaProcessDef', xmlid)                          
cr=pdef.split('\n')[0]                                                  
sr=pdef.split('\n')[1]                                                  
                                                                        
#Add key/values for Servant                                             
for k,v in kv.items():                                                  
  AdminConfig.create('Property', sr,'[ \                                
  [name '+k+'] \                                                        
  [value '+v+']]')                                                      
                                                                        
#Add key/values for Control                                             
for k,v in kv.items():                                                  
  AdminConfig.create('Property', cr,'[ \                                
  [name '+k+'] \                                                        
  [value '+v+']]')                                                      
AdminConfig.save()                                                      