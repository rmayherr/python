#Query xml of clusters
WDIR="/MyThinClient/websrvprops/"
def wlog(t):                                                             
 try:                                                                    
  f = open(WDIR+'cluster.txt',"a")                                                       
  f.write(t)                                                             
  f.write("\n")                                                          
  f.close()                                                              
 except:                                                                 
   print sys.exc_info()[0], sys.exc_info()[1]                            
   sys.exit(8)                                                           
 else:                                                                   
   f.close()     
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
def func1():
	a=AdminClusterManagement.listClusters()
	for i in a:
	 sn = i[0:i.find("(")] 
	 S=WDIR+sn+".props"
	 try:
	  print "Extract " + sn + " to " + S
	  #AdminTask.extractConfigProperties('-propertiesFileName ' + S + ' -configData ServerCluster=' + sn + ' -filterMechanism  SELECTED_SUBTYPES -selectedSubTypes WebserverPluginSettings')
	 except:
	  print sys.exc_info()[0], sys.exc_info()[1] 
	 else:
	  print "done."
def func2():
	a=AdminClusterManagement.listClusters()
	for i in a:
		wlog(AdminConfig.showall(i))
def func3():
	b = getIDs()                                                  
	for i in b.split(" "):                                        
		if (i != ""):                                                
  		 	a=AdminServerManagement.listServers("WEB_SERVER", i)  
			for j in a:
				#print "servername " + j
				c=AdminConfig.show(j,'components')
				c=c[13:]
				c=c[:len(c)-2]
				p=AdminConfig.show(c,'pluginProperties')
				p=p[20:]
				p=p[:len(p)-2]
				p='pluginProperties('+p				
				q=AdminConfig.show(p,'pluginServerClusterProperties')
				q=q[1:]
				q=q[:-1]
				AdminConfig.show(q)
def func4():
	a=AdminClusterManagement.listClusters()
	for i in a:	
		sn = i[0:i.find("(")] 		
		print "servername " + sn
		o=AdminConfig.show(i,'clusterAddressProperties') 	
		o=o[1:]
		o=o[1:len(o)-1] 
		print " property xml " + o
		print AdminConfig.show(o)
def func5():
	a=AdminClusterManagement.listClusters()
	for i in a:		
#		w=AdminConfig.show(i,'clusterAddressProperties') 	
		w=AdminConfig.show(i,'clusterAddressEndPoints') 	
		print "clusterAddressEndPoints " + w
 		w=w[26:]
		w=w[:len(w)-2] 
		print " property xml " + w
		print AdminConfig.show(w)		
		#AdminConfig.modify(w,[['keyring', 'safkeyring:///ringname']])
def func6():
	a=AdminClusterManagement.listClusters()
	for i in a:
#show top level attributes			
		print AdminConfig.show(i) 
def func7():
	a=AdminClusterManagement.listClusters()
	for i in a:
#show xml of clusterAddressProperties
		print AdminConfig.showAttribute(i,'clusterAddressProperties') 
def func8():
	a=AdminClusterManagement.listClusters()
	for i in a:		
		w=AdminConfig.show(i,'clusterAddressEndPoints') 	
		print "clusterAddressEndPoints " + w
 		w=w[26:]
		w=w[:len(w)-2] 
		print " property xml " + w
		AdminConfig.modify(w,[['keyring', 'safkeyring:///ringname'],['stashfile','']])
def func9():
	b = getIDs()                                                  
	for i in b.split(" "):                                        
		if (i != ""):                                                
  		 	a=AdminServerManagement.listServers("WEB_SERVER", i)  
			for j in a:
				#print "servername " + j
				print AdminConfig.showall(j)
def func10():
	#List servers xmls
	#nd = AdminConfig.getid('/Node:nodea/Server:/')
	#List a specific server's xml
	s = AdminConfig.getid('/Node:nodea/Server:???os/')	
	#b=getIDs()
	#for i in b.split(" "):
	#	if (i != ""):
	a=AdminConfig.list('PluginProperties',s)
	b=AdminConfig.show(a)
	print b
def func11():
	s=AdminConfig.getid('/Node:nodea/Server:??os/')
	a=AdminConfig.list('pluginServerClusterProperties',s)
	b=AdminConfig.show(a)
	print b
def func12():
	s=AdminConfig.getid('/Node:nodea/Server:ihszos/')
	c=AdminConfig.show(s,'components')
	#print c
	#Cut xml from the list
	#[components [??os(cells/??????????ebServer_1553785373470)]]
	arr=c.split("[")
	r=arr[2]
	d=AdminConfig.show(r[:len(r)-2], 'server')
	arr2=d.split("[")
	s=arr[2]
	w=AdminConfig.show(s[:len(s)-2],'stateManagement')
	w=w[:len(w)-1]
	w=w[1:]
	x=AdminConfig.show(w,'managedObject')
	x=x[1:]
	x=x[:len(x)-1]
	print AdminConfig.show(x)
def func13():
	#Query ihs* xml files
 	#p=AdminConfig.list('Server','ihs*')
	#print AdminConfig.showAttribute(p,'*')
	#AdminConfig.getid('/Cell:/Node:/Server:/ApplicationServer:/WebContainer:/SessionManager:/')
	id=AdminConfig.getid('/Node:nodea/Server:???os/')
	print id
	#print AdminConfig.showAttribute(id,'name')
def func14():
	AdminTask.extractConfigProperties('-interactive')
func13()
func14()
AdminConfig.save()
