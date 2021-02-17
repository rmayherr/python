def getServers():
 nd = "nodea"
#Get xml files for servers on node
 a = AdminServerManagement.listServers("APPLICATION_SERVER", "nodea")
 for i in a:
  sname = i[0:i.find("(")]
  l = AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + sname)
  print l

getServers()
------
def getSdkForNode():                                                  
 wnodes = ["wxa50node","wxa51node","wxa52node"]                       
 for wvalue in wnodes:                                                
  wsdk = AdminTask.getNodeDefaultSDK('-nodeName ' + wvalue )          
  print "Default SDK for " + wvalue + ":" + wsdk                      
                                                                      
def getSdkForServer():                                                
  n = ["wxa51node","wxa52node"]                                       
  for v in n:                                                         
   print "servers on node " + v                                       
   a=AdminServerManagement.listServers("APPLICATION_SERVER", v)       
   for i in a:                                                        
    sn = i[0:i.find("(")]                                             
    l=AdminTask.getServerSDK('-nodeName ' + v + ' -serverName ' + sn) 
    print "SDK for " + sn + " is " + l                                
                                                                      
getSdkForServer()                                                     

