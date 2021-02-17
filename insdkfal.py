import os,sys                                                          
                                                                       
#filename with absolute path where the data is read from               
#be of aware of that content must be in ASCII!!!                       
WF ="/tmp/SDKsettings.txt"                                             
                                                                       
def restoreServers():                                                  
 try:                                                                  
#Open file for read                                                    
   f = open(WF,"r")                                                    
#read by lines                                                         
   l = f.readline()                                                    
#read until EOF                                                        
   while l:                                                            
    w =l.split(",")                                                    
#Check whether node default should be set                              
    if (w[0].strip() == w[1].strip()):                                 
     print "Restore node default on " + w[0].strip() + " with SDK " \  
     + w[2].strip()                                                    
     AdminTask.setNodeDefaultSDK('-nodeName ' + w[0].strip() \         
     + ' -sdkName ' + w[2].strip())                                    
#Set servers with specific SDK                                         
    else:                                                              
     print "Restore server " + w[1].strip() + " on node " \            
     + w[0].strip() + " with SDK " + w[2].strip()                      
     AdminTask.setServerSDK('-nodeName ' + w[0].strip() + \            
     ' -serverName ' + w[1].strip() + ' -sdkName ' + w[2].strip())     
    l = f.readline()                                                   
 except:                                                               
   print sys.exc_info()[0], sys.exc_info()[1]                          
   sys.exit(8)                                                         
 else:                                                                 
   f.close()                                                           
                                                                       
restoreServers()                                                       
#AdminConfig.save()                                                    
