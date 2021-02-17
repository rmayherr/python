import os,sys
#Path for properties, don't forget / at the end of path 
WDIR="/tmp/websrvprops/"
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

def getWWW(nd):                                                           
  print "Querying webservers on node " + nd                                          
#Look for webservers on node, get the specific xml files
  a=AdminServerManagement.listServers("WEB_SERVER", nd)          
#Loop in array of servers                                                
  for i in a:                                                            
#Get the name  by cutting long filename before "("
   sn = i[0:i.find("(")]        
#Extract properties to ASCII file
   try:
    S=WDIR + sn + ".props"
    print "Extracting " + sn + " webserver settings to " + S
#    AdminTask.extractConfigProperties('-propertiesFileName ' + S + ' -configData Server=' + sn)
    AdminTask.extractConfigProperties('-propertiesFileName ' + S + ' -configData Server=' + sn + ' -filterMechanism All')
   except:
    print sys.exc_info()[0], sys.exc_info()[1]                            
    sys.exit(8)  
   else:
    print "done."
#Query webserver on nodes       
b = getIDs()                                                  
for i in b.split(" "):                                        
 if (i != ""):                                                
  getWWW(i)       


