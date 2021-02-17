apps = AdminApp.list()                       
appslist = apps.split("\n")                  
pathofapps = '/u/hu73696/tmp/'               
for i in appslist:                           
  result = pathofapps + i + ".ear"           
  AdminApp.export( i, result)                
  print("Exporting ",i," to ",result)        
