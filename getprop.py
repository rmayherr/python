import sys                                                                
#nodeName=AdminControl.getNode()                                          
#print AdminConfig.types()                                                
listDest=AdminTask.listSIBDestinations('-bus PrintServiceBus').split()    
for i in listDest:                                                        
  print "show attributes xml path for " + i                               
  fileName=i.split('#')                                                   
  fileName=fileName[1]                                                    
  fileName=fileName[:len(fileName)-1]                                     
# print fileName                                                          
  filePath="/u/hu73696/p/" + fileName                                     
# print filePath                                                          
  attrList=AdminConfig.showall(i)                                         
  file=open(filePath,'w')                                                 
  file.write(attrList)                                                    
  file.close()                                                            
# print AdminConfig.showAttribute(i, 'identifier')                        
# print "#################### END ########################"               
