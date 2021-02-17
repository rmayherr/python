import os,sys
#Path for properties, don't forget / at the end of path 
WDIR="/MyThinClient/websrvprops/"
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

def setWWW(nd):                                                           
  print "Setting webservers on node " + nd                                          
#Look for servers on node, get the xml files of specific servers                                                
  a=AdminServerManagement.listServers("WEB_SERVER", nd)          
#Loop in array of servers                                                
  for i in a:                                                            
#Get the name  by cutting long filename before "("
   sn = i[0:i.find("(")]                                    
   try:
    S=WDIR + sn + ".props"
    print "Setting " + sn + " webserver settings from " + S
    AdminTask.applyConfigProperties('-propertiesFileName ' + S)
   except:
    print "There is no property file for " + sn + ".Skipping..."
   else:
    print "done."  
#Query the current settings for servers and nodes             
b = getIDs()                                                  
for i in b.split(" "):                                        
 if (i != ""):                                                
  setWWW(i)                                                    
                                                              
AdminConfig.save()     
