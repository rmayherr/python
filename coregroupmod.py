#Get cellname
cn=AdminConfig.showAttribute(AdminConfig.list('Cell').split()[0], 'name')
#Get CoregroupName
cgn=AdminTask.getDefaultCoreGroupName()
#Get Coregroup xml file
cgxml=AdminConfig.getid('/Cell:'+cn+'/CoreGroup:'+cgn+'/')
#Modify core group configuration
AdminConfig.modify(cgxml,'[[numCoordinators "2"]]')
#Save settings
AdminConfig.save()