#######################################
#                                     #
# Customize the variables accordingly #
#                                     #
#######################################
#CellName=AdminControl.getCell()
CellName="was36ecell"
NodeName="bb85na"
ServerName="bb85as2"
RegionType="Servant"
#NodeName=AdminControl.getNode()
#ServerName=AdminTask.listServers().split("(")
#######################################

def SetCellLevelWASVariables():
  print "-----------------------------------"
  print "Starting function SetCellLevelWASVariables()"
  print "-----------------------------------"
  WFound=0

  ##################################################
  #                                                #
  # Set WAS environment variables in "WVariables"  #
  #                                                #
  ##################################################

  WVariables={"ras_default_msg_dd" : "DEFALTDD" ,
              "ras_hardcopy_msg_dd" : "HRDCPYDD",
              "DAEMON_ras_default_msg_dd" : "DEFALTDD",
              "DAEMON_ras_hardcopy_msg_dd" : "HRDCPYDD",
              "JAVA_DUMP_TDUMP_PATTERN" : "SYS1.DUMP.&JOBNAME..D&YYMMDD..T&HHMMSS..S&SEQ.",
              "_CEE_DMPTARG" : "/tmp"}
  Cell=AdminConfig.getid("/Cell:"+CellName+"/VariableMap:/")
  WVarSub=AdminConfig.list("VariableSubstitutionEntry",Cell).split()
  print "Setting websphere variables with scope " + CellName
  #print "Server name " + ServerName[0]
  for Wkey,Wvalue in WVariables.items():
    for SubVar in WVarSub:
      GetVarName = AdminConfig.showAttribute(SubVar, "symbolicName")
      if Wkey == GetVarName:
        WFound=1
        print "Modify variable " + Wkey + " with the value " + Wvalue
        AdminConfig.modify(SubVar,[['value', Wvalue]])
    WFound=0
    if WFound == 0:
      print "Set variables " + Wkey + " with value " + Wvalue
      AdminTask.setVariable('-scope Cell='+CellName+' -variableName '+Wkey+' -variableValue '+Wvalue+'')

def SetRasTime():
  print "------------------------------"
  print "Starting function SetRasTime()"
  print "------------------------------"
  WFound=0

  ##################################################
  #                                                #
  # Set WAS environment variables in "WVariables"  #
  #                                                #
  ##################################################

  WVariables={"DAEMON_ras_time_local" : "1"}
  Cell=AdminConfig.getid("/Cell:"+CellName+"/VariableMap:/")
  WVarSub=AdminConfig.list("VariableSubstitutionEntry",Cell).split()
  print "Setting websphere variables with scope " + CellName
  for Wkey,Wvalue in WVariables.items():
    for SubVar in WVarSub:
      GetVarName = AdminConfig.showAttribute(SubVar, "symbolicName")
      if Wkey == GetVarName:
        WFound=1
        print "Modify key " + Wkey + " with the value " + Wvalue
        AdminConfig.modify(SubVar,[['value', Wvalue]])
    WFound=0
    if WFound == 0:
      print "Set key " + Wkey + " with the value " + Wvalue
      AdminTask.setVariable('-scope Cell='+CellName+' -variableName '+Wkey+' -variableValue '+Wvalue+'')

def SetNodeLevelVariables():
  print "-----------------------------------"
  print "Starting function SetNodeLevelVariables()"
  print "-----------------------------------"
  WFound=0

  ##################################################
  #                                                #
  # Set WAS environment variables in "WVariables"  #
  #                                                #
  ##################################################

  WVariables={"DB2UNIVERSAL_JDBC_DRIVER_NATIVEPATH" : "/was/85/was36g/appserver/Applg0/profiles/default/etc/DB2JDBC",
              "MQ_INSTALL_ROOT" : "/usr/local/aop/WebSphere/mqm/QMG1J5",
              "DB2UNIVERSAL_JDBC_DRIVER_PATH" : "/was/85/was36g/appserver/Applg0/profiles/default/etc/DB2JDBC/classes"}
  Node=AdminConfig.getid("/Node:"+NodeName+"/VariableMap:/")
  print "Setting variables on node " + NodeName
  WVarSub=AdminConfig.list("VariableSubstitutionEntry",Node).split()
  for Wkey,Wvalue in WVariables.items():
    for SubVar in WVarSub:
      GetVarName = AdminConfig.showAttribute(SubVar, "symbolicName")
      if GetVarName == Wkey:
        WFound=1
        print "Modify key " + Wkey + " with the value " + Wvalue
        AdminConfig.modify(SubVar,[['value', Wvalue]])
    WFound=0
    if WFound == 0:
      print "Set key " + Wkey + " with the value " + Wvalue
      AdminTask.setVariable('-scope Node=' + NodeName + ' -variableName ' + Wkey + ' -variableValue ' + Wvalue + '')

def SetAdjunctProp():
  print "----------------------------------"
  print "Starting function SetAdjunctProp()"
  print "----------------------------------"
  server = AdminConfig.getid('/Server: ' + ServerName + ' /')
  SibService = AdminConfig.list('SIBService', server)
  print "Turn on Adjunct region on " + ServerName
  AdminConfig.modify(SibService, [["enable", "true"]])

def SetVerboseGc():
  print "--------------------------------"
  print "Starting function SetVerboseGc()"
  print "--------------------------------"
  print "Turn on verbose gc on node " + NodeName + " on server " + ServerName
  AdminTask.setJVMProperties('-nodeName ' + NodeName + ' -serverName ' + ServerName + ' -processType Servant -verboseModeGarbageCollection true')

def SetJvmArguments():
  print "-----------------------------------"
  print "Starting function SetJvmArguments()"
  print "-----------------------------------"
  print "Modifing JVM argument on node " + NodeName + " on server " + ServerName + " with value -Xgcpolicy:gencon"
  AdminTask.setJVMProperties('-nodeName ' + NodeName + ' -serverName ' + ServerName + ' -processType Servant -genericJvmArguments "-Xgcpolicy:gencon"')

def NodeSync():
  print "----------------------------"
  print "Starting function NodeSync()"
  print "----------------------------"
  print "Syncronizing node..."
  Sync1 = AdminControl.completeObjectName('type=NodeSync,node=' + NodeName + ',*')
  AdminControl.invoke(Sync1, 'sync')

def SetInstances():
  print "--------------------------------"
  print "Starting function SetInstances()"
  print "--------------------------------"
  AdminTask.setServerInstance('-nodeName ' + NodeName + ' -serverName ' + ServerName + ' -enableMultipleServerInstances "true"')
  AdminTask.setServerInstance('-nodeName ' + NodeName + ' -serverName ' + ServerName + ' -minimumNumOfInstances "1"')
  AdminTask.setServerInstance('-nodeName ' + NodeName + ' -serverName ' + ServerName + ' -maximumNumberOfInstances "2"')

#-------------------------------------------------------------------------------------------------------#

SetCellLevelWASVariables()
SetRasTime()
SetNodeLevelVariables()
SetAdjunctProp()
SetVerboseGc()
SetJvmArguments()
SetInstances()
NodeSync()
print "---------------------------"
print "Saving to master-repository"
print "---------------------------"
AdminConfig.save()
