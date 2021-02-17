#server = AdminConfig.getid('/Server:server1/') bbz8s01
def SetAdjunctProp():
  ServerName=AdminTask.listServers().split("(")
  server = AdminConfig.getid('/Server:????/')
  SibService = AdminConfig.list('SIBService', server)
  print "Turn on Adjunct region on " + server
  AdminConfig.modify(SibService, [["enable", "true"]])
SetAdjunctProp()
AdminConfig.save()
