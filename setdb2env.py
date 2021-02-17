NodeName=AdminControl.getNode()
def SetDB2Variables():
  WFound=0
  WVariables={"DB2UNIVERSAL_JDBC_DRIVER_NATIVEPATH" : "/??????????ult/etc/DB2JDBC",
              "MQ_INSTALL_ROOT" : "/?????????",
              "DB2UNIVERSAL_JDBC_DRIVER_PATH" : "/?????????lt/etc/DB2JDBC/classes"}
  Node=AdminConfig.getid("/Node:"+NodeName+"/VariableMap:/")
  WVarSub=AdminConfig.list("VariableSubstitutionEntry",Node).split()
  for Wkey,Wvalue in WVariables.items():
    for SubVar in WVarSub:
      GetVarName = AdminConfig.showAttribute(SubVar, "symbolicName")
      if GetVarName == Wkey:
        WFound=1
    if WFound == 1:
      print "Modify key " + Wkey + " with the value " + Wvalue
      AdminConfig.modify(SubVar,[['value', Wvalue]])
    else:
      print "Set key " + Wkey + " with the value " + Wvalue
      AdminTask.setVariable('-scope Node='+NodeName+' -variableName '+Wkey+' -variableValue '+Wvalue+'')
SetDB2Variables()
AdminConfig.save()
