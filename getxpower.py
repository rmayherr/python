# Print singleton RWW server webcontainer properties                 
def listWebContainer():                                              
  serverArr = ["xxxxxxxx", "yyyyyyy"]                               
  for as in serverArr:                                               
    server = AdminConfig.getid('/Server: ' + as + ' /')              
   #print xml file by as                                             
   #print "serverid: " + server                                      
    wc = AdminConfig.list('WebContainer',server)                     
    props = AdminConfig.showAttribute(wc, 'properties').split()      
    print "Show Webcontainer attributes of " + as                    
    print "\n"                                                       
    for prop in props:                                               
      print prop                                                     
    print "\n"                                                       
                                                                     
listWebContainer()                                                   

