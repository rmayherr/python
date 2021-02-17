import os,sys                                                             
                                                                          
#filename with absolute path                                              
WF = "/tmp/SDKsettings.txt"                                               
                                                                          
def restoreServers():                                                     
 try:                                                                     
   f = open(WF,"r")                                                       
   l = f.readline()                                                       
   while l:                                                               
    w =l.split(",")                                                       
    print "Restore server " + w[1] + " on node " + w[0] +\                
     "with SDK " + w[2]                                                   
    AdminTask.setServerSDK('-nodeName ' +w[0]+ ' -serverName ' +w[1]+\    
    '  -sdkName  ' + w[2])                                                   
    l = f.readline()                                                      
 finally:                                                                 
   f.close()                                                              
                                                                          
restoreServers()                                                          

