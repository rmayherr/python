#server = AdminConfig.getid('/Server:server1/') 
def SetAdjunctProp():
  ServerName=AdminTask.listServers().split("(")
  server = AdminConfig.getid('/Server:??????1/')
  SibService = AdminConfig.list('SIBService', server)
  print "Turn on Adjunct region on " + server
  AdminConfig.modify(SibService, [["enable", "true"]])
SetAdjunctProp()
AdminConfig.save()
