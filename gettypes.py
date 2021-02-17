print AdminConfig.types() - get the types of resources
listDest=AdminTask.listSIBDestinations('-bus PrintServiceBus').split() #list the xml           
 for i in listDest:                                                                             
   print "show attributes xml path for " + i                                                    
   print AdminConfig.showall(i)  # show detailed information about bus
   print AdminConfig.showAttribute(i,'identifier') #show the identifier in the specific xml's property                                                               
   print "show attributes xml path for " + i
   fileName=i.split('#')                    
   fileName=fileName[1]                     
   fileName=fileName[:len(fileName)-1]      
   print fileName                           
   filePath="/u/hu73696/p/" + fileName      
   print filePath                           
   attrList=AdminConfig.showall(i)          
   file=open(filePath,'w')                  
   file.write(attrList)                     
   file.close()                             
   print "#################### END ########################"                                    


---
AdminTask.createSIBDestination('[-bus PrintServiceBus -name Archive806DestinationTest -type Queue -reliability ASSURED_PERSISTENT -description -node wasgqn01 -server sgq0101 ]')
AdminTask.listSIBDestinations('[-bus PrintServiceBus ]') 
