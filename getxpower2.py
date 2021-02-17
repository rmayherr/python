# Print Webcontainer properties                                           
def listWebContainer():                                                   
  sname = []                                                              
  cells = AdminConfig.list('Cell').split()                                
  for cell in cells:                                                      
    nodes = AdminConfig.list('Node', cell).split()                        
    for node in nodes:                                                    
      cname = AdminConfig.showAttribute(cell, 'name')                     
      nname = AdminConfig.showAttribute(node, 'name')                     
      servs = AdminControl.queryNames('type=Server,cell=' + cname +       
        ',node=' + nname + ',*').split()                                  
      for server in servs:                                                
        sname.append(AdminControl.getAttribute(server, 'name'))           
    #Removing nodeagent word from the list                                
    sname.remove('nodeagent')                                             
  for as in sname:                                                        
   server = AdminConfig.getid('/Server: ' + as + ' /')                    
   #print xml file by as                                                  
   #print "serverid: " + server                                           
   wc = AdminConfig.list('WebContainer',server)                           
   props = AdminConfig.showAttribute(wc, 'properties').split()            
   print "Show Webcontainer attributes of " + as                          
   print "----------------------------------------"                       
   print "\n"                                                             
   for prop in props:                                                     
     print prop                                                           
   print "\n"                                                             
                                                                          
listWebContainer()                                                        
