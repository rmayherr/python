#Query current SDK of Application Servers 
def getAS(nd): 
 print "servers on node " + nd 
#Look for servers on node 
 a=AdminServerManagement.listServers("APPLICATION_SERVER", nd) 
#Loop in array of servers 
 for i in a: 
  sn = i[0:i.find("(")] 
# l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + sn) 
  print "SDK for " + sn + " is "
# s = "nodeagent" 
# if (nd[4:5] == "1" or nd[4:5] == "2"): 
# l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + s) 
# print "SDK for " + s + " is " + l 
# s = "dmgr" 
# if (nd[4:5] == "0"): 
# l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + s) 
# print "SDK for " + s + " is " + l 
 
def getIDs(): 
 a = "" 
#Query cell config 
 cell = AdminConfig.list('Cell').split() 
 for j in cell: 
 #print "Cell name " + AdminConfig.showAttribute(j, 'name') 
#Query node configs 
 n = AdminConfig.list('Node', j).split() 
 for i in n: 
#Query node names 
 #print i 
 a = AdminConfig.showAttribute(i, 'name') + " " + a 
 return a 

#Query the current settings for servers and nodes 
b = getIDs() 
for i in b.split(" "): 
 if (i != ""): 
 getAS(i) 
 getSdkForNode(i) 
 
#AdminConfig.save() 
