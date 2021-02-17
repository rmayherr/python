CellName=AdminControl.getCell()
NodeName=AdminControl.getNode()
ServerName=AdminTask.listServers().split("(")
#server = AdminConfig.getid('/Server:server1/')
def SetVerboseGc():
  AdminTask.setJVMProperties('-serverName', ServerName, '-nodeName', NodeName, '-verboseModeGarbageCollection', 'true')
SetVerboseGc()
#AdminConfig.save()
