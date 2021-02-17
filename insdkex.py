import os,sys,time                                                       
                                                                         
#Make a timestamp                                                        
T=time.strftime('%H') + time.strftime('%M') + time.strftime('%S')        
#filename with absolute path. Be aware of that content must be           
#in ASCII!!!                                                             
WF = "/tmp/SDKsettings_" + T + ".txt"                                    
                                                                         
#wlog prints current SDK of servers to an USS file                       
def wlog(t):                                                             
 try:                                                                    
  f = open(WF,"a")                                                       
  f.write(t)                                                             
  f.write("\n")                                                          
  f.close()                                                              
 except:                                                                 
   print sys.exc_info()[0], sys.exc_info()[1]                            
   sys.exit(8)                                                           
 else:                                                                   
   f.close()                                                             
                                                                         
#Query current SDK of Application Servers                                
def getAS(nd):                                                           
  print "servers on node " + nd                                          
#Look for servers on node                                                
  a=AdminServerManagement.listServers("APPLICATION_SERVER", nd)          
#Loop in array of servers                                                
  for i in a:                                                            
   sn = i[0:i.find("(")]                                                 
   l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + sn)    
   print "SDK for " + sn + " is " + l                                    
   wlog(nd + "," + sn + "," + l[-9:-3])                                  
  s = "nodeagent"                                                        
  if (nd[4:5] == "1" or nd[4:5] == "2"):                                 
   l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + s)     
   print "SDK for " + s + " is " + l                                     
   wlog(nd + "," + s + "," + l[-9:-3])                                   
  s = "dmgr"                                                             
  if (nd[4:5] == "0"):                                                   
   l=AdminTask.getServerSDK('-nodeName ' + nd + ' -serverName ' + s)     
   print "SDK for " + s + " is " + l                                     
   wlog(nd + "," + s + "," + l[-9:-3])                                   
                                                                         
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
                                                              
def getSdkForNode(nd):                                        
#Query current SDK for nodes                                  
  wsdk = AdminTask.getNodeDefaultSDK('-nodeName ' + nd )      
  print "Default SDK for " + nd + ":" + wsdk                  
  wlog(nd + "," + nd + "," + wsdk[-9:-3])                     
                                                              
#Query the current settings for servers and nodes             
b = getIDs()                                                  
for i in b.split(" "):                                        
 if (i != ""):                                                
  getAS(i)                                                    
  getSdkForNode(i)                                            
                                                              
#AdminConfig.save()                                           
