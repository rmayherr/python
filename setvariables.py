CellName=AdminControl.getCell()                                                                                    
NodeName=AdminControl.getNode()                                                                                    
ServerName=AdminTask.listServers().split("(")                                                                      
def SetWASVariables():                                                                                             
  WVariables={"ras_default_msg_dd" : "DEFALTDD" ,                                                                  
              "ras_hardcopy_msg_dd" : "HRDCPYDD",                                                                  
              "DAEMON_ras_default_msg_dd" : "DEFALTDD",                                                            
              "DAEMON_ras_hardcopy_msg_dd" : "HRDCPYDD",                                                           
              "_CEE_DMPTARG" : "/tmp"}                                                                             
  print "Setting websphere variables with scope " + CellName                                                       
  print "Server name " + ServerName[0]                                                                             
  for key,value in WVariables.items():                                                                             
    print "Set the following variables " + key + " with value " + value                                            
    AdminTask.setVariable('-scope Cell='+CellName+' -variableName '+key+' -variableValue '+value+'')               
def SetRasTime():                                                                                                  
  WVariables={"DAEMON_ras_time_local" : "1"}                                                                       
  print "Setting websphere variables with scope " + CellName                                                       
  print "Server name " + ServerName[0]                                                                             
  for Wkey,Wvalue in WVariables.items():                                                                           
    print "Set the following variables " + Wkey + " with value " + Wvalue                                          
    AdminTask.setVariable('-scope Cell='+CellName+' -variableName '+ Wkey +' -variableValue '+ Wvalue +'')         
SetWASVariables()                                                                                                  
SetRasTime()                                                                                                       
#AdminConfig.save()                                                                                                
