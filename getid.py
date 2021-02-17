def getIDs():                                       
  a = ""
  #Get cell config                                  
  cell = AdminConfig.list('Cell').split()      
  for j in cell:                                    
   #print "Cell name " + AdminConfig.showAttribute(j, 'name')    
   #Get node configs                                
   n = AdminConfig.list('Node', j).split()          
   for i in n:                                      
    #Get node names                                 
    a = AdminConfig.showAttribute(i, 'name') + " " + a
  return a

def get51Servers(nd):                                                          
  print "servers on node " + nd                                              
  a=AdminServerManagement.listServers("APPLICATION_SERVER", nd)              
  for i in a:                                                                
   sn = i[0:i.find("(")]                                                     
   if (sn[5:6] == "b" and sn[-1] == "w"):                                    
    print "Helios server!!!"                                                 
    l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + sn)       
    print "SDK for " + sn + " is " + l                                       
   else:                                                                     
    l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + sn)       
    print "SDK for " + sn + " is " + l      

b = getIDs()
for i in b.split(" "):
	if (i != ""):
		#print i
		get51Servers(i)

