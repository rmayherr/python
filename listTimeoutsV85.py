#-------------------------------------------------------------------------
# (C) COPYRIGHT International Business Machines Corp., 2015
#
# BY ACCESSING AND/OR USING THE SAMPLE FILE(S) PROVIDED, YOU ACKNOWLEDGE
# THAT YOU HAVE READ, UNDERSTOOD, AND AGREE, TO BE BOUND BY THESE TERMS.
# YOU AGREE TO THE BINDING NATURE OF THESE ENGLISH LANGUAGE TERMS AND
# CONDITIONS REGARDLESS OF LOCAL LANGUAGE RESTRICTIONS.  IF YOU DO NOT AGREE
# TO THESE TERMS, DO NOT USE THE FILE.  INTERNATIONAL BUSINESS MACHINES
# CORPORATION PROVIDES THESE SAMPLE FILES ON AN "AS IS" BASIS AND IBM
# DISCLAIMS ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED
# TO, THE WARRANTY OF NON-INFRINGEMENT AND THE IMPLIED WARRANTIES OF
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE.  YOU MAY COPY,
# MODIFY, AND DISTRIBUTE THESE SAMPLE FILES IN ANY PROGRAMS IN ANY FORM
# WITHOUT PAYMENT TO IBM.  THESE SAMPLE FILES HAVE NOT BEEN THOROUGHLY
# TESTED, THEREFORE, IBM CANNOT GUARANTEE NOR DOES IT IMPLY RELIABILITY,
# SERVICEABILITY OR FUNCTION OF THESE SAMPLE FILES; IBM SHALL NOT BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL OR CONSEQUENTIAL DAMAGES
# ARISING OUT OF THE USE OR OPERATION OF THIS SOFTWARE.  IBM HAS NO
# OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS OR
# MODIFICATIONS TO THE SAMPLE FILES PROVIDED.
#-------------------------------------------------------------------------
#
# File:    listTimeoutsV85.py WebSphere for z/OS V8.5 timeouts analysis script.
# Purpose: List timeout values associated with a server or all servers in a cell.
#          Report any mismatches between relative timeout values.
#          Identify if any useful properties are not being used.
#
# Timeout comparisons currently checked are:
#   Maximum transaction timeout >= Transaction timeout (Total transaction timeout)
#   Transaction timeout > Client inactivity timeout.
#   ORB request timeout > WLM timeout.
#   WLM timeout > Maximum transaction timeout.
#   MDB timeout > Maximum transaction timeout.
#   SIP/S protocol timeout > Maximum transaction timeout.
#   Transaction timeout > Non ASF receive timeout.
#   HTTP/S protocol timeout > Maximum transaction timeout.
#   WLM timeout > V4 DataSource orphan timeout.
#   MDB timeout > V4 DataSource orphan timeout.
#   HTTP/S protocol timeout > V4 DataSource orphan timeout.
#   Transaction timeout > Connection Factory connection timeout.
#   Connection Factory aged timeout > Connection Factory reap time.
#   Connection Factory unused timeout > Connection Factory reap time.
#   Connection Factory unused timeout not 0
# Checks related to avoiding timeouts or related failures:
#   Warns if a WLM classification XML file is being used. (Properties my be overridden there.)
#   Checks that queue_percent_timeouts are being used
#   Checks that stalled thread threshold is being used
#   Checks if control_region_dreg_on_no_srs or control_region_save_last_servant are used
#   If stalled thread threshold is used, checks protocol_http_output_recovery=SERVANT
#   Checks that http and iiop requests are not accepted until min servants are started
#   Checks whether HTTP re-queue is enabled
#   Checks that the cputimeused value is reasonable
#   Checks several datasource custom properties related to timeouts
#    and any invalid interdependencies between them or datasource type.
#   For T4 datasources ...
#      Recommends enableSysplex WLB for T4 datasources
#      If enableSysplexWLB is set suggests different connection pool timeouts
#      Suggests unusedTimeout is set to 50% of default firewall idle timeout.
#      Suggests minConnections = 0 for T4 datasources.
# For ActivationSpecs and WMQ connection factories ...
#    Checks for CLIENT or BINDINGS AND CLIENT mode that Connect_Timeout is set as JVM custom property.
# For WMQ Resource Adapters ...
#    Checks that start-up and reconnect counts and timeouts are set.
#    Warns if the values of start-up and reconnect timeouts are different.
# Added check for new ME properties in WP102450 if the server has MEs.
# adjunct_region_start_synchronized default 0/false
# adjunct_region_start_sib_waittime default 300 secs
# adjunct_region_start_sib_abend    default 0/false
# synchWithControlRegion (default false)  Scheduler custom property.
# sib.property.isMECritical default 0/false) SIB custom property.
# Verbose now reports on many more timeout-related properties
#
# Usage: wsadmin
#          -host <HostName>
#          -port (HostPort>
#          -lang jython
#          -f listTimeoutsV85.py
#          <Scope>
#          <verbose>
#
#   <HostName>   : Host name of the application server (base) or Deployment Maneger (ND).
#   <HostPort>   : SOAP port of the application server (base) or Deployment Maneger (ND).
#   <Scope>      : Cluster or server long name, or "all" for all clusters in the cell.
#   <Verbose>    : Optional character string (any content) to report all timeout
#                  values in addition to the compared value mismatches.
#
# Change control:
#   15/02/2006 R Heald.  First version for WAS V5.1. Published in Techdoc WP100738 (now withdrawn)
#   02/01/2015 K Senior. Substantial update for WAS V8.5 and support for cluster scope.
#   28/04/2015 K Senior. Fix to ORB connectTimeout processing.
#   28/04/2015 K Senior. Add processing of node-scoped WebSphere variables
#
import sys
#----------------------------------------------------------------------
# checkServer routine: Process a server
#----------------------------------------------------------------------
def checkServer( currentCluster, currentServer , checkScope ):

   global AdminConfig
   global errorOccurred
   global propertyMap
   global allV4Factories
   global allV8Factories
   global allRAs
   global allSIBs

#
# Extract the cell and node names for the server
#
   serverId = AdminConfig.getid("/Server:" + currentServer + "/")

   nameBits = serverId.split("/")
   for i in range(len(nameBits)):
      if nameBits[i].endswith("cells"):
#        Next one is the cell name
         currentCell = nameBits[i + 1]
      if nameBits[i] == "nodes":
#        Next one is the node name
         currentNode = nameBits[i + 1]

   print "   Cell is " + currentCell
   cellId = AdminConfig.getid("/Cell:" + currentCell + "/")
   print "   Node is " + currentNode
   nodeId = AdminConfig.getid("/Node:" + currentNode + "/")

#  In case a server name rather than cluster name was passed, check the server exists ...
   if checkScope == 'server':
      if serverId == "":
         print "   Server name: " + currentServer + " not found."
         errorOccurred = 1
         return
      else:
         print "\n   Checking server " + currentServer + " on node " + currentNode + ' ...'

#
# Initialize table of properties
#
   propertyMap = {}

#
# Search for timeout-related properties that are in the envvarlist array.
# For each property in envvarlist, the a property map is created which
# has the name of the property and contains 3 attributes:
# [value] [measurement unit] [default flag]
# In the 'for' loop below, each property map is initially created with
# the [value] set to the default value coded in the envvarlist.
# Then we searche for the property at various scopes in WAS.
# If the property exists with a value, the [value] in the property map
# is replaced with the value which is set and the [default flag] is removed.
# Issuing 'getProperty' then testing propertyName[3] for '1' (default)
# will show if the property has not been defined to WAS.
#
   if verboseFlag != "false":
      print "\n   Obtaining WebSphere environment variables related to time-outs."
#
   for i in range(len(envvarlist)):
       varx = envvarlist[i][0]
       defx = envvarlist[i][1]
       unitx = envvarlist[i][2]
       # Set the property with the default values to start with
       setProperty(varx, defx, unitx, '', 'default')
       # Now try to list the property in WAS env variables ...
       # Check in order of increasing granularity.
       # A variable at Node scope overrides cell scope.
       # A variable at Cluster scope overrides cell and node scope.
       # A variable at Server scope overrides cell, node and cluster scope.
       # First see if property is set at cell scope ...
       listargs  = "[ -variableName " + varx + " -scope Cell=" + currentCell + "]"
       varxCellValue = AdminTask.showVariables ( listargs )
       if varxCellValue:
          varScope = "Scope: Cell=" + currentCell
          setProperty( varx, varxCellValue, unitx, varScope)
       # Next see if property is also set at node scope and use this value if set ...
       listargs  = "[ -variableName " + varx + " -scope Node=" + currentNode + " ]"
       varxNodeValue = AdminTask.showVariables ( listargs )
       if varxNodeValue:
          varScope = "Scope: Node=" + currentNode
          setProperty( varx, varxNodeValue, unitx, varScope)
       # If targetScope is cluster,  see if property is set at cluster scope and use this value if set ...
       if checkScope == 'cluster':
          listargs  = "[ -variableName " + varx + " -scope Cluster=" + currentCluster + "]"
          varxClusterValue = AdminTask.showVariables ( listargs )
          if varxClusterValue:
             varScope = "Scope: Cluster=" + currentCluster
             setProperty( varx, varxClusterValue, unitx, varScope)
       # Next see if property is also set at server scope and use this value if set ...
       listargs  = "[ -variableName " + varx + " -scope Node=" + currentNode + ",Server=" + currentServer + " ]"
       varxServerValue = AdminTask.showVariables ( listargs )
       if varxServerValue:
          varScope = "Scope: Server=" + currentServer
          setProperty( varx, varxServerValue, unitx, varScope)

       # Print the property with its current value. (if verbose is set)
       printProperty(varx)
   #endfor
#
# Extract transaction service properties
#
   setProperty("clientInactivityTimeout", 60, "s", "", "default")
   setProperty("transaction_defaultTimeout", 120, "s", "", "default")
   setProperty("transaction_maximumTimeout", 300, "s", "", "default")

   transactionService = AdminConfig.list("TransactionService", serverId)
   propertyValue = AdminConfig.showAttribute(transactionService,"clientInactivityTimeout")
   setProperty("clientInactivityTimeout", propertyValue, "s", "(Server transaction service settings)")
   propertyValue = AdminConfig.showAttribute(transactionService,"totalTranLifetimeTimeout")
   setProperty("transaction_defaultTimeout", propertyValue, "s", "(Server transaction service settings)")
   propertyValue = AdminConfig.showAttribute(transactionService,"propogatedOrBMTTranLifetimeTimeout")
   setProperty("transaction_maximumTimeout", propertyValue, "s", "(Server transaction service settings)")

#
# Extract ORB service properties
#
   setProperty("com.ibm.CORBA.ConnectTimeout", 10, "s", "", "default")
   setProperty("com.ibm.CORBA.RequestTimeout", 180, "s", "", "default")
   setProperty("control_region_wlm_dispatch_timeout", 1200, "s", "", "default")

   currentOrb = AdminConfig.list("ObjectRequestBroker", serverId)
   orbProperties = AdminConfig.list("Property", currentOrb).split(lineSeparator)
   # com.ibm.CORBA.ConnectTimeout is not defined as a custom property by default.
   # Look for it anyway and get the value if it is present.
   for orbProperty in orbProperties:
       if (AdminConfig.showAttribute(orbProperty, "name") == 'com.ibm.CORBA.ConnectTimeout'):
          propertyValue = AdminConfig.showAttribute(orbProperty, "value")
          setProperty("com.ibm.CORBA.ConnectTimeout", propertyValue, "s", "(Server ORB custom property)")
       if (AdminConfig.showAttribute(orbProperty, "name") == "was.wlmTimeout"):
          propertyValue = AdminConfig.showAttribute(orbProperty, "value")
          setProperty("control_region_wlm_dispatch_timeout", propertyValue, "s", "(Server ORB service settings)")
          break
   # requestTimeout is an ORB attribute so get the value directly from the currentOrb ...
   propertyValue = AdminConfig.showAttribute(currentOrb, "requestTimeout")
   setProperty("com.ibm.CORBA.RequestTimeout", propertyValue, "s", "(Server ORB service settings)")

   allProperties = AdminConfig.list("Property", serverId).split(lineSeparator)
#
#  for thisProperty in allProperties:
#     if AdminConfig.showAttribute(thisProperty, "name") == "was.wlmTimeout":
#        propertyValue = AdminConfig.showAttribute(thisProperty, "value")
#        setProperty("control_region_wlm_dispatch_timeout", propertyValue, "s", "(Server ORB service settings)")

#
# Extract messaging timeouts
# Use the collection of properties which were obtained for the ORB service report
#
   setProperty("control_region_mdb_request_timeout", 120, "s", "", "default")
   setProperty("com.ibm.mq.cfg.TCP.Connect_Timeout", 0, "s", "", "default")
   setProperty("com.ibm.msg.client.config.location", "", "", "", "default")

   for thisProperty in allProperties:
      if AdminConfig.showAttribute(thisProperty, "name") == "control_region_mdb_request_timeout":
         propertyValue = AdminConfig.showAttribute(thisProperty, "value")
         setProperty("control_region_mdb_request_timeout", propertyValue, "s", varScope)
      if AdminConfig.showAttribute(thisProperty, "name") == "NON.ASF.RECEIVE.TIMEOUT":
         propertyValue = AdminConfig.showAttribute(thisProperty, "value")
         setProperty("NON.ASF.RECEIVE.TIMEOUT", propertyValue, "ms", "Message Listener custom property")

   # Find if servant JVM com.ibm.mq.cfg.TCP.Connect_Timeout or com.ibm.msg.client.config.location are set ...
   processIdList = AdminConfig.list('ProcessDef', serverId).split("\n")
   for processId in processIdList:
      if (processId != ""):
         if AdminConfig.showAttribute(processId, 'processType') == "Servant":
            jvmList = AdminConfig.list('JavaVirtualMachine', processId).split("\n")
         continue
   for jvmId in jvmList:
      #  we now have the correct jvm .. get the properties ...
      jvmPropertyList = AdminConfig.showAttribute(jvmId, "systemProperties")[1:-1].split(" ")
      if (jvmPropertyList != ['']):
             for entry in jvmPropertyList:
                entryName = AdminConfig.showAttribute(entry, "name")
                if (entryName == "com.ibm.mq.cfg.TCP.Connect_Timeout"):
                   jvmPropertyValue = AdminConfig.showAttribute(entry, "value")
                   setProperty("com.ibm.mq.cfg.TCP.Connect_Timeout", jvmPropertyValue, "s", "Servant JVM custom property")
                if (entryName == "com.ibm.msg.client.config.location"):
                   jvmPropertyValue = AdminConfig.showAttribute(entry, "value")
                   setProperty("com.ibm.msg.client.config.location", jvmPropertyValue, "", "Servant JVM custom property")
#
#--------------------------------------------------------------------------------------------------------------------------
# Process server properties ...
#--------------------------------------------------------------------------------------------------------------------------
#
# Check if a WLM classification XML file is being used.
# Timeout properties may be overriding values set as environment variables.
#
   wlmXMLValue = getProperty("wlm_classification_file")[0]
   if wlmXMLValue:
      print "\n   WARNING: A WLM classification XML file is being used from the following path:"
      print "            " + wlmXMLValue
      print "            Timeout properties may have been overridden in that file and this"
      print "            script is not able to take those overrides into account."
#
# Transaction service property checks ...
#
   print "\n   " + currentServer + " Transaction Service time-out checks ..."
   warning = 'n'

   transactionMaximumTimeoutValue = int(getProperty("transaction_maximumTimeout")[0])
   transactionDefaultTimeoutValue = int(getProperty("transaction_defaultTimeout")[0])
   clientInactivityTimeoutValue = int(getProperty("clientInactivityTimeout")[0])

   printProperty("transaction_maximumTimeout")

   printProperty("transaction_defaultTimeout")
   if transactionMaximumTimeoutValue > 0:
      if transactionMaximumTimeoutValue < transactionDefaultTimeoutValue:
         warning = 'y'
         print "         WARNING: transaction_defaultTimeout should not be greater than transaction_maximumTimeout (" + str(transactionMaximumTimeoutValue) + ")"
      if transactionDefaultTimeoutValue == 0:
         warning = 'y'
         print "         WARNING: transaction_defaultTimeout disabled when transaction_maximumTimeout (" + str(transactionMaximumTimeoutValue) + ") is active"

   printProperty("clientInactivityTimeout")
   if clientInactivityTimeoutValue == 0:
      warning = 'y'
      print "         WARNING: clientInactivityTimeout = 0 which means this timeout is disabled."
      print "                  Usually the clientInactivityTimeout is best set to a value less than transaction_defaultTimeout (" + str(transactionDefaultTimeoutValue) + ") secs."

   if clientInactivityTimeoutValue > 0:
      if  (transactionDefaultTimeoutValue > 0) and (clientInactivityTimeoutValue >= transactionDefaultTimeoutValue):
         warning = 'y'
         print "         WARNING: clientInactivityTimeout should be less than transaction_defaultTimeout (" + str(transactionDefaultTimeoutValue) + ")"

   if warning == 'n':
      print "   " + currentServer + " Transaction Service time-out checks ended with no warnings."
#
# ORB properties
# Note: The ORB properties should not be set as environment variables.
# They are ignored if set as environment variables.
#
   print "\n   " + currentServer + " ORB Service time-out checks ..."
   warning = 'n'

   iiopConnectTimeout = getProperty("com.ibm.CORBA.ConnectTimeout")
   iiopConnectTimeoutValue = int(iiopConnectTimeout[0])
   printProperty("com.ibm.CORBA.ConnectTimeout")
   #
   iiopRequestTimeout = getProperty("com.ibm.CORBA.RequestTimeout")
   iiopRequestTimeoutValue = int(iiopRequestTimeout[0])
   printProperty("com.ibm.CORBA.RequestTimeout")
   #
   controlRegionWlmDispatchTimeout = getProperty("control_region_wlm_dispatch_timeout")
   controlRegionWlmDispatchTimeoutValue = int(controlRegionWlmDispatchTimeout[0])
   printProperty("control_region_wlm_dispatch_timeout")
   #
   protocolAcceptIiopWork = getProperty("protocol_accept_iiop_work_after_min_srs")


   if iiopConnectTimeoutValue == 0:
      warning = 'y'
      print "         WARNING: com.ibm.CORBA.ConnectTimeout = 0 which means there is no timeout for connection"
      print "                  requests to remote ORBs. If applications are making RMI/IIOP calls to applications in"
      print "                  remote servers, it is a good idea to set com.ibm.CORBA.ConnectTimeout."
   if iiopRequestTimeoutValue == 0:
      warning = 'y'
      print "         WARNING: com.ibm.CORBA.RequestTimeout = 0 which means there is no timeout for RMI/IIOP requests"
      print "                  to remote ORBs. If applications are making RMI/IIOP calls to applications in"
      print "                  remote servers, it is a good idea to set com.ibm.CORBA.RequestTimeout."
   if iiopRequestTimeoutValue >  transactionDefaultTimeoutValue:
      warning = 'y'
      print "         WARNING: com.ibm.CORBA.RequestTimeout (" + str(iiopRequestTimeoutValue) + ") is greater than the transaction_defaultTimeout (" + str(transactionDefaultTimeoutValue) + ")."
      print "                  If applications are making RMI/IIOP calls to other applications in this server then "
      print "                  com.ibm.CORBA.RequestTimeout should be less than the transaction_defaultTimeout."
   if controlRegionWlmDispatchTimeoutValue == 0:
      warning = 'y'
      print "         WARNING: control_region_wlm_dispatch_timeout = 0 which means there is no timeout for IIOP requests."
      print "                  control_region_wlm_dispatch_timeout should be set in order to a avoid that threads hang forever."
   if controlRegionWlmDispatchTimeoutValue > 0:
      if (iiopConnectTimeoutValue > 0) and (iiopConnectTimeoutValue >= controlRegionWlmDispatchTimeoutValue):
         warning = 'y'
         print "         WARNING: If applications are making RMI/IIOP calls to other applications in this server then "
         print "                  com.ibm.CORBA.ConnectTimeout (" + str(iiopConnectTimeoutValue) + ") should be less than"
         print "                  control_region_wlm_dispatch_timeout(" + str(controlRegionWlmDispatchTimeoutValue) + ")"
      if (iiopRequestTimeoutValue > 0) and (iiopRequestTimeoutValue >= controlRegionWlmDispatchTimeoutValue):
         warning = 'y'
         print "         WARNING: If applications are making RMI/IIOP calls to other applications in this server then "
         print "                  com.ibm.CORBA.RequestTimeout (" + str(iiopRequestTimeoutValue) + ") should be less than"
         print "                  control_region_wlm_dispatch_timeout(" + str(controlRegionWlmDispatchTimeoutValue) + ")"
      if (transactionMaximumTimeoutValue > 0) and (transactionMaximumTimeoutValue >= controlRegionWlmDispatchTimeoutValue):
         warning = 'y'
         print "         WARNING: control_region_wlm_dispatch_timeout should be greater than transaction_maximumTimeout (" + str(transactionMaximumTimeoutValue) + ")"
# Check that the queue_percent_timeout is reasonable ...
   qptwarning = checkQueuePercentTimeout( "iiop" )

# Check that IIOP requests are not allowed in until min servants are active ...
   if protocolAcceptIiopWork:
#     Check this is defaulting or set to 1 or true ...
      print " "
      printProperty("protocol_accept_iiop_work_after_min_srs")
      protocolAcceptIiopWorkValue = str(protocolAcceptIiopWork[0])
      if protocolAcceptIiopWork[3] != 1:
         #  The property is set so check it has a good value ...
         if (protocolAcceptIiopWorkValue == '0') or (protocolAcceptIiopWorkValue == 'false'):
            warning = 'y'
            print "         WARNING: protocol_accept_iiop_work_after_min_srs = 1 or 'true' is recommended"
            print "                  to avoid requests queuing to run before servants are initialized."
      #  Else: The property is not set but the default is good so no need for any warnings.

   if (warning == 'n') and (qptwarning == 'n'):
      print "   " + currentServer + " ORB Service time-out checks ended with no warnings."
#
# Messaging properties
#
   print "\n   " + currentServer + " messaging time-out checks ..."
   warning = 'n'

   # Check if there are any listener ports defined.
   # If none, then the MDB timeouts are not relevant anyway ...
   if getListenerPortIds( currentServer ) != '[]':

      controlRegionMdbRequestTimeoutValue = int(getProperty("control_region_mdb_request_timeout")[0])

      nonAsfReceiveTimeout = getProperty("NON.ASF.RECEIVE.TIMEOUT")

      printProperty("control_region_mdb_request_timeout")
      if controlRegionMdbRequestTimeoutValue == 0:
         warning = 'y'
         print "         WARNING: control_region_mdb_request_timeout =0 which means this timeout is disabled and MDB"
         print "                  requests could hang indefinitely."
      if controlRegionMdbRequestTimeoutValue > 0:
         if (transactionMaximumTimeoutValue > 0) and (transactionMaximumTimeoutValue >= controlRegionMdbRequestTimeoutValue):
            warning = 'y'
            print "         WARNING: control_region_mdb_request_timeout should be greater than transaction_maximumTimeout (" + str(transactionMaximumTimeoutValue) + ")"

      if nonAsfReceiveTimeout != None:
   #     Property exists (it has no default value)
         printProperty("NON.ASF.RECEIVE.TIMEOUT")
         nonAsfReceiveTimeoutValue = int(nonAsfReceiveTimeout[0])
         if nonAsfReceiveTimeoutValue > 0:
            if (transactionDefaultTimeoutValue > 0) and (nonAsfReceiveTimeoutValue >= (transactionDefaultTimeoutValue*1000)):
                  warning = 'y'
                  print "         WARNING: NON.ASF.RECEIVE.TIMEOUT should be less than transaction_defaultTimeout (" + str(transactionDefaultTimeoutValue) + ")"
   # Check that the queue_percent_timeout is reasonable ...
      qptwarning = checkQueuePercentTimeout( "mdb" )

   else:
      # If no Listener Ports, check for activationSpecs ...
      aSpecList = AdminConfig.list('J2CActivationSpec').splitlines()
      if aSpecList:
         # If there are any activationSpecs defined, explain which timeouts do apply ...
         print "            INFO: Listener ports are not defined for this server but activationSpec definitions exist."
         print "                  The dispatch timeout of MDBs driven by activationSpecs is determined by property"
         print "                  control_region_wlm_dispatch_timeout = " + str(controlRegionWlmDispatchTimeoutValue) + " (secs)."
         printProperty("com.ibm.mq.cfg.TCP.Connect_Timeout")
         printProperty("com.ibm.msg.client.config.location")
         # List the properties of each activation spec. Find the transPort type are WMQ ...
         for thisAS in aSpecList:
             asName = AdminConfig.showAttribute(thisAS, 'name')
             asProps = AdminConfig.showAttribute(thisAS, 'resourceProperties')[1:-1].split()
             asTransport = ""
             asQmgr = ""
             for asProp in asProps:
                if (AdminConfig.showAttribute(asProp, 'name') == 'transportType'):
                   asTransport = AdminConfig.showAttribute(asProp, 'value')
                if (AdminConfig.showAttribute(asProp, 'name') == 'queueManager'):
                   asQmgr = AdminConfig.showAttribute(asProp, 'value')
             #endfor
             if (asTransport != "") and (asQmgr != ""):
                if (asTransport.find("CLIENT") != -1):
                   # AS is using BINDINGS THEN CLIENT or CLIENT mode ...
                   mqTCPConnectTimeout = getProperty("com.ibm.mq.cfg.TCP.Connect_Timeout")
                   mqClientConfigLocation = getProperty("com.ibm.msg.client.config.location")
                   if (mqTCPConnectTimeout[3] == 1) and (mqClientConfigLocation[3] == 1):
                      # Servant JVM custom property com.ibm.mq.cfg.TCP.Connect_Timeout can be set, or
                      # Connect_Timeout can be set in a properties file referenced by com.ibm.msg.client.config.location.
                      # If neither JVM property is set, issue a warning ...
                      print "         WARNING: ActivationSpec " + asName + " to QMGR " + asQmgr + " is using mode '" + asTransport + "' but"
                      print "                  com.ibm.mq.cfg.TCP.Connect_Timeout is not set as a servant JVM custom property and"
                      print "                  com.ibm.msg.client.config.location does not set a path to a properties file."
                      print "                  This means that no socket connect timeout is set."
                      print "                  For client mode connections, consider setting servant JVM custom property"
                      print "                  com.ibm.mq.cfg.TCP.Connect_Timeout (secs) to a few seconds to avoid hung connect requests."
                   if (mqTCPConnectTimeout[3] == 1) and (mqClientConfigLocation[3] != 1):
                      print "         WARNING: ActivationSpec " + asName + " to QMGR " + asQmgr + " is using mode '" + asTransport + "'."
                      print "                  com.ibm.mq.cfg.TCP.Connect_Timeout is not set as a servant JVM custom property but"
                      print "                  com.ibm.msg.client.config.location specifies a path to a properties file."
                      print "                  Check that the properties file includes a value for Connect_Timeout (secs)."
                      print "                  For client mode connections, setting JVM custom property com.ibm.mq.cfg.TCP.Connect_Timeout"
                      print "                  or setting Connect_Timeout_Timeout in a properties file can prevent hung connect requests."
         #endfor
      #endif
   #  Check the WMQ resource adapters ...
      for thisRA in allRAs:
         raClasspath = AdminConfig.showAttribute(thisRA, 'classpath')
         if thisRA == "":
            # Null entry
            continue
         elif thisRA.find("applications") != -1:
            # Application definition so skip it ...
            continue
         elif raClasspath.find("wmq.jmsra.rar") == -1:
            # Skip over any RAs for SIBs. We want only WMQ RAs ...
            continue
         elif thisRA.find("clusters") != -1:
            # Cluster level definition
            raScope = 'Cluster=' + currentCluster
            if thisRA.find(currentCluster) != -1:
               # Definition for this cluster - process it
               RAwarning = printRA(thisRA, raScope)
               continue
         elif thisRA.find("servers") != -1:
            # Server level definition
            raScope = 'Server=' + currentServer
            if thisRA.find(currentServer) != -1:
               # Definition for this server - process it
               RAwarning = printRA(thisRA, raScope)
               continue
         elif (thisRA.find("nodes") != -1):
            # Node level definition
            if (thisRA.find("servers") == -1):
               # Only process a node level resource if no resource at server scope.
               raScope = 'Node=' + currentNode
               if thisRA.find(currentNode) != -1:
                  # Definition for this node - process it
                  RAwarning = printRA(thisRA, raScope)
                  continue
         else:
            # Cell level definition - process it
            raScope = 'Cell=' + currentCell
            RAwarning = printRA(thisRA, raScope)

      #endfor
   if (warning == 'n') and (qptwarning == 'n') and (RAwarning == 'n'):
      print "   " + currentServer + " Messaging time-out checks ended with no warnings."
#
# HTTP and SIP properties.
#
   print "\n   " + currentServer + " HTTP/HTTPS/SIP/SIPS time-out checks ..."
   warning = 'n'

   httpRequeue = getProperty("control_region_http_requeue_enabled")
   protocolHttpTimeoutOutput = getProperty("protocol_http_timeout_output")
   protocolHttpsTimeoutOutput = getProperty("protocol_https_timeout_output")
   protocolHttpTimeoutRecovery = getProperty("protocol_http_timeout_output_recovery")
   protocolHttpsTimeoutRecovery = getProperty("protocol_https_timeout_output_recovery")
   protocolAcceptHttpWork = getProperty("protocol_accept_http_work_after_min_srs")
   protocolSipTimeoutOutput = getProperty("protocol_sip_timeout_output")
   protocolSipsTimeoutOutput = getProperty("protocol_sips_timeout_output")
   protocolSipTimeoutRecovery = getProperty("protocol_sip_timeout_output_recovery")
   protocolSipsTimeoutRecovery = getProperty("protocol_sips_timeout_output_recovery")
   stalledThreadThreshold = getProperty("server_region_stalled_thread_threshold_percent")
   httpQueueTimeoutPercent = getProperty("control_region_http_queue_timeout_percent")
   httpsQueueTimeoutPercent = getProperty("control_region_https_queue_timeout_percent")
   sipQueueTimeoutPercent = getProperty("control_region_sip_queue_timeout_percent")
   sipsQueueTimeoutPercent = getProperty("control_region_sips_queue_timeout_percent")
   controlRegionDregOnNoSrs= getProperty("control_region_dreg_on_no_srs")
   controlRegionTimeoutSaveLastServant= getProperty("control_region_timeout_save_last_servant")

   if protocolHttpTimeoutOutput:
      protocolHttpTimeoutOutputValue = int(protocolHttpTimeoutOutput[0])
      printProperty("protocol_http_timeout_output")
      if protocolHttpTimeoutOutput[3] != 1:
      #  HTTP protocol timeout is set ...
         if protocolHttpTimeoutOutputValue > 0:
            if transactionMaximumTimeoutValue >= protocolHttpTimeoutOutputValue:
               warning = 'y'
               print "         WARNING: protocol_http_timeout_output (" +  str(protocolHttpTimeoutOutputValue) + ") is less than transaction_maximumTimeout (" + str(transactionMaximumTimeoutValue) + ")"
               print "                  protocol_http_timeout_output should be greater than transaction_maximumTimeout"
         else:
            warning = 'y'
            print "         WARNING: protocol_http_timeout_output should NOT be disabled by setting it to zero"
      else:
         #  HTTP protocol timeout is not set so is defaulting ...
         warning = 'y'
         print "            INFO: protocol_http_timeout_output is not set and is defaulting to " +  str(protocolHttpTimeoutOutputValue) + " secs."

   if protocolHttpsTimeoutOutput:
      protocolHttpsTimeoutOutputValue = int(protocolHttpsTimeoutOutput[0])
      printProperty("protocol_https_timeout_output")
      if protocolHttpsTimeoutOutput[3] != 1:
   #     HTTPS protocol timeout is set ...
         protocolHttpsTimeoutOutputValue = int(protocolHttpsTimeoutOutput[0])
         if protocolHttpsTimeoutOutputValue > 0:
            if (transactionMaximumTimeoutValue > 0) and (transactionMaximumTimeoutValue >= protocolHttpsTimeoutOutputValue):
               warning = 'y'
               print "         WARNING: protocol_https_timeout_output (" + str(protocolHttpsTimeoutOutputValue) + ") is less than transaction_maximumTimeout (" + str(transactionMaximumTimeoutValue) + ")"
               print "         WARNING: protocol_https_timeout_output should be greater than transaction_maximumTimeout (" + str(transactionMaximumTimeoutValue) + ")"
         else:
            warning = 'y'
            print "         WARNING: protocol_https_timeout_output should NOT be disabled by setting it to zero"
      else:
         #  HTTPS protocol timeout is not set so is defaulting ...
         print "            INFO: protocol_https_timeout_output is not set and is defaulting to " +  str(protocolHttpsTimeoutOutputValue) + " secs."

   if protocolHttpTimeoutRecovery:
#     The default is probably being overridden which is not recommended ...
      printProperty("protocol_http_timeout_output_recovery")
      protocolHttpTimeoutRecoveryValue = str(protocolHttpTimeoutRecovery[0])
      if protocolHttpTimeoutRecoveryValue == 'SESSION':
         warning = 'y'
         print "         WARNING: protocol_http_timeout_output_recovery = SESSION is not recommended."
         print "               Instead set to 'SERVANT' (the default) and use the stalled thread threshold."

   if protocolHttpsTimeoutRecovery:
#     The default is probably being overridden which is not recommended ...
      printProperty("protocol_https_timeout_output_recovery")
      protocolHttpsTimeoutRecoveryValue = str(protocolHttpsTimeoutRecovery[0])
      if protocolHttpsTimeoutRecoveryValue == 'SESSION':
         warning = 'y'
         print "         WARNING: protocol_https_timeout_output_recovery = SESSION is not recommended."
         print "               Instead set to 'SERVANT' (the default) and use the stalled thread threshold."

# Check that HTTP requests are not allowed in until min servants are active ...
   if protocolAcceptHttpWork:
      printProperty("protocol_accept_http_work_after_min_srs")
      protocolAcceptHttpWorkValue = str(protocolAcceptHttpWork[0])
      if protocolAcceptHttpWork[3] == 1:
         warning = 'y'
         print "         WARNING: protocol_http_accept_work_on_min_srs is not set and is defaulting to " +  protocolAcceptHttpWorkValue + "."
         print "                  Consider setting this property to 1 (the default) in order to"
         print "                  avoid requests queuing while servants are initializing."
      else:
         #  The property is set, so warn if it is false ...
         if protocolAcceptHttpWorkValue in ('0', 'false'):
            warning = 'y'
            print "         WARNING: protocol_http_accept_work_on_min_srs = 0"
            print "                  Consider setting this property to 1 (the default) in order to"
            print "                  avoid requests queuing while servants are initializing."

   if protocolSipTimeoutRecovery:
#     The default is probably being overridden which is not recommended ...
      printProperty("protocol_sip_timeout_output_recovery")
      protocolSipTimeoutRecoveryValue = str(protocolSipTimeoutRecovery[0])
      if protocolSipTimeoutRecoveryValue == 'SESSION':
         warning = 'y'
         print "         WARNING: protocol_sip_timeout_output_recovery = SESSION is not recommended."
         print "               Instead set to 'SERVANT' (the default) and use the stalled thread threshold."

   if protocolSipTimeoutOutput:
      protocolSipTimeoutOutputValue = int(protocolSipTimeoutOutput[0])
      printProperty("protocol_sip_timeout_output")
      if protocolSipTimeoutOutput[3] != 1:
      #  SIP protocol timeout is set ...
         if protocolSipTimeoutOutputValue > 0:
            if transactionDefaultTimeoutValue >= protocolSipTimeoutOutputValue:
               warning = 'y'
               print "         WARNING: protocol_sip_timeout_output (" +   str(protocolSipTimeoutOutputValue) + ") is less than transaction_defaultTimeout (" + str(transactionDefaultTimeoutValue) + ")"
               print "                  protocol_sip_timeout_output should be greater than transaction_defaultTimeout"
         else:
            warning = 'y'
            print "         WARNING: protocol_sip_timeout_output should NOT be disabled by setting it to zero"
      else:
         #  SIP protocol timeout is not set so is defaulting ...
         warning = 'y'
         print "            INFO: protocol_sip_timeout_output is not set and is defaulting to " + str(protocolSipTimeoutOutputValue) + " secs."

   if protocolSipsTimeoutOutput:
      protocolSipsTimeoutOutputValue = int(protocolSipsTimeoutOutput[0])
      printProperty("protocol_sips_timeout_output")
      if protocolSipsTimeoutOutput[3] != 1:
      #  SIPS protocol timeout is set ...
         if protocolSipsTimeoutOutputValue > 0:
            if transactionDefaultTimeoutValue >= protocolSipsTimeoutOutputValue:
               warning = 'y'
               print "         WARNING: protocol_sips_timeout_output (" +  str(protocolSipsTimeoutOutputValue) + ") is less than transaction_defaultTimeout (" + str(transactionDefaultTimeoutValue) + ")"
               print "                  protocol_sips_timeout_output should be greater than transaction_defaultTimeout"
         else:
            warning = 'y'
            print "         WARNING: protocol_sips_timeout_output should NOT be disabled by setting it to zero"
      else:
         #  SIPS protocol timeout is not set so is defaulting ...
         warning = 'y'
         print "            INFO: protocol_sips_timeout_output is not set and is defaulting to " +  str(protocolSipsTimeoutOutputValue) + " secs."

   if protocolSipsTimeoutRecovery:
#     The default is probably being overridden which is not recommended ...
      printProperty("protocol_sips_timeout_output_recovery")
      protocolSipsTimeoutRecoveryValue = str(protocolSipsTimeoutRecovery[0])
      if protocolSipsTimeoutRecoveryValue == 'SESSION':
         warning = 'y'
         print "         WARNING: protocol_sips_timeout_output_recovery = SESSION is not recommended."
         print "               Instead set to 'SERVANT' (the default) and use the stalled thread threshold."

#  if no warnings were issued, put out a message that all was OK
   if warning == 'n':
      print "   " + currentServer + " HTTP and SIP time-out checks ended with no warnings."
#
# Is the stalled thread threshold reasonable and will it actually take effect?
#
   if stalledThreadThreshold:
      print "\n   " + currentServer + " Stalled thread threshold checks ..."
      warning = 'n'
      printProperty("server_region_stalled_thread_threshold_percent")
      stalledThreadThresholdValue = int(stalledThreadThreshold[0])
      if stalledThreadThreshold[3] != 1:
         #  Property is set (not defaulting) so check http/https/sip/sips recovery is not SESSION
         if protocolHttpTimeoutRecoveryValue == 'SESSION':
            warning = 'y'
            print "         WARNING: server_region_stalled_thread_threshold_percent has no effect when "
            print "               protocol_http_timeout_output_recovery = SESSION."
         elif protocolHttpsTimeoutRecoveryValue == 'SESSION':
            warning = 'y'
            print "         WARNING: server_region_stalled_thread_threshold_percent has no effect when "
            print "               protocol_https_timeout_output_recovery = SESSION."
         elif protocolSipTimeoutRecoveryValue == 'SESSION':
            warning = 'y'
            print "         WARNING: server_region_stalled_thread_threshold_percent has no effect when "
            print "               protocol_sip_timeout_output_recovery = SESSION."
         elif protocolSipsTimeoutRecoveryValue == 'SESSION':
            warning = 'y'
            print "         WARNING: server_region_stalled_thread_threshold_percent has no effect when "
            print "               protocol_sips_timeout_output_recovery = SESSION."
         elif stalledThreadThresholdValue == 0:
            #  Property is set but set to 0 (the default) which is not good,  so ...
            warning = 'y'
            print "         WARNING: server_region_stalled_thread_threshold_percent=0 which means that"
            print "                  a single time-out could cause a servant restart."
            print "                  It is usually best to set a non-zero value so servants will be scheduled to"
            print "                  restart only after a percentage of threads have become stalled due to timeouts."
            print "                  An exception is for IIOP requests where WAS z/OS is participating in an"
            print "                  existing global transaction. In that scenario it may be best not to enable"
            print "                  the stalled thread threshold."
      else:
         # Property is defaulting which is not good so ...
         warning = 'y'
         print "         WARNING: The server_region_stalled_thread_threshold_percent is defaulting to 0 (disabled)"
         print "                  which means that a single time-out could cause a servant restart."
         print "                  It is usually best to set a non-zero value so servants will be scheduled to"
         print "                  restart only after a percentage of threads have become stalled due to timeouts."
         print "                  An exception is for IIOP requests where WAS z/OS is participating in an"
         print "                  existing global transaction. In that scenario it may be best not to enable"
         print "                  the stalled thread threshold."

#  If no warnings were issued, put out a message that all was OK
   if warning == 'n':
      print "   " + currentServer + " Stalled thread threshold checks ended with no warnings."
#
# Check the queue timeout percents for http,https,sip,sips ...
#
   print "\n   " + currentServer + " HTTP and SIP queue timeout percent checks ..."
   warning = 'n'
#
   if httpQueueTimeoutPercent:
#     Is the control_region_http_queue_timeout_percent reasonable? ...
      qptwarning = checkQueuePercentTimeout( "http" )

   if httpsQueueTimeoutPercent:
#     Is the control_region_https_queue_timeout_percent reasonable? ...
      qptwarning = checkQueuePercentTimeout( "https" )

   if sipQueueTimeoutPercent:
#     Is the control_region_sip_queue_timeout_percent reasonable? ...
      qptwarning = checkQueuePercentTimeout( "sip" )

   if sipsQueueTimeoutPercent:
#     Is the control_region_sips_queue_timeout_percent reasonable? ...
      ptwarning = checkQueuePercentTimeout( "sips" )

#  If no warnings were issued, put out a message that all was OK
   if (warning == 'n') and (qptwarning == 'n'):
      print "   " + currentServer + " HTTP and SIP queue timeout percent checks ended with no warnings."
#
# CPU time used limit checks ...
#
   print "\n   " + currentServer + " CPU time used limit checks ..."
   warning = 'n'

   cpuTimeUsedLimit = getProperty("server_region_request_cputimeused_limit")

   if cpuTimeUsedLimit:
#     If not suggest, suggest setting it. If too small, warn about units ...
      printProperty("server_region_request_cputimeused_limit")
      cpuTimeUsedLimitValue = int(cpuTimeUsedLimit[0])
      if cpuTimeUsedLimit[3] != 1:
         # The property is set so check the value is reasonable ...
         if cpuTimeUsedLimitValue == 0:
            warning = 'y'
            print "         WARNING: server_region_request_cputimeused_limit is not set so CPU-intensive or looping"
            print "                  tasks will be allowed to keep running. Consider setting a non-zero value (millisecs)."
         if (cpuTimeUsedLimitValue > 0) and (cpuTimeUsedLimitValue < 1000):
            warning = 'y'
            print "         WARNING: server_region_request_cputimeused_limit is less than 1 second. (" + str( cpuTimeUsedLimitValue ) + ")"
            print "                  Note that he units for this property are millisecs, not secs. This value seems low."
      else:
            # The property is defaulting which is not good, so ...
            warning = 'y'
            print "         WARNING: server_region_request_cputimeused_limit is defaulting to  (" + str( cpuTimeUsedLimitValue ) + ") (ms)"
            print "                  which means that the property is disabled and requests are can consume unlimited CPU."

#  If no warnings were issued, put out a message that all was OK
   if warning == 'n':
      print "   " + currentServer + " CPU time used checks ended with no warnings."
#
# Is control_region_timeout_delay set to a reasonable value? ...
#
   print "\n   " + currentServer + " control_region_timeout_delay check ..."
   warning = 'n'

   controlRegionTimeoutDelay = getProperty("control_region_timeout_delay")
   if controlRegionTimeoutDelay:
      printProperty("control_region_timeout_delay")
      controlRegionTimeoutDelayValue = int(controlRegionTimeoutDelay[0])
      if controlRegionTimeoutDelay[3] != 1:
         # Property is set so check the value ...
         if controlRegionTimeoutDelayValue == 0:
            warning = 'y'
            print "         WARNING: control_region_timeout_delay=0 which means that servants"
            print "                  scheduled for restart will be terminated immediately leaving no time"
            print "                  for other requests to end. Usually it is best to set a non-zero"
            print "                  value of a few secs to reduce the impact of restarting servants."
         elif (controlRegionTimeoutDelayValue > 10):
            warning = 'y'
            print "         WARNING: control_region_timeout_delay = " + str(controlRegionTimeoutDelayValue) + " is a rather long time to delay"
            print "                  the termination of a servant scheduled for restart."
            print "                  For online workloads (as opposed to batch) a value < 10 is usually sufficient."
         else:
            print "            INFO: control_region_timeout_delay = " + str(controlRegionTimeoutDelayValue) + " will allow requests some time"
            print "                  to end normally in a servant scheduled for restart."
            print "                  Usually this is a good practice, but note that the diagnostics taken when"
            print "                  the servant terminates may miss the specific infomation pertaining to"
            print "                  the timeout which caused the decision to restart the servant."
      else:
         # Property is not set and the default is not so good, so ...
         warning = 'y'
         print "         WARNING: control_region_timeout_delay is not set which means that servants"
         print "                  scheduled for restart will be terminated immediately leaving no time"
         print "                  for other requests to end. Usually it is best to set a non-zero"
         print "                  value of a few secs to reduce the impact of restarting servants."

#  If no warnings were issued, put out a message that all was OK
   if warning == 'n':
      print "   " + currentServer + " control_region_timeout_delay checks ended with no warnings."
#
# Can HTTP be requeued if the affinity servant is scheduled for restart?
#
   print "\n   " + currentServer + " HTTP re-queue requests with affinity check ..."
   warning = 'n'

   if httpRequeue:
      printProperty("control_region_http_requeue_enabled")
      # Find out if session persistence is enabled ...
      sessMgrId = AdminConfig.list("SessionManager", AdminConfig.getid("/Server:" + currentServer + "/"))
      sessionRecovery = AdminConfig.showAttribute(sessMgrId, 'sessionPersistenceMode')
      # Check if requeue is set ...
      httpRequeueValue = str(httpRequeue[0])
      if httpRequeue[3] == 1:
         # If httpRequeue is defaulting, warn that it is disabled ...
         warning = 'y'
         print "         WARNING: control_region_http_requeue_enabled is not set and defaults to 0."
      else:
         # Check control_region_timeout_delay and session recovery ...
         if (httpRequeueValue == '1') and (controlRegionTimeoutDelayValue == 0):
            warning = 'y'
            print "         WARNING: control_region_http_requeue_enabled = 1 but control_region_timeout_delay = 0 so "
            print "                  control_region_http_requeue_enabled=1 will have no effect."
            print "                  A value must be set for control_region_timeout_delay for HTTP requeue to have any effect."
         if controlRegionTimeoutDelayValue > 0:
            if (httpRequeueValue in( '', '0')):
               # If httpRequeue property is defined but has no value or is set to the default 0 ...
               # Suggest to set it and word message differently depending on state of session recovery.
               warning = 'y'
               print "         WARNING: control_region_http_requeue_enabled = 0 and control_region_timeout_delay = " + str(controlRegionTimeoutDelayValue) + "(secs)."
               print "                  If a servant is scheduled for restart following one or more timeouts, this means"
               print "                  HTTP requests with affinity to that servant will fail during the delay period."
               print "                  Consider setting control_region_http_requeue_enabled = 1 so that HTTP requests"
               print "                  with affinity can be re-queued to another servant during the delay period."
               if sessionRecovery == 'None':
                  print "                  Also consider enabling HTTP session recovery so users are not forced to"
                  print "                  restart their session if their request is requeued to another servant."
               else:
                  print "                  HTTP session recovery is set to '" + sessionRecovery + "' which means that the end"
                  print "                  users of requeued requests should not be aware of the servant restart."
            if (httpRequeueValue == '1') and (sessionRecovery == 'None'):
               # httpRequeue is set to 1 which is good, but session recovery is not enabled ...
               warning = 'y'
               print "         WARNING: control_region_http_requeue_enabled = 1 and control_region_timeout_delay = " + str(controlRegionTimeoutDelayValue) + "(secs)"
               print "                  but HTTP session recovery is not enabled for this server."
               print "                  This means that HTTP requests with an affinity to a servant that has been"
               print "                  scheduled to restart will be re-queued to another servant during the"
               print "                  control_region_timeout_delay period."
               print "                  But since HTTP session recovery is not enabled, the HTTP session cannot"
               print "                  cannot be recovered and the user will have to start a new session."
            if (httpRequeueValue == '1') and (sessionRecovery != 'None'):
               # httpRequeue is set to 1 which is good, and session recovery is enabled which is even better ...
               print "            INFO: control_region_http_requeue_enabled = 1 and HTTP session recovery mode is set"
               print "                  to '" + sessionRecovery + "'. This means that HTTP requests with an affinity"
               print "                  to a servant that has been scheduled to restart will be re-queued to"
               print "                  another servant during the control_region_timeout_delay period and the HTTP"
               print "                  session should be recovered in that other servant."
               print "                  The end user should not be aware of the servant restart."

#  If no warnings were issued, put out a message that all was OK
   if warning == 'n':
      print "   " + currentServer + " HTTP re-queue checks ended with no warnings."
#
# Check what happens if all servants scheduled for restart ...
#
   print "\n   " + currentServer + " Check which action is taken if there should be no servants ..."
   warning = 'n'

   if controlRegionDregOnNoSrs:
      printProperty("control_region_dreg_on_no_srs")
      # Find out if the property has a value ...
      controlRegionDregOnNoSrsValue = str(controlRegionDregOnNoSrs[0])
   if controlRegionTimeoutSaveLastServant:
      printProperty("control_region_timeout_save_last_servant")
      controlRegionTimeoutSaveLastServantValue = str(controlRegionTimeoutSaveLastServant[0])
#     print 'controlRegionDregOnNoSrsValue = ' + controlRegionDregOnNoSrsValue
#     print 'controlRegionTimeoutSaveLastServantValue = ' + controlRegionTimeoutSaveLastServantValue

   if controlRegionDregOnNoSrs[3] == 1:
      # If control_region_dreg_on_no_srs is defaulting, warn that it is disabled ...
      warning = 'y'
      print "         WARNING: control_region_dreg_on_no_srs is not set and defaults to 0 (disabled)."
   elif controlRegionDregOnNoSrsValue != '1':
      # If control_region_dreg_on_no_srs is not set, warn that it is disabled ...
      warning = 'y'
      print "         WARNING: control_region_dreg_on_no_srs is set to " + str(controlRegionDregOnNoSrsValue) + " (disabled)."
   if (controlRegionDregOnNoSrs[3] == 1) or (controlRegionDregOnNoSrsValue != '1'):
      print "                  This means that if all servants should be scheduled to restart following timeouts,"
      print "                  requests will still be accepted by the control region and will queue until MINSRS"
      print "                  is reached. Consider setting control_region_dreg_on_no_srs=1 so the control region"
      print "                  will automatically PAUSELISTENERS until the minimum number of servants have initialized."
      print "                  Requests can then be sent to another cluster member until this server has active servants."
   if controlRegionTimeoutSaveLastServant[3] == 1:
      # If control_region_timeout-save_last_servant is defaulting, warn that it is disabled ...
      warning = 'y'
      print "         WARNING: control_region_timeout-save_last_servant is not set and defaults to 0 (disabled)."
   elif controlRegionTimeoutSaveLastServantValue != '1':
      # If control_region_timeout-save_last_servant is not set, warn that it is disabled ...
      warning = 'y'
      print "         WARNING: control_region_timeout_save_last_servant is set to " + str(controlRegionTimeoutSaveLastServantValue) + " (disabled)."
      print "                  This means that if all servants are scheduled to restart following timeouts,"
      print "                  all the servants could be terminated and then restarted at the same time."
      if controlRegionDregOnNoSrsValue != '1':
         print "                  Also, since control_region_dreg_on_no_srs is not set to 1, requests will be accepted while"
         print "                  the servants are restarting. Requests will be forced to queue until a minimum number of"
         print "                  servants have initialized. Consider setting control_region_dreg_on_no_srs=1 so requests"
         print "                  are not accepted until a minimum number of servants have initialized to process them."
         print "                  This should cause requests to be sent to another cluster member where they should run."
         print "                  Or, consider setting control_region_timeout_save_last_servant=1 because the last servant"
         print "                  may be able to process requests while other servant(s) are restarting."
         print "                  Delaying the restart of the last servant will also tend to spread-out the CPU"
         print "                  consumed by the restarting servant(s)."
   if (controlRegionDregOnNoSrsValue == '1') and (controlRegionTimeoutSaveLastServantValue == '1'):
         print "            INFO: Both control_region_dreg_on_no_srs=1 and control_region_timeout_save_last_servant=1."
         print "                  Setting control_region_dreg_on_no_srs=1 means that if all servants are scheduled to be"
         print "                  restarted following timeouts, PAUSELISTENERS is issued until a minimum number of servants"
         print "                  have initialized. By also setting control_region_timeout_save_last_servant=1, the"
         print "                  termination of the last servant is delayed until at least one other servant has initialized."
         print "                  That last servant can not receive any requests while listeners are paused, but delaying the"
         print "                  servant termination should help to spread-out the CPU consumed by the restarting servants."
#  If no warnings were issued, put out a message that all was OK
   if warning == 'n':
      print "   " + currentServer + " Checks about the action taken if no servants have ended with no warnings."

#
# Extract and print Connection Factory properties
# The objective is to process only resources that might apply to the
# cluster members, or to a  specific server if only a servername is
# input. Therefore resources at node scope are not processed when
# a cluster name is input.
# If a servername is passed in rather than a cluster name, resources
# at node scope are listed if not present at server scope.
#
   print "\n   Starting Datasource and Connection Factory checks ..."

   for thisFactory in allV4Factories:
      if thisFactory == "":
         # Null entry
         continue
      elif thisFactory.find("applications") != -1:
         # Application definition so skip it ...
         continue
      elif thisFactory.find("clusters") != -1:
         # Cluster level definition
         cfScope = 'Cluster=' + currentCluster
         if thisFactory.find(currentCluster) != -1:
            # Definition for this cluster - process it
            printConnectionFactoryV4(thisFactory, cfScope)
            continue
      elif thisFactory.find("servers") != -1:
         # Server level definition
         cfScope = 'Server=' + currentServer
         if thisFactory.find(currentServer) != -1:
            # Definition for this server - process it
            printConnectionFactoryV4(thisFactory, cfScope)
      elif (thisFactory.find("nodes") != -1):
         # Node level definition
         if (thisFactory.find(currentServer) == -1):
            # Only process node scope resource if no resource at server scope and if not a cluster check
            cfScope = 'Node=' + currentNode
            if (thisFactory.find(currentNode) != -1):
               # Definition for this node - process it
               printConnectionFactoryV4(thisFactory, cfScope)
      else:
         # Cell level definition - process it
         cfScope = 'Cell=' + currentCell
         printConnectionFactoryV4(thisFactory, cfScope)

   for thisFactory in allV8Factories:
      if thisFactory == "":
         # Null entry
         continue
      elif thisFactory.find("applications") != -1:
         # Application definition so skip it ...
         continue
      elif thisFactory.find("clusters") != -1:
         # Cluster level definition
         cfScope = 'Cluster=' + currentCluster
         if thisFactory.find(currentCluster) != -1:
            # Definition for this cluster - process it
            printConnectionFactoryV8(thisFactory, cfScope)
            continue
      elif thisFactory.find("servers") != -1:
         # Server level definition
         cfScope = 'Server=' + currentServer
         if thisFactory.find(currentServer) != -1:
            # Definition for this server - process it
            printConnectionFactoryV8(thisFactory, cfScope)
            continue
      elif thisFactory.find("nodes") != -1:
         # Node level definition
         if (thisFactory.find(currentServer) == -1):
            # Only process node scope resource if no resource at server scope.
            cfScope = 'Node=' + currentNode
            if (thisFactory.find(currentNode) != -1):
               # Definition for this node - process it
               printConnectionFactoryV8(thisFactory, cfScope)
               continue
      else:
         # Cell level definition - process it
         cfScope = 'Cell=' + currentCell
         printConnectionFactoryV8(thisFactory, cfScope)

#  endfor
#
#  Start SIB checks ...

   if allSIBs[0]:
      # Only process SIBs if there is at least one SIB ...
      print "\n   Starting Service Integration Bus checks ..."
      for thisSIB in allSIBs:
         if thisSIB == "":
            # Null entry
            continue
         else:
            # All SIBs have cell scope so no need pass scope
            printSIB( thisSIB )

      #endfor

#
#----------------------------------------------------------------------
# End of checkServer
#----------------------------------------------------------------------
#

# -------------------------------------------------------------------
# Start of funtions called from checkServer ...
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# getCellName routine: Get the cell name
# -------------------------------------------------------------------
#
def getCellName():
    """Return the name of the cell we're connected to"""
    # AdminControl.getCell() is simpler, but only
    # available if we are connected to a running server.
    cellObjects = getObjectsOfType('Cell')  # should only be one
    cellname = AdminConfig.showAttribute(cellObjects[0], 'name')
    return cellname

# -------------------------------------------------------------------
# Check all members of a cluster
# checkCluster routine: This calls checkServer for each cluster member
# -------------------------------------------------------------------
#
def checkCluster(clusterId):
   """Run checkServer for all members of a cluster"""
   cluster_name = AdminConfig.showAttribute(clusterId, "name")
   member_ids = AdminConfig.showAttribute(clusterId, "members")
   # AdminConfig returns the list in [], get rid of the brackets
   member_ids = member_ids[1:-1]
   # For each member confid, extract the member and node names ...
   for member_id in member_ids.split():
      member_name=AdminConfig.showAttribute(member_id, "memberName")
      node_name=AdminConfig.showAttribute(member_id, "nodeName")
      print "\n   Checking cluster member " + member_name + " on node " + node_name + ' ...'
      checkServer(cluster_name, member_name, "cluster")
# -------------------------------------------------------------------
# getProperty routine: Get a property set by setProperty
# -------------------------------------------------------------------
#
def getProperty(propertyName):

   try:
      return propertyMap[propertyName]
   except:
      return None
# -------------------------------------------------------------------
# setProperty routine: Set a property and its values in a property map
# -------------------------------------------------------------------
#
def setProperty(propertyName, propertyValue, propertyMeasure, propertyScope, defaultFlag=None):

   if defaultFlag == None:
      propertyMap[propertyName] = [propertyValue, propertyMeasure, propertyScope, 0]
   else:
      propertyMap[propertyName] = [propertyValue, propertyMeasure, propertyScope, 1]
# -------------------------------------------------------------------
# printProperty routine: print a property if verbose set
# -------------------------------------------------------------------
#
def printProperty(propertyName):
   # The propertyType is just used to decide how to pad fields for printing
   # so the names, values and units are approximately aligned in columns
   if verboseFlag == "false":
      return
   padLength = 48
   propertyNamePadded = (propertyName+"                                                 ")[:padLength]
   propertyScope = ""
   propertyAttributes = getProperty(propertyName)
   propertyValue = propertyAttributes[0]
   if propertyValue == 0:
      valueLen = 1
   else:
      valueLen = len(str(propertyValue))
   propertyMeasure = propertyAttributes[1]
   propertyScope = propertyAttributes[2]

   if propertyAttributes[3] == 1:
      propertyDefault = "Default"
      pads = ""
   else:
      propertyDefault = "Set"
      pads = "     "

   pad  = ""
   if propertyMeasure:
      # calculate total length of print string with propertyValue and propertyMeasure
      # There is 1 blank and 2 () when there is a value and a measure.
      # in order to work out how many spaces to pad before propertyDefault (string  'Set' or 'Default').
      plen = ( 3 + valueLen + len(propertyMeasure) )
      padm = (pad+"           ")[:12 - plen]
      print "      %s: %s (%s) %s (%s) %s %s" % (propertyNamePadded, propertyValue, propertyMeasure, padm, propertyDefault, pads, propertyScope)
   else:
      if valueLen > 12:
         # If long value, no padding for value ...
         padv = ""
      else:
         padv = (pad+"            ")[:12 - valueLen]

      print "      %s: %s %s (%s) %s %s" % (propertyNamePadded, propertyValue, padv, propertyDefault, pads, propertyScope)

# -------------------------------------------------------------------
# printConnectionFactoryV4: Extract and print a V4 Connection Factory
# -------------------------------------------------------------------
#
def printConnectionFactoryV4(currentCF, scope):

   global AdminConfig

   connectionPool = AdminConfig.showAttribute(currentCF, "connectionPool")
   if connectionPool != None:
#     The connection pool exists
      print "\n    " + AdminConfig.showAttribute(currentCF,"name") + " V4 Connection Factory connection pool at scope: " + scope
      orphanTimeoutValue = AdminConfig.showAttribute(connectionPool,"orphanTimeout")
      setProperty("orphanTimeout", orphanTimeoutValue, "s", "")
      connectionTimeoutValue = AdminConfig.showAttribute(connectionPool,"connectionTimeout")
      setProperty("connectionTimeout", connectionTimeoutValue, "s", "")
      printProperty("orphanTimeout")
      if int(orphanTimeoutValue) > 0:
         controlRegionWlmDispatchTimeoutValue = int(getProperty("control_region_wlm_dispatch_timeout")[0])
         controlRegionMdbRequestTimeoutValue = int(getProperty("control_region_mdb_request_timeout")[0])
         protocolHttpTimeoutOutput = getProperty("protocol_http_timeout_output")
         protocolHttpsTimeoutOutput = getProperty("protocol_https_timeout_output")
#        Takes 2 cycles of orphan timeout before connection is freed
         orphanTimeoutPeriod = int(orphanTimeoutValue) * 2
         if (controlRegionWlmDispatchTimeoutValue > 0) and (orphanTimeoutPeriod >= controlRegionWlmDispatchTimeoutValue):
            print "         WARNING: orphanTimeout*2 should be less than control_region_wlm_dispatch_timeout (" + str(controlRegionWlmDispatchTimeoutValue) + ")"
         if (controlRegionMdbRequestTimeoutValue > 0) and (orphanTimeoutPeriod >= controlRegionMdbRequestTimeoutValue):
            print "         WARNING: orphanTimeout*2 should be less than control_region_mdb_dispatch_timeout (" + str(controlRegionMdbRequestTimeoutValue) + ")"
         if protocolHttpTimeoutOutput != None:
            protocolHttpTimeoutOutputValue = int(protocolHttpTimeoutOutput[0])
            if (protocolHttpTimeoutOutputValue > 0) and (orphanTimeoutPeriod >= protocolHttpTimeoutOutputValue):
               print "         WARNING: orphanTimeout*2 should be less than protocol_http_timeout_output (" + str(protocolHttpTimeoutOutputValue) + ")"
         if protocolHttpsTimeoutOutput != None:
            protocolHttpsTimeoutOutputValue = int(protocolHttpsTimeoutOutput[0])
            if (protocolHttpsTimeoutOutputValue > 0) and (orphanTimeoutPeriod >= protocolHttpsTimeoutOutputValue):
               print "         WARNING: orphanTimeout*2 should be less than protocol_https_timeout_output (" + str(protocolHttpsTimeoutOutputValue) + ")"
      printProperty("connectionTimeout")
      if int(connectionTimeoutValue) > 0:
         transactionDefaultTimeoutValue = int(getProperty("transaction_defaultTimeout")[0])
         if (transactionDefaultTimeoutValue > 0) and (int(connectionTimeoutValue) >= transactionDefaultTimeoutValue):
            print "         WARNING: connectionTimeout should be less than transaction_defaultTimeout (" + str(transactionDefaultTimeoutValue) + ")"

# -------------------------------------------------------------------
# printConnectionFactoryV8: Extract and print a V8 Connection Factory
# -------------------------------------------------------------------
def printConnectionFactoryV8(currentCF, scope):

   global AdminConfig

   # Test if the currentCF is for a CMP datasource  ...
   try:
      isCmp = AdminConfig.showAttribute(currentCF, "cmpDatasource")
   except:
      isCmp = 'N'

   # Get the connectionPool for this CF ... (a CF should always have one)
   connectionPool = AdminConfig.showAttribute(currentCF, "connectionPool")
   warning = 'n'
   if (connectionPool != None) and (isCmp == 'N'):
      # The connection pool exists and it is not a CMP Connection Factory
      print "\n    " + AdminConfig.showAttribute(currentCF,"name") + " Connection Factory connection pool at scope: " + scope
      # Try to find confid of a datasource that owns this connection pool and determine datasource type
      dsId = getDsConfForCpId( connectionPool )
      dsType = getDsType( dsId )
      # Get connection pool timeouts ...
      agedTimeoutValue = AdminConfig.showAttribute(connectionPool,"agedTimeout")
      setProperty("agedTimeout", agedTimeoutValue, "s", "")
      printProperty("agedTimeout")
      #
      connectionTimeoutValue = AdminConfig.showAttribute(connectionPool,"connectionTimeout")
      setProperty("connectionTimeout", connectionTimeoutValue, "s", "")
      printProperty("connectionTimeout")
      #
      reapTimeValue = AdminConfig.showAttribute(connectionPool,"reapTime")
      setProperty("reapTime", reapTimeValue, "s", "")
      printProperty("reapTime")
      #
      unusedTimeoutValue = AdminConfig.showAttribute(connectionPool,"unusedTimeout")
      setProperty("unusedTimeout", unusedTimeoutValue, "s", "")
      printProperty("unusedTimeout")
      # Get some other properties related to timeouts ...
      minConnectionsValue = AdminConfig.showAttribute(connectionPool,"minConnections")
      setProperty("minConnections", minConnectionsValue, "", "")
      printProperty("minConnections")
      #
      purgePolicyValue = AdminConfig.showAttribute(connectionPool,"purgePolicy")
      setProperty("purgePolicy", purgePolicyValue, "", "")
      printProperty("purgePolicy")
      # Now do some checks on the values ...
      # When DB2 datasources are created the connection pool always has some values set
      # for the main timeouts so we do not need a separate check that the property is set.
      if int(agedTimeoutValue) > 0:
         if int(reapTimeValue) == 0:
            warning = 'y'
            print "         WARNING: agedTimeout inactive due to reapTime (" + str(reapTimeValue) + ")"
         else:
            if int(agedTimeoutValue) <= int(reapTimeValue):
               warning = 'y'
               print "         WARNING: agedTimeout (" + str(agedTimeoutValue) + ") should be greater than reapTime (" + str(reapTimeValue) + ")"
      #
      if int(unusedTimeoutValue) > 0:
         if int(reapTimeValue) == 0:
            warning = 'y'
            print "         WARNING: unusedTimeout (" + str(unusedTimeoutValue) + ") is inactive due to reapTime (" + str(reapTimeValue) + ")"
         else:
            if int(unusedTimeoutValue) <= int(reapTimeValue):
               warning = 'y'
               print "         WARNING: unusedTimeout (" + str(unusedTimeoutValue) + ") should be greater than reapTime (" + str(reapTimeValue) + ")"
      elif (int(unusedTimeoutValue) > 1800) and (dsId == '4'):
         warning = 'y'
         print "         WARNING: unusedTimeout (" + str(unusedTimeoutValue) + ") should NOT be set > 1800 for type 4 datasources if there"
         print "                  is a firewall between WAS and the DB2 database."
         print "                  Set unused timeout to about 50% of the firewall idle timeout."
         print "                  A firewall idle timeout usually defaults to 3600 secs."
      else:
         warning = 'y'
         print "         WARNING: unusedTimeout (" + str(unusedTimeoutValue) + ") should NOT be disabled by setting it to zero"
      #
      if int(connectionTimeoutValue) > 0:
         transactionDefaultTimeoutValue = int(getProperty("transaction_defaultTimeout")[0])
         transactionDefaultTimeoutValuems = int(transactionDefaultTimeoutValue*1000)
         if (transactionDefaultTimeoutValue > 0) and (int(connectionTimeoutValue) >= transactionDefaultTimeoutValue):
            warning = 'y'
            print "         WARNING: connectionTimeout (" + str(connectionTimeoutValue) + ") should be less than transaction_defaultTimeout (" + str(transactionDefaultTimeoutValue) + ")"
            print "                  In the ISC, transaction_defaultTimeout is the field 'Total transaction lifetime timeout'"
            print "                  in a server's transaction service settings."
      if (dsType == '4') and (minConnectionsValue != 0):
         warning = 'y'
         # For a T4 datasource it is often best to set minConnection = 0 to avoid stale connections
         # when there is a filewall between WAS and the database
         print "         WARNING: minConnections =" + str(minConnectionsValue) + " but for a T4 datasource"
         print "                  with a firewall between WAS and the database it is often better to set"
         print "                  minConnections = 0. This will ensure no connection is left 'stale' if"
         print "                  a network problem or firewall timeout should break the connection to"
         print "                  the database. When minConnections = 0, the default purgePolicy of"
         print "                  'PurgeEntirePool' can cleanup all stale connections."
      if (warning == 'n'):
         print "    No warnings generated for this Connection Factory connection pool"

      if dsId:
         warning = 'n'
         # If this is a datasource check the datasource custom properties ...
         if dsType:
            print "\n    " + AdminConfig.showAttribute(dsId,"name") + " T" + str(dsType) + " datasource custom properties at scope: " + scope
         else:
            print "\n    " + AdminConfig.showAttribute(dsId,"name") + " datasource custom properties at scope: " + scope
         #-------------------------------------------------------------
         # Check various datasource custom properties related to timeouts ...
         # List the datasource custom properties
         #-------------------------------------------------------------
         listJ2EEResourceProperty = AdminConfig.list('J2EEResourceProperty', dsId).split(lineSeparator)
         #-------------------------------------------------------------
         # For each property in dscustproplist, set the property map to
         # the default values initially. Then see if the property has
         # a value set. If it does, and the value is not the same as
         # the default value, update the property map with the value
         # and remove the defaultFlag fom the property map.
         #-------------------------------------------------------------
         for n in range(len(dscustproplist)):
            ivarx = dscustproplist[n][0]
            idefx = dscustproplist[n][1]
            imesx = dscustproplist[n][2]
            idesx = dscustproplist[n][3]
            setProperty(ivarx, idefx, "", "", "default")
            # Find the current value for this property ...
            for j2eeresource in listJ2EEResourceProperty:
               if j2eeresource.startswith(ivarx + '(' ):
                  ovalue = AdminConfig.showAttribute(j2eeresource, "value")
                  if (ovalue) and (str(ovalue) != str(idefx)):
                     # Only put the set value in (and remove defaultFlag) if it differs from the default value
                     setProperty( ivarx, ovalue, imesx, "")
               #endif j2eeresource
            #endfor j2eeresource
         #endfor n
         #-------------------------------------------------------------
         # Analyse datasource custom properties ...
         #-------------------------------------------------------------
         # First get all the properties for timeout-related custom properties
         #-------------------------------------------------------------
         blockingReadConnectionTimeout = getProperty("blockingReadConnectionTimeout")
         currentLockTimeout = getProperty("currentLockTimeout")
         enableSysplexWLB = getProperty("enableSysplexWLB")
         loginTimeout = getProperty("loginTimeout")
         keepAliveTimeOut = getProperty("keepAliveTimeOut")
         interruptProcessingMode = getProperty("interruptProcessingMode")
         queryTimeoutInterruptProcessingMode = getProperty("queryTimeoutInterruptProcessingMode")
         syncQueryTimeoutWithTransactionTimeout = getProperty("syncQueryTimeoutWithTransactionTimeout")
         timerLevelForQueryTimeOut = getProperty("timerLevelForQueryTimeOut")
         webSphereDefaultQueryTimeout = getProperty("webSphereDefaultQueryTimeout")
         #-------------------------------------------------------------
         # Check each property ...
         #-------------------------------------------------------------
         # blockingReadConnectionTimeout is very useful for T4 datasources and should be set
         # but does not apply to T2 datasources
         if blockingReadConnectionTimeout:
            printProperty("blockingReadConnectionTimeout")
            blockingReadConnectionTimeoutValue = ""
            if blockingReadConnectionTimeout[0]:
               # A value is set so get it ...
               blockingReadConnectionTimeoutValue = int(blockingReadConnectionTimeout[0])
               if dsType == '2':
                  warning = 'y'
                  # A value is set but datasource is T2, warn that property does not apply
                  print "         WARNING: blockingReadConnectionTimeout (" + str(blockingReadConnectionTimeoutValue) + ") does not apply"
                  print "                  to a T2 datasource."
            else:
               # No value is set but if T4 it is usually best to set one ...
               if dsType == '4':
                  warning = 'y'
                  print "         WARNING: No value is set for blockingReadConnectionTimeout"
                  print "                  For a T4 datasource it is usually best to set a blockingReadConnectionTimeout"
                  print "                  in order to avoid that network issues may cause threads to hang in WebSphere."

         # currentLockTimeout applies only to T4 datasources
         # -1  (WAIT)     means that the database manager is to wait until a lock is released,
         #                or a deadlock is detected (SQLSTATE 40001 or 57033).
         #  0  (NOT WAIT) means that the database manager is not to wait for locks that cannot
         #                be obtained, and an error (SQLSTATE 40001 or 57033) will be returned. (This is the default.)
         # ''  (NULL)     means the value of the locktimeout database configuration parameter is to be used when waiting for a lock.
         if currentLockTimeout:
            printProperty("currentLockTimeout")
            currentLockTimeoutValue = ""
            if currentLockTimeout[0]:
               # A value was set so issue warnings ...
               currentLockTimeoutValue = int(currentLockTimeout[0])
               if dsType == '4':
                  if currentLockTimeoutValue == -1:
                     warning = 'y'
                     print "         WARNING: Setting currentLockTimeout (" + str(currentLockTimeoutValue) + ") means that the"
                     print "                  database manager is to wait until a lock is released. This could cause locks to be"
                     print "                  held for a long time and result in data-contention issues."
                     print "                  Usually currentLockTimeout is not set to any value."
               else:
                  # Datasource must be T2
                  if currentLockTimeoutValue != 0:
                     warning = 'y'
                     print "         WARNING: currentLockTimeout (" + str(currentLockTimeoutValue) + ") is set but this"
                     print "                  property does not apply to a T2 datasource."

         # enableSysplexWLB determines whether Sysplex load balancing is enabled for T4 connections to DB2 z/OS. Default=false.
         # For T4 datasources, warn if enableSysplexWLB is not true because generally that is a good thing to set.
         # If enableSysplexWLB = true, connection pool timeout settings should be different:
         # reap time = 0, Aged timeout = 0, Purge policy = FailingConnectionOnly
         if enableSysplexWLB:
            printProperty("enableSysplexWLB")
            enableSysplexWLBValue = ""
            if enableSysplexWLB[0]:
               # There is a value set for enableSysplexWLB so get it ...
               enableSysplexWLBValue = str(enableSysplexWLB[0])
               if dsType == '4':
                  # The property is not set, suggest to set it ...
                  if (enableSysplexWLBValue == '0') or (enableSysplexWLBValue == 'false'):
                     warning = 'y'
                     print "         WARNING: enableSysplexWLB (" + str(enableSysplexWLBValue) + ") is set but the datasource is T4."
                     print "                  Usually it is best to set enableSysplexWLB=true for this kind of datasource."
                     print "                  If you decide to set enableSysplexWLB=true, also adjust the Connection Pool"
                     print "                  timeouts as follows:"
                     print "                  reap time = 0, Aged timeout = 0, Purge policy = FailingConnectionOnly"
                  else:
                     # The enableSysplexWLBValue is set to 1/true so ...
                     # check the connection pool values for this datasource ...
                     warning = 'y'
                     print "         WARNING: When enableSysplexWLB = true the Connection Pool time-outs should be different."
                     if int(reapTimeValue) != 0:
                        print "                  Reap time = " + str(reapTimeValue) + ") but Reap time = 0 is better."
                     if int(agedTimeoutValue) != 0:
                        print "                  Aged timeout = " + str(agedTimeoutValue) + ") but Aged timeout = 0 is better."
                     if purgePolicyValue != 'FailingConnectionOnly':
                        print "                  Purge policy is '" + str(purgePolicyValue) + "' but Purge policy 'FailingConnectionOnly' is better."
               else:
                  # Datasource is not T4. Warn if enableSysplexWLB is set because it will have no effect ...
                  if (enableSysplexWLBValue == '1') or (enableSysplexWLBValue == 'true'):
                     warning = 'y'
                     print "         WARNING: enableSysplexWLB (" + str(enableSysplexWLBValue) + ") is set but this property"
                     print "                  does not apply to a T2 datasource."
            else:
               # There is no value set for enableSysplexWLB. Maybe this property
               # is not known about so if T4 suggest to use it.
               if dsType == '4':
                  warning = 'y'
                  print "         WARNING: This datasource is using a T4 driver to DB2 z/OS but no value has been set"
                  print "                  for enableSysplexWLB and the default value is '0|false'."
                  print "                  Usually it is best to set enableSysplexWLB=1|true for this kind of datasource."
                  print "                  If you decide to set enableSysplexWLB=true, also adjust the Connection Pool"
                  print "                  timeouts as follows:"
                  print "                  reap time = 0, Aged timeout = 0, Purge policy = FailingConnectionOnly"

         # loginTimeout is a largely unused property that has been superceded by the
         # connection timeout in the connection pool. The default of 0 means it is
         # not used. Any non-zero value will not be used when connection timeout is set.
         # loginTimeout does not apply to T2 datasources.
         if loginTimeout:
            printProperty("loginTimeout")
            loginTimeoutValue = ""
            if loginTimeout[0]:
               # A value has been set, so get it ...
               loginTimeoutValue = int(loginTimeout[0])
               if dsType == '4':
                  # If datasource is T4 and a connectionTimepout is set, this property is ignored so warn about that.
                  if (loginTimeoutValue != 0) and (int(connectionTimeoutValue) != 0):
                     warning = 'y'
                     print "         WARNING: loginTimeout (" + str(loginTimeoutValue) + ") will be ignored"
                     print "                  because connectionTimeout (" + str(connectionTimeoutValue) + ") overrides it."
                     print "                  loginTimeout is normally not used and allowed to default to 0."
               else:
               # A value is set but the datasource is T2 but this property does not apply to T2.
                  if loginTimeoutValue != 0:
                     warning = 'y'
                     print "         WARNING: loginTimeout (" + str(loginTimeoutValue) + ") will be ignored"
                     print "                  because it is valid for T4 datsources only."
                     print "                  loginTimeout is normally not used and allowed to default to 0."

         # interruptProcessingMode determines whether it allowed to cancel a long running SQL request
         # 0: DB2BaseDataSource.INTERRUPT_PROCESSING_MODE_DISABLED         Disables cancelling of SQL requests.
         # 1: DB2BaseDataSource.INTERRUPT_PROCESSING_MODE_STATEMENT_CANCEL This is the default.
         # 2: DB2BaseDataSource.INTERRUPT_PROCESSING_MODE_CLOSE_SOCKET     For T4 connections to DB2 for z/OS data servers,
         #                                                                 this value is always used regardless
         # In order for webSphereDefaultQueryTimeout to be effective,
         # For T2 and T4 datasources, warn if interruptProcessingMode is set to 0 (disabled)
         # For T4 datasources, warn if interruptProcessingMode is not 2, because 2 will be used anyway.
         if interruptProcessingMode:
            printProperty("interruptProcessingMode")
            interruptProcessingModeValue = ""
            if interruptProcessingMode[0]:
               # There is a value set, so get it ...
               interruptProcessingModeValue = int(interruptProcessingMode[0])
               if interruptProcessingModeValue == 0:
                  warning = 'y'
                  # Check it is not disabled by being set to 0 ...
                  print "         WARNING: interruptProcessingMode (" + str(interruptProcessingModeValue) + ") will stop"
                  print "                  WebSphere or applications from issuing SQL CANCEL. This will prevent the"
                  print "                  webSphereDefaultQueryTimeout from interrupting SQL requests when they time out."
               if dsType == '4':
                  # If T4 and interruptProcessingMode is not set to 2, warn that the value set is ignored ...
                  if interruptProcessingModeValue != 2:
                     warning = 'y'
                     print "         WARNING: interruptProcessingMode (" + str(interruptProcessingModeValue) + ") will be ignored"
                     print "                  For a T4 datasource the effective value will always be 2."
                     print "                  (DB2BaseDataSource.INTERRUPT_PROCESSING_MODE_CLOSE_SOCKET)"
               else:
               # It must be type 2 so check it is not set to 2 ...
                  if interruptProcessingModeValue == 2:
                     warning = 'y'
                     print "         WARNING: interruptProcessingMode (" + str(interruptProcessingModeValue) + ") is incorrect"
                     print "                  for a T2 datasource. Allow interruptProcessingMode to default (set no value) or"
                     print "                  set interruptProcessingMode=1."
                     print "                  (DB2BaseDataSource.INTERRUPT_PROCESSING_MODE_STATEMENT_CANCEL)"


         # queryTimeoutInterruptProcessingMode  (applies to T4 connections only)
         # 1: DB2BaseDataSource.INTERRUPT_PROCESSING_MODE_STATEMENT_CANCEL
         #    For DB2 z/OS, if this option is set it is ignored and
         #    INTERRUPT_PROCESSING_MODE_CLOSE_SOCKET is used instead.
         # 2: DB2BaseDataSource.INTERRUPT_PROCESSING_MODE_CLOSE_SOCKET
         #    For DB2 z/OS T4 connections behavior depends on
         #    the setting of enableSysplexWLB
         #
         # enableSysplexWLB applies only to T4 connections.
         # If enableSysplexWLB is set to false, SQL code -4499 is thrown.
         # This is the default.
         # After a statement times out, the application must establish a
         # new connection before it can execute a new transaction.
         # If enableSysplexWLB = true the JDBC driver tries to re-establish
         # a connection and returns SQL code -30108 if
         # successful. However the driver does not execute the timed-out
         # SQL statements again.
         if queryTimeoutInterruptProcessingMode:
            printProperty("queryTimeoutInterruptProcessingMode")
            queryTimeoutInterruptProcessingModeValue = ""
            if queryTimeoutInterruptProcessingMode[0]:
               # A value is set so check it ...
               queryTimeoutInterruptProcessingModeValue = int(queryTimeoutInterruptProcessingMode[0])
               if (dsType == '4') and (queryTimeoutInterruptProcessingModeValue == 1):
                  warning = 'y'
                  # If there is a value, for T4 warn if it is set to 1 ...
                  print "         WARNING: queryTimeoutInterruptProcessingMode (" + str(queryTimeoutInterruptProcessingMode) + ") is ignored"
                  print "                  for a T4 datasource to DB2 z/OS. A value of 2 will be used instead."
                  print "                  (DB2BaseDataSource.INTERRUPT_PROCESSING_MODE_CLOSE_SOCKET)"
               else:
                  warning = 'y'
                  # For T2 datasources, if queryTimeoutInterruptProcessingMode is set, warn that it is ignored.
                  print "         WARNING: queryTimeoutInterruptProcessingMode (" + str(queryTimeoutInterruptProcessingModeValue) + ") but this property"
                  print "                  applies only to T4 datasources."

         # syncQueryTimeoutWithTransactionTimeout   Default = false       X
         # We just get the value here. The check is done under webSphereDefaultQueryTimeout.
         if syncQueryTimeoutWithTransactionTimeout:
            printProperty("syncQueryTimeoutWithTransactionTimeout")
            syncQueryTimeoutWithTransactionTimeoutValue = ""
            if syncQueryTimeoutWithTransactionTimeout[0]:
               # A value is set to check it ...
               syncQueryTimeoutWithTransactionTimeoutValue = str(syncQueryTimeoutWithTransactionTimeout[0])

         # timerLevelForQueryTimeOut
         # 1. DB2BaseDataSource.QUERYTIMEOUT_STATEMENT_LEVEL (Default)
         #    The IBM Data Server Driver for JDBC and SQLJ creates a Timer
         #    object for each Statement object. When the Statement object
         #    is closed, the driver deletes the Timer object.
         # 2. DB2BaseDataSource.QUERYTIMEOUT_CONNECTION_LEVEL (2)
         #    The IBM Data Server Driver for JDBC and SQLJ creates a Timer
         #    object for each Connection object. When the Connection object
         #    is closed, the driver deletes the Timer object.
         # -1 DB2BaseDataSource.QUERYTIMEOUT_DISABLED
         #    The JDBC driver does not create a Timer object to control
         #    query execution timeout
         # We just get the value here. The check is done under webSphereDefaultQueryTimeout.
         if timerLevelForQueryTimeOut:
            printProperty("timerLevelForQueryTimeOut")
            timerLevelForQueryTimeOutValue = ""
            if timerLevelForQueryTimeOut[0]:
               # A value is set, so get it ...  it is checked later.
               timerLevelForQueryTimeOutValue = int(timerLevelForQueryTimeOut[0])

         # webSphereDefaultQueryTimeout applies to T2 and T4 datasources.
         # webSphereDefaultQueryTimeout can cancel an SQL request that has
         # been running for too long.
         # If an SQL request is waiting for a lock the DB2 IRLMRWT system
         # parameter should interrupt the request. But if a request is
         # running but not waiting for a lock, DB2 may not interrupt it.
         # The application ought to specify a timeout when it makes SQL
         # calls but if it does not, webSphereDefaultQueryTimeout can be
         # set on a datasource so long running requests are timed-out.
         # The behavior of this property depends on some other properties.
         # a) interruptProcessingMode
         # b) queryTimeoutInterruptProcessingMode.
         # c) syncQueryTimeoutWithTransactionTimeout
         # In summary, if you wish to use webSphereDefaultQueryTimeout
         # you should not change the defaults settings for:
         # interruptProcessingMode and queryTimeoutInterruptProcessingMode.
         #
         # For JTA requests it could be a good idea to set
         # syncQueryTimeoutWithTransactionTimeout=true because this dynamically
         # alters the webSphereDefaultQueryTimeout to the time left before
         # the transaction timeout expires. This means that the
         # webSphereDefaultQueryTimeout should always expire before the
         # transaction timeout and that should prevent servant restarts.
         #
         if webSphereDefaultQueryTimeout:
            printProperty("webSphereDefaultQueryTimeout")
            if webSphereDefaultQueryTimeout[0]:
               # The property has a value set ...
               webSphereDefaultQueryTimeoutValue = int(webSphereDefaultQueryTimeout[0])
               if webSphereDefaultQueryTimeoutValue == 0:
                  warning = 'y'
               # The value is set to 0 which disables the webSphereDefaultQueryTimeout ...
                  print "         WARNING: webSphereDefaultQueryTimeout is set to 0 which disables this timeout."
                  print "                  Is this what you intended? Usually it is a good idea to set a value for"
                  print "                  webSphereDefaultQueryTimeout which is greater than 0 and less than the"
                  print "                  transaction_defaultTimeout (" + str(transactionDefaultTimeoutValue) + " secs)."
               if webSphereDefaultQueryTimeoutValue > transactionDefaultTimeoutValue:
                  warning = 'y'
               # SQL requests must time out before the transaction timeout is hit ...
                  print "         WARNING: webSphereDefaultQueryTimeout (" + str(webSphereDefaultQueryTimeoutValue) + ") is greater than the"
                  print "                  transaction_defaultTimeout (" + str(transactionDefaultTimeoutValue) + ")."
                  print "                  webSphereDefaultQueryTimeout should be less than the transaction_defaultTimeout."
                  print "                  In the ISC, transaction_defaultTimeout is the field 'Total transaction lifetime timeout'"
                  print "                  in a server's transaction service settings."
               if timerLevelForQueryTimeOutValue == -1:
                  warning = 'y'
               #  The timeLevelForQueryTimeout is disabled so webSphereDefaultQueryTimeout will not work ...
                  print "         WARNING: webSphereDefaultQueryTimeout (" + str(webSphereDefaultQueryTimeoutValue) + ") but timerLevelForQueryTimeOut (-1)"
                  print "                  which means that webSphereDefaultQueryTimeout is disabled."
                  print "                  Allow timerLevelForQueryTimeOut to default to 1 in order to use"
                  print "                  the webSphereDefaultQueryTimeout."
               if timerLevelForQueryTimeOutValue == 2:
                  warning = 'y'
               #  A value of 2 (DB2BaseDataSource.QUERYTIMEOUT_CONNECTION_LEVEL) means the timer is for the connection ...
                  print "         WARNING: webSphereDefaultQueryTimeout (" + str(webSphereDefaultQueryTimeoutValue) + ") timerLevelForQueryTimeOut (2)"
                  print "                  which means the query timeout lasts for the life of the connection."
                  print "                  This is probably not the best choice because connections in a connection pool"
                  print "                  are re-used by multiple SQL requests."
                  print "                  Allow timerLevelForQueryTimeOut to default to 1 in order to use"
                  print "                  the webSphereDefaultQueryTimeout at the request level."
               if syncQueryTimeoutWithTransactionTimeoutValue == 'false':
                  warning = 'y'
               # Suggest to set syncQueryTimeoutWithTransactionTimeout=true ...
                  print "         WARNING: webSphereDefaultQueryTimeout (" + str(webSphereDefaultQueryTimeoutValue) + ") but"
                  print "                  syncQueryTimeoutWithTransactionTimeout is defaulting or is set to false."
                  print "                  When using webSphereDefaultQueryTimeout it is usually best to set "
                  print "                  syncQueryTimeoutWithTransactionTimeout (true) so that for JTA requests"
                  print "                  webSphereDefaultQueryTimeout is dynamically changed to the time remaining within"
                  print "                  the JTA transaction. This is more flexible than a fixed webSphereDefaultQueryTimeout."
               if (dsType == '2') and ((interruptProcessingModeValue != "") or (interruptProcessingModeValue != 1)):
                  warning = 'y'
                  # Suggest to set interruptProcessingMode to 1 or allow to default ...
                  print "         WARNING: webSphereDefaultQueryTimeout (" + str(webSphereDefaultQueryTimeoutValue) + ") but interruptProcessingMode (" + str(interruptProcessingModeValue) + ")."
                  print "                  The property interruptProcessingMode should be allowed to default or be set to 1"
                  print "                  if you wish the webSphereDefaultQueryTimeout to be effective."
            else:
               warning = 'y'
               # It is not set, so suggest to set it ...
               print "         WARNING: webSphereDefaultQueryTimeout is not set. Usually it is a good idea to"
               print "                  set this property so SQL requests are not allowed to run forever."
               print "                  If you choose to set a value for webSphereDefaultQueryTimeout the values"
               print "                  of some other properties should be check. The following are suggested:"
               print "                  - interruptProcessingModeValue = 1 (or do not set and allow to default to 1)"
               print "                  - syncQueryTimeoutWithTransactionTimeout=true (default=false)"
               print "                  - timerLevelForQueryTimeOutValue = 1 (or do not set and allow to default to 1)"
         if (warning == 'n'):
            print "    No warnings generated for this datasource's custom properties"
      # End of datasource custom property checks

      # If this is not a datasource, check Connection Factory custom properties
      else:
         cfType = ""
         if isCmp == 'N':
            #-------------------------------------------------------------
            # Process only non-CMP connection factories
            #-------------------------------------------------------------
            try:
               if (AdminConfig.showAttribute(currentCF,"queueManager")):
                  #-------------------------------------------------------------
                  # If it is a WMQ CF and client mode, check servant JVM properties
                  #-------------------------------------------------------------
                  warning = 'n'
                  print "\n    " + AdminConfig.showAttribute(currentCF,"name") + " Connection Factory servant JVM properties at scope: " + scope
                  # This is a WMQ CF. Check for connection mode:
                  cfType = 'WMQ'
                  cfName = AdminConfig.showAttribute(currentCF, 'name')
                  cfTransport = AdminConfig.showAttribute(currentCF,"transportType")
                  cfQmgr = AdminConfig.showAttribute(currentCF,"queueManager")
                  if cfTransport and cfQmgr:
                     if (cfTransport.find("CLIENT") != -1):
                        # CF is using BINDINGS THEN CLIENT or CLIENT mode ...
                        printProperty("com.ibm.mq.cfg.TCP.Connect_Timeout")
                        printProperty("com.ibm.msg.client.config.location")
                        mqCfTCPConnectTimeout = getProperty("com.ibm.mq.cfg.TCP.Connect_Timeout")
                        mqCfClientConfigLocation = getProperty("com.ibm.msg.client.config.location")
                        if (mqCfTCPConnectTimeout[3] == 1) and (mqCfClientConfigLocation[3] == 1):
                           warning = 'y'
                           # Neither JVM property that might set com.ibm.mq.cfg.TCP.Connect_Timeout is set.
                           print "         WARNING: ConnectionFactory " + cfName + " to QMGR " + cfQmgr + " is using mode '" + cfTransport + "' but"
                           print "                  com.ibm.mq.cfg.TCP.Connect_Timeout is not set as a servant JVM custom property and"
                           print "                  com.ibm.msg.client.config.location does not set a path to a properties file."
                           print "                  This means that no socket connect timeout is set."
                           print "                  For client mode connections, consider setting servant JVM custom property"
                           print "                  com.ibm.mq.cfg.TCP.Connect_Timeout (secs) to a few seconds to avoid hung connect requests."
                        if (mqCfTCPConnectTimeout[3] == 1) and (mqCfClientConfigLocation[3] != 1):
                           warning = 'y'
                           print "         WARNING: ConnectionFactory " + cfName + " to QMGR " + cfQmgr + " is using mode '" + cfTransport + "'."
                           print "                  com.ibm.mq.cfg.TCP.Connect_Timeout is not set as a servant JVM custom property but"
                           print "                  com.ibm.msg.client.config.location specifies a path to a properties file."
                           print "                  Check that the properties file includes a value for Connect_Timeout (secs)."
                           print "                  For client mode connections, setting JVM custom property com.ibm.mq.cfg.TCP.Connect_Timeout"
                           print "                  or setting Connect_Timeout_Timeout in a properties file can prevent hung connect requests."
                  if (warning == 'n'):
                     print "    No warnings generated for WMQ Connection Factory servant JVM properties"
            except:
               # Not a WMQ CF so do nothing and go on to check CF custom properties
               pass
            #-------------------------------------------------------------
            # Get the Connection Factory custom properties
            #-------------------------------------------------------------
            listJ2EEResourceProperty = AdminConfig.list('J2EEResourceProperty', currentCF).split(lineSeparator)
            #-------------------------------------------------------------
            # For each property in cfcustproplist, set the property map to
            # the default values initially. Then see if the property has
            # a value set. If it does, and the value is not the same as
            # the default value, update the property map with the value
            # and remove the defaultFlag fom the property map.
            # Detect properties that are unique to different CF types
            # and set cfType variable accordingly.
            #-------------------------------------------------------------
            for n in range(len(cfcustproplist)):
               ivarx = cfcustproplist[n][0]
               idefx = cfcustproplist[n][1]
               imesx = cfcustproplist[n][2]
               idesx = cfcustproplist[n][3]
               setProperty(ivarx, idefx, "", "", "default")
               # Find the current value for this property ...
               for j2eeresource in listJ2EEResourceProperty:
                  if j2eeresource.startswith(ivarx + '(' ):
                     ovalue = AdminConfig.showAttribute(j2eeresource, "value")
                     if (ovalue) and (str(ovalue) != str(idefx)):
                        # Only put the set value in (and remove defaultFlag) if it differs from the default value
                        setProperty( ivarx, ovalue, imesx, scope)
                     # Based on the properties discovered, work out which type of CF this is ...
                     # The assumption is that the 3 properties tested below are unique to their RA.
                     if j2eeresource[0:7] == 'BusName':
                        # Note if the CF is JMS
                        cfType = 'JMS'
                     if j2eeresource[0:4] == 'ipic':
                        # Note if the CF is CTG ECI RA
                        cfType = 'CTG'
                     if j2eeresource[0:14] == 'IMSConnectName':
                        # Note if the CF is IMS TM RA
                        cfType = 'IMSTM'
                     if j2eeresource[0:10] == 'DriverType':
                        # Note if the CF is IMS DB RA
                        cfType = 'IMSDB'
                  #endif j2eeresource
               #endfor j2eeresource
            #endfor n
            if cfType != "JMS":
               # We do not process JMS so only put out the header line if this CF is not JMS
               print "\n    " + AdminConfig.showAttribute(currentCF,"name") + " Connection Factory custom properties at scope: " + scope

            #-------------------------------------------------------------
            # Now check the CF custom properties ...
            #-------------------------------------------------------------
            if cfType == 'CTG':
               #-------------------------------------------------------------
               # Analyse CICS ECI RA Connection Factory custom properties ...
               #-------------------------------------------------------------
               # First get all the properties for timeout-related custom properties
               #-------------------------------------------------------------
               connectionURL = getProperty("connectionURL")
               ipicHeartbeatInterval = getProperty("ipicHeartbeatInterval")
               serverName = getProperty("serverName")
               socketConnectTimeout = getProperty("socketConnectTimeout")
               #-------------------------------------------------------------
               # Check each property ...
               # For JCA resource adapters, although custom properties are
               # always defined, we are checking for both CICS and IMS
               # which have different required properties, so we can not
               # assume that a particular property exists in the CF.
               #-------------------------------------------------------------
               # First work out if this is a local-mode IPIC connection by
               # checking if a URL is coded for start of serverName.
               #-------------------------------------------------------------
               #
               warning = 'n'
               ipicLocal = 'N'
               if serverName:
                  printProperty("serverName")
                  if serverName[0]:
                     # The property has a value set ...
                     serverNameValue = str(serverName[0])
                     if serverNameValue[0:4] in ( 'tcp:', 'ssl:' ):
                        ipicLocal = 'Y'
                  else:
                     warning = 'y'
                     print "         WARNING: The serverName property is not set for this Connection Factory."
                     print "                  For a local-mode IPIC connection to CICS, set serverName in one of the formats below:"
                     print "                  protocol://hostname:port   (where 'protocol' is tcp: or ssl:)"
                     print "                  protocol://hostname:port#CICSAPPLID"
                     print "                  protocol://hostname:port#CICSAPPLIDQUALIFIER.CICSAPPLID"
               #-------------------------------------------------------------
               # Get the value of socketConnectTimeout
               #-------------------------------------------------------------
               if socketConnectTimeout:
                  printProperty("socketConnectTimeout")
                  if socketConnectTimeout[0]:
                     # The property has a value set ...
                     socketConnectTimeoutValue = int(socketConnectTimeout[0])
                     if (socketConnectTimeoutValue != 0) and (ipicLocal == 'Y'):
                        warning = 'y'
                     # If its an IPIC local-mode connection, socketConnectTimeout does not apply ...
                        print "         WARNING: socketConnectTimeout is set (" + str(socketConnectTimeoutValue) + " ms) but this is an IPIC local-mode"
                        print "                  connection so socketConnectTimeout does not apply to this connection."
               #-------------------------------------------------------------
               # Get the value of ipicHeartbeatInterval
               #-------------------------------------------------------------
               if ipicHeartbeatInterval:
                  printProperty("ipicHeartbeatInterval")
                  if ipicHeartbeatInterval[0]:
                     # The property has a value set ...
                     ipicHeartbeatIntervalValue = int(ipicHeartbeatInterval[0])
               #------------------------------------------------------------
               # Checks related to the connectionURL ...
               #-------------------------------------------------------------
               if connectionURL:
                  printProperty("connectionURL")
                  if connectionURL[0]:
                     # The property has a value set ...
                     connectionURLValue = str(connectionURL[0])
                     if connectionURLValue[0:4] in ( 'tcp:', 'ssl:' ) and (ipicLocal == 'N'):
                        # Must be a remote-mode connection ...
                        if serverName[0]:
                           pass
                        else:
                           warning = 'y'
                           print "         WARNING: The serverName property is not set for this Connection Factory."
                           print "                  For a remote-mode IPIC connection to CICS, set serverName"
                           print "                  to the name of the target CICS server that is defined in an"
                           print "                  IPICSERVER SECTION of the CTG Daemon configuration file."
                        if socketConnectTimeoutValue == 0:
                           warning = 'y'
                           # socketConnectTimeout is disabled which is not good for a remote-mode connection ...
                           print "         WARNING: This is a remote-mode connection but socketConnectTimeout=0 which means the"
                           print "                  timeout is disabled and requests could hang while waiting for a connection"
                           print "                  to the CTG daemon. A value between 1000 and 5000 ms is suggested."
                        elif socketConnectTimeoutValue < 1000:
                           warning = 'y'
                           # Check value is not < 1000 and warn if less in case value was coded in secs
                           print "         WARNING: The units for socketConnectTimeout are milliseconds but the value set"
                           print "                  is " + str(socketConnectTimeoutValue) + " which suggests the value"
                           print "                  was set as seconds rather than milliseconds. Check the value."
                        elif socketConnectTimeoutValue >= transactionDefaultTimeoutValuems:
                           warning = 'y'
                           # Do not wait for longer than the transaction_defaultTimeout ...
                           print "         WARNING: The socketConnectTimeout value (" + str(socketConnectTimeoutValue) + " ms) is greater than, or equal to the"
                           print "                  transasction_defaultTimeout (" + str(transactionDefaultTimeoutValuems) + "."
                           print "                  The value of socketConnectTimeout should be much less than the"
                           print "                  transasction_defaultTimeout. A value between 1000 and 5000 ms is suggested."
                     else:
                        # ConnectionURL is local:  If it is not IPIC local-mode, warn about DFHXCOPT
                        if ipicLocal == 'N':
                           warning = 'y'
                           print "         WARNING: This is a non-IPIC local-mode connection which means that the EXCI protocol"
                           print "                  is used to connect to CICS. Ensure that you have coded the TIMEOUT parameter"
                           print "                  in the CICS DFHXCOPT table so requests can be timed-out if CICS does not respond."
                        else:
                           # Must be an IPIC local-mode connection so check ipicHeartbeatInterval ...
                           if ipicHeartbeatIntervalValue < 30:
                              warning = 'y'
                              print "         WARNING: An ipicHeartbeatInterval of " + str(ipicHeartbeatInterval[0]) + " (secs) will cause heartbeats"
                              print "                  to be sent to CICS is a connection is idle for more than " + str(ipicHeartbeatInterval[0]) + " (secs)."
                              print "                  This may increase CPU overhead if connections are frequently idle for short periods."
                              print "                  Usually the default of 30 secs is a good value."
                           elif ipicHeartbeatIntervalValue > 60:
                              warning = 'y'
                              print "         WARNING: An ipicHeartbeatInterval of " + str(ipicHeartbeatInterval[0]) + " (secs) will cause heartbeats"
                              print "                  to be sent to CICS is a connection is idle for more than " + str(ipicHeartbeatInterval[0]) + " (secs)."
                              print "                  60 seconds is probably too long to wait before checking if the connection is no longer there."
                              print "                  Usually the default of 30 secs is a good value."
                           else:
                              pass
               else:
                  warning = 'y'
                  # No connectionURL set but there ought to be something ...
                  print "         WARNING: Property connectionURL has no value set."
                  print "                  Set it to local:, tcp:, or ssl:."
               if (warning == 'n'):
                  print "    No warnings generated for CTG Connection Factory custom properties"
            # end of CTG CF checking.
            # If it is an IMS CF put out a message ...
            if cfType[0:3] == 'IMS':
               print "            INFO: This is an " + cfType + " Resource Adapter Connection Factory. No timeout properties can be set"
               print "                  as custom properties on the Connection Factory. The application developer should be sure"
               print "                  to set executionTimeout (ms) and set socketTimeout (ms) if the connection is remote."
               print "                  These properties can be set on the IMSInteractionSpec object when making a request."
            if cfType == 'WMQ':
               print "            INFO: This is a " + cfType + " Resource Adapter Connection Factory. No timeout properties can be set"
               print "                  as custom properties on the Connection Factory. For client-mode connections, consider"
               print "                  setting JVM custom property com.ibm.mq.cfg.TCP.Connect_Timeout (secs)."

   # endif connection pool != None.

   # If not a datasource or Connection Factory Connection Pool, try a JMS CF Session Pool ...
   try:
      sessionPool = AdminConfig.showAttribute(currentCF, "sessionPool")
      if sessionPool != None:
         warning = 'n'
         # The session pool exists. Get and set the values ...
         print "\n    " + AdminConfig.showAttribute(currentCF,"name") + " Connection Factory session pool at scope: " + scope
         agedTimeoutValue = AdminConfig.showAttribute(sessionPool,"agedTimeout")
         setProperty("agedTimeout", agedTimeoutValue, "s", "")
         printProperty("agedTimeout")
         #
         connectionTimeoutValue = AdminConfig.showAttribute(sessionPool,"connectionTimeout")
         setProperty("connectionTimeout", connectionTimeoutValue, "s", "")
         printProperty("connectionTimeout")
         #
         reapTimeValue = AdminConfig.showAttribute(sessionPool,"reapTime")
         setProperty("reapTime", reapTimeValue, "s", "")
         printProperty("reapTime")
         #
         unusedTimeoutValue = AdminConfig.showAttribute(sessionPool,"unusedTimeout")
         setProperty("unusedTimeout", unusedTimeoutValue, "s", "")
         printProperty("unusedTimeout")
         if int(agedTimeoutValue) > 0:
            # Check that reapTimeout is set if agedTimeout is set ...
            if int(reapTimeValue) == 0:
               warning = 'y'
               print "         WARNING: agedTimeout inactive due to reapTime (" + str(reapTimeValue) + ")"
            else:
               if int(agedTimeoutValue) <= int(reapTimeValue):
                  warning = 'y'
                  print "         WARNING: agedTimeout should be greater than reapTime (" + str(reapTimeValue) + ")"
         if int(unusedTimeoutValue) > 0:
            # Check that reapTimeout is set if unusedTimeout is set ...
            if int(reapTimeValue) == 0:
               warning = 'y'
               print "         WARNING: unusedTimeout inactive due to reapTime (" + str(reapTimeValue) + ")"
            else:
               if int(unusedTimeoutValue) <= int(reapTimeValue):
                  warning = 'y'
                  print "         WARNING: unusedTimeout should be greater than reapTime (" + str(reapTimeValue) + ")"
         else:
            print "         WARNING: unusedTimeout should NOT be disabled by setting it to zero"
         if int(connectionTimeoutValue) > 0:
            transactionDefaultTimeoutValue = int(getProperty("transaction_defaultTimeout")[0])
            if (transactionDefaultTimeoutValue > 0) and (int(connectionTimeoutValue) >= transactionDefaultTimeoutValue):
               warning = 'y'
               print "         WARNING: connectionTimeout should be less than transaction_defaultTimeout (" + str(transactionDefaultTimeoutValue) + ")"
         if (warning == 'n'):
            print "    No warnings generated for this Session pool"
   except:
#     Likely that this Connection Factory has no session pool
      pass
# -------------------------------------------------------------------
# End of routine printConnectionFactpryV8
# -------------------------------------------------------------------
#
# -------------------------------------------------------------------
# printRA routine: Extract and print WMQ resource adapter properties
# -------------------------------------------------------------------
#
def printRA(currentRA, scope):

   global AdminConfig

   print "\n    " + AdminConfig.showAttribute(currentRA,"name") + " resource adapter at scope: " + scope
   #-------------------------------------------------------------
   # Check various resource adapter custom properties related to timeouts ...
   #-------------------------------------------------------------
   RAwarning = "n"
   RAPropertyList = AdminConfig.list('J2EEResourceProperty', currentRA).split(lineSeparator)
   #-------------------------------------------------------------
   # For each property in racustproplist, set the property map to
   # the default values initially. Then see if the property has
   # a value set. If it does, and the value is not the same as
   # the default value, update the property map with the value
   # and remove the defaultFlag fom the property map.
   #-------------------------------------------------------------
   for n in range(len(racustproplist)):
      ivarx = racustproplist[n][0]
      idefx = racustproplist[n][1]
      imesx = racustproplist[n][2]
      idesx = racustproplist[n][3]
      setProperty(ivarx, idefx, imesx, "", "default")
      # Find the current value for this property ...
      for j2eeresource in RAPropertyList:
         if j2eeresource.startswith(ivarx + '(' ):
            ovalue = AdminConfig.showAttribute(j2eeresource, "value")
            if (ovalue) and (str(ovalue) != str(idefx)):
               # Only put the set value in (and remove defaultFlag) if it differs from the default value
               setProperty( ivarx, ovalue, imesx, "")
         #endif j2eeresource
      #endfor j2eeresource
   #endfor n
   #
   # Check the WMQ RA custom properties ...
   #
   reconnectionRetryCount = getProperty("reconnectionRetryCount")
   reconnectionRetryInterval = getProperty("reconnectionRetryInterval")
   startupRetryCount = getProperty("startupRetryCount")
   startupRetryInterval = getProperty("startupRetryInterval")
   #
   if reconnectionRetryCount:
      printProperty("reconnectionRetryCount")
      reconnectionRetryCountValue = int(reconnectionRetryCount[0])
      if reconnectionRetryCount[3] != 1:
         # The property has a value set. Check it is not 0 ...
         if (reconnectionRetryCountValue == 0):
            # The value is set to 0 which disables the reconnectionRetryCount ...
            RAwarning = "y"
            print "         WARNING: reconnectionRetryCount is set to 0 which disables reconnection retry."
            print "                  Is this what you intended? Usually it is a good idea to set a value for"
            print "                  reconnectionRetryCount so WAS can reconnect to a QMGR that may have restarted."
   if reconnectionRetryInterval:
      # check the interval ...
      printProperty("reconnectionRetryInterval")
      reconnectionRetryIntervalValue = int(reconnectionRetryInterval[0])
      if reconnectionRetryInterval[3] != 1:
         # The property has a value set ...
         if (reconnectionRetryIntervalValue == 0):
            # The value is set to 0 which disables the reconnectionRetryInterval ...
            RAwarning = "y"
            print "         WARNING: reconnectionRetryInterval is set to 0 which disables reconnection retry."
            print "                  Is this what you intended? Usually it is a good idea to set a value for"
            print "                  reconnectionRetryInterval so WAS can reconnect to a QMGR that may have restarted."
      if (reconnectionRetryIntervalValue < 1000):
         RAwarning = "y"
         print "         WARNING: reconnectionRetryInterval(" + str(reconnectionRetryIntervalValue) + ") is less than 1000 which suggests that"
         print "                  that the value may have been set in seconds instead of millisecs."
   if (reconnectionRetryCountValue > 0) and (reconnectionRetryIntervalValue > 0):
      # Calculate when retry gives up. There should always be some values here ...
      reconnectionRetryIntervalValueSecs = reconnectionRetryIntervalValue/1000.
      reconnectionRetryEnds = reconnectionRetryCountValue * reconnectionRetryIntervalValueSecs
      if (reconnectionRetryEnds < 300):
         RAwarning = "y"
         print "         WARNING: reconnectionRetryCount = " + str(reconnectionRetryCountValue) + " and reconnectionRetryInterval = " + str(reconnectionRetryIntervalValue) + "."               + "."
         print "                  This means that reconnection attempts will end after only " + str(reconnectionRetryEnds) + " secs."
         print "                  Usually it is a good idea to continue reconnect attempts for at least 15 minutes (900 secs)."

   if startupRetryCount:
      printProperty("startupRetryCount")
      startupRetryCountValue = int(startupRetryCount[0])
      if startupRetryCount[3] != 1:
         # The property has a value set. Check it is not 0 ...
         if (startupRetryCountValue == "0"):
            # The value is set to 0 which disables the startupRetryCount ...
            RAwarning = "y"
            print "         WARNING: startupRetryCount is set to 0 which disables start-up retry."
            print "                  Usually it is a good idea to set startupRetryCount to the same value as"
            print "                  reconnectionRetryCount (" + str(reconnectionRetryCountValue) + ")."
      else:
         RAwarning = "y"
         print "         WARNING: startupRetryCount is defaulting to 0 which disables start-up retry."
         print "                  Usually it is a good idea to set startupRetryCount to the same value as"
         print "                  reconnectionRetryCount (" + str(reconnectionRetryCountValue) + ")."
   if startupRetryInterval:
      # check the interval ...
      printProperty("startupRetryInterval")
      startupRetryIntervalValue = int(startupRetryInterval[0])
      if startupRetryInterval[3] != 1:
         # The property has a value set ...
         if (startupRetryIntervalValue == 0):
            # The value is set to 0 which disables the startupRetryInterval ...
            RAwarning = "y"
            print "         WARNING: startupRetryInterval is set to 0 which disables start-up retry."
            print "                  Is this what you intended? Usually it is a good idea to set a value for"
            print "                  startupRetryInterval so WAS can reconnect to a QMGR that may not have been"
            print "                  started when the WAS server was starting."
         if (startupRetryIntervalValue < 1000):
            RAwarning = "y"
            print "         WARNING: startupRetryInterval(" + str(startupRetryIntervalValue) + ") is less than 1000 which suggests that"
            print "                  that the value may have been set in seconds instead of millisecs."
      if (startupRetryCountValue > 0) and (startupRetryIntervalValue > 0):
         # Calculate when retry gives up. There should always be some values here ...
         startupRetryIntervalValueSecs = startupRetryIntervalValue/1000.
         startupRetryEnds = startupRetryCountValue * startupRetryIntervalValueSecs
         if (startupRetryEnds < 300):
            RAwarning = "y"
            print "         WARNING: startupRetryCount = " + str(startupRetryCountValue) + " and startupRetryInterval = " + str(startupRetryIntervalValue) + "."
            print "                  This means that connection attempts will end after only " + str(startupRetryEnds) + " secs."
            print "                  Usually it is a good idea to continue reconnect attempts for at least 15 minutes (900 secs)."
      if (reconnectionRetryCountValue != startupRetryCountValue):
         # Suggest they should be the same ...
         RAwarning = "y"
         print "         WARNING: reconnectionRetryCount = " + str(reconnectionRetryCountValue) + " and startupRetryCount = " + str(startupRetryCountValue) + "."
         print "                  For consistent behavior during start-up and runtime, usually set these to the same value."
      if (reconnectionRetryIntervalValue != startupRetryIntervalValue):
         # Suggest they should be the same ...
         RAwarning = "y"
         print "         WARNING: reconnectionRetryInterval = " + str(reconnectionRetryIntervalValue) + " and startupRetryInterval = " + str(startupRetryIntervalValue) + "."
         print "                  For consistent behavior during start-up and runtime, usually set these to the same value."

   return ( RAwarning )

# -------------------------------------------------------------------
# printSIB routine: Extract and Check SIB message engine properties
# -------------------------------------------------------------------
#
def printSIB( currentSIB ):

   global AdminConfig

   print "\n    " + AdminConfig.showAttribute(currentSIB, "name") + " Service Integration Bus."
   #-------------------------------------------------------------
   # Check each message engine in the bus ...
   #-------------------------------------------------------------
   adjunctRegionStartSynchronized = getProperty("adjunct_region_start_synchronized")
   adjunctRegionStartSibWaittime = getProperty("adjunct_region_start_sib_waittime")
   if adjunctRegionStartSibWaittime[0] != "":
      adjunctRegionStartSibWaittimeValue = int(adjunctRegionStartSibWaittime[0])
   else:
      adjunctRegionStartSibWaittimeValue = ""
   adjunctRegionStartSibAbend = getProperty("adjunct_region_start_sib_abend")
   sibName = AdminConfig.showAttribute(currentSIB, "name")
   if (adjunctRegionStartSynchronized[3] == 1):
      # There is at least one bus defined but adjunctRegionStartSynchronized is defaulting
      print "         WARNING: adjunct_region_start_synchronized is not set and defaults to 0 (disabled)"
   if (adjunctRegionStartSynchronized[0] == 'false'):
      # There is at least one bus defined but adjunctRegionStartSynchronized is set to false
      print "         WARNING: adjunct_region_start_synchronized = 0 (disabled)"
   if (adjunctRegionStartSynchronized[3] == 1) or (adjunctRegionStartSynchronized[0] == 'false'):
      # if not set suggest to set it ...
      print "                  so even if any message engines are marked as critical the server will begin"
      print "                  processing without waiting for message engines to initialize."
      print "                  Usually it is best to set adjunct_region_start_synchronized=1 so the server waits for"
      print "                  any critical message engines to initialize before becoming 'Open for e-business'."
   if (adjunctRegionStartSynchronized[0] == 'true'):
      # if set, check the other related properties ...
      if (adjunctRegionStartSibAbend[0] == '1'):
         print "         WARNING: adjunct_region_start_sib_abend=1 which means that if any critical message engines"
         print "                  have not initialized before adjunct_region_start_sib_waittime has expired,"
         print "                  the entire server will be abended. Is this what you intended?"
      if (adjunctRegionStartSibWaittimeValue == 0):
         # StartSynchronized requested but waittime is disabled so it has no effect:
         print "         WARNING: adjunct_region_start_sib_waittime=0 (disabled)."
      if (adjunctRegionStartSibWaittimeValue == ""):
         # StartSynchronized requested but waittime property is set to blank so defaults to 0:
         print "         WARNING: adjunct_region_start_sib_waittime property is defined with no value so is disabled."
      if (adjunctRegionStartSibWaittimeValue in (0, "")):
         print "                  This means that although you have set adjunct_region_start_synchronized=1, the server will"
         print "                  not wait for critical message engines to initialize before becoming 'Open for e-business'."

      elif (adjunctRegionStartSibWaittimeValue < 300):
         # Usually 2 servants will take more than 300 secs to initialize ...
         print "         WARNING: adjunct_region_start_sib_waittime=" + str(adjunctRegionStartSibWaittimeValue) + "  is a rather short time to wait for all"
         print "                  critical message engines to initialize. The value of adjunct_region_start_sib_waittime should"
         print "                  be longer than the adjunct initialization time to allow time for the message engines to start."
         print "                  Also remember that the adjunct start-up time increases as more applications are deployed."
   # Now check if the message engine(s) in the bus are marked critical ...
   meAttrs = '[-bus ' + sibName + ']'
   meList = AdminTask.listSIBEngines(meAttrs).split(lineSeparator)
   if meList[0]:
      for meId in meList:
          # There could be a bus with no meId
          meName = AdminConfig.showAttribute(meId, "name")
          isCritical = getMeCritical ( meId )
          if verboseFlag != 'false':
             print "       Message engine " + meName + " : sib.property.isMECritical = " + isCritical
          if isCritical == "":
             print "         WARNING: Message engine " + meName + " custom property 'sib.property.isMECritical' is not set"
          elif isCritical == "":
             print "         WARNING: Message engine " + meName + " custom property sib.property.isMECritical=false"
          if (isCritical in ( "" , "false")):
             print "                  which means that this message engine is not marked as critical."
             print "                  When the cell contains Service Integration Buses, it is usually a good idea to prevent"
             print "                  the server from accepting work until the SIB message engines have fully started."
             print "                  This is done my setting message engine custom property sib.property.isMECritical=true"
             print "                  and WebSphere environment variable adjunct_region_start_synchronized=1."
             print "                  See Techdoc http://www.ibm.com/support/techdocs/atsmastr.nsf/WebIndex/WP102450"
          else:
             # Put out warning if StartSynchronized not set ...
             if (adjunctRegionStartSynchronized[0] != '1'):
                print "         WARNING: Message engine " + meName + " of Service Integration Bus " + sibName
                print "                  is marked critical but adjunct_region_start_synchronized is not set to 1 so the server"
                print "                  will not wait for critical message engines to initialize before becoming 'Open for e-business'."
             # Put out warning if SibWaitTime is 0 or blank ...
             if (adjunctRegionStartSibWaittimeValue in (0, "")):
                print "         WARNING: Message engine " + meName + " of Service Integration Bus " + sibName
                print "                  is marked critical but adjunct_region_start_sib_waittime is not set so the server will"
                print "                  not wait for critical message engines to initialize before becoming 'Open for e-business'."
   else:
      print "         WARNING: No message engine found for Service Integration Bus " + sibName + "."
# -------------------------------------------------------------------
# End of printSIB routine
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# getDsConfForCPId routine: Get the confid of thea datasource that is
# parent of a given connection pool confid.
# -------------------------------------------------------------------
#
def getDsConfForCpId(cpId):
   dsIds = AdminConfig.list("DataSource").split(lineSeparator)
   dsfound = 'n'
   for dsId in dsIds:
      dsCpId = AdminConfig.showAttribute(dsId,'connectionPool')
      if dsCpId == cpId:
         dsfound = 'y'
         return dsId
   if dsfound == 'n':
         dsId = None
         return dsId
# -------------------------------------------------------------------
# getDsType routine: Return the type of datasource (type 2 or type 4)
# -------------------------------------------------------------------
def getDsType(dsId):

   global AdminConfig

   driverType = ''
   listJ2EEResourceProperty = AdminConfig.list('J2EEResourceProperty', dsId).split(lineSeparator)
   for j2eeresource in listJ2EEResourceProperty:
      if j2eeresource.startswith('driverType'):
         driverType = AdminConfig.showAttribute(j2eeresource, "value")
         return( driverType )
      #endif j2eeresource
   #endfor j2eeresource

# -------------------------------------------------------------------
# getMECritical routine: Return whether Message Engine marked critical
# -------------------------------------------------------------------
#
def getMeCritical( meId ):
   # Returns value of ME custom property sib.property.isMECritical
   # If not set, default is false
   meCritical = ""
   mePropertyList = AdminConfig.list("Property", meId).split(lineSeparator)
   if mePropertyList[0]:
      for mePropertyId in mePropertyList:
          mePropertyName = AdminConfig.showAttribute(mePropertyId, 'name')
          if (mePropertyName == 'sib.property.isMECritical'):
             meCritical = AdminConfig.showAttribute(mePropertyId, 'value')
   return meCritical
# -------------------------------------------------------------------
# getListenerPortIds routine: Return a list of Listener ports.
# -------------------------------------------------------------------
#
def getListenerPortIds( server ):
   serverId = AdminConfig.getid("/Server:" + server + "/")
   mls = AdminConfig.list('MessageListenerService', serverId)
   lports = AdminConfig.showAttribute(mls,'listenerPorts')
   return lports
# -------------------------------------------------------------------
# getObjectsOfType routine: Return a python list of objectids of all
# objects of the given type in the given scope
# -------------------------------------------------------------------
#
def getObjectsOfType(typename, scope = None):
    """Return a python list of objectids of all objects of the given type in the given scope
    (another object ID, e.g. a node's object id to limit the response to objects in that node)
    Leaving scope default to None gets everything in the Cell with that type.
    ALWAYS RETURNS A LIST EVEN IF ONLY ONE OBJECT.
    """
    m = "getObjectsOfType:"
    if scope:
        #sop(m, "AdminConfig.list(%s, %s)" % ( repr(typename), repr(scope) ) )
        return _splitlines(AdminConfig.list(typename, scope))
    else:
        #sop(m, "AdminConfig.list(%s)" % ( repr(typename) ) )
        return _splitlines(AdminConfig.list(typename))
# -------------------------------------------------------------------
# _splitlines routine: to split lines
# -------------------------------------------------------------------
#
def _splitlines(s):
  rv = [s]
  if '\r' in s:
    rv = s.split('\r\n')
  elif '\n' in s:
    rv = s.split('\n')
  if rv[-1] == '':
    rv = rv[:-1]
  return rv
# -------------------------------------------------------------------
# checkQueuePercentTimeout routine: Check the current settings of
# control_region_xxxx_queue_timeout_percent for protocol xxxx.
# -------------------------------------------------------------------
#
def checkQueuePercentTimeout( protocol ):
#     Get the property names and values for this protocol ...
      qptwarning = 'n'
      if protocol.lower() == "http":
         queueTimeoutPercentName = "control_region_http_queue_timeout_percent"
         protocolTimeoutName = "protocol_http_timeout_output"
      elif protocol.lower() == "https":
         queueTimeoutPercentName = "control_region_https_queue_timeout_percent"
         protocolTimeoutName = "protocol_https_timeout_output"
      elif protocol.lower() == "iiop":
         queueTimeoutPercentName = "control_region_iiop_queue_timeout_percent"
         protocolTimeoutName = "control_region_wlm_dispatch_timeout"
      elif protocol.lower() == "mdb":
         queueTimeoutPercentName = "control_region_mdb_queue_timeout_percent"
         protocolTimeoutName = "control_region_mdb_request_timeout"
      elif protocol.lower() == "sip":
         queueTimeoutPercentName = "control_region_sip_queue_timeout_percent"
         protocolTimeoutName = "protocol_sip_timeout_output"
      elif protocol.lower() == "sips":
         queueTimeoutPercentName = "control_region_sips_queue_timeout_percent"
         protocolTimeoutName = "protocol_sips_timeout_output"
      else:
         print "  ERROR: Protocol not supported by checkQueuePercentTimeout function"
#     endif protocol
#     Check the queueTimeoutPercent in relation to the dispatch timeout ...
      queueTimeoutPercent = getProperty( queueTimeoutPercentName )
      queueTimeoutPercentValue = int(getProperty( queueTimeoutPercentName )[0])
      protocolTimeoutValue = int(getProperty( protocolTimeoutName )[0])
      print " "
      printProperty( queueTimeoutPercentName)
      queueTimeout = (queueTimeoutPercentValue*protocolTimeoutValue)/100
      if queueTimeout < 1:
         queueTimeout = 1
      if (queueTimeoutPercent[3] == 1):
         # Property is defaulting ...
         qptwarning = 'y'
         print "         WARNING: " + queueTimeoutPercentName + " is defaulting to 99% which means that requests"
      if (queueTimeoutPercentValue == 99):
         # Property is set to the default ...
         qptwarning = 'y'
         print "         WARNING: " + queueTimeoutPercentName + " is set to 99 which means that requests"
      if (queueTimeoutPercent[3] == 1) or (queueTimeoutPercentValue == 99):
         print "                  are allowed to wait in the dispatch queue until 99% of the dispatch timeout."
         print "                  Consequently, when the request is eventually dispatched it is likely to time-out soon after."
         print "                  How long do you think it is reasonable to allow requests to queue for execution?"
         print "                  Consider setting a percentage that will time-out requests that have queued for more than about 30 secs."
         print "                  See https://www.ibm.com/support/techdocs/atsmastr.nsf/WebIndex/WP101233"
      else:
         print "            INFO: " + queueTimeoutPercentName + " = " + str(queueTimeoutPercentValue) + "% and"
         print "                  " + protocolTimeoutName + " = " + str(protocolTimeoutValue) + " secs means that requests will be "
         print "                  timed-out after they have queued for about " + str(queueTimeout) +  " secs. Is that what you intended?"
      #endif
      return ( qptwarning )
#end checkQueuePercentTimeout function
#
# -------------------------------------------------------------------
# List of WAS environment variables that the script may check
# The second tuple is the default value. The third is a description.
# The description is not used by this script but may be useful if you
# wish to use this table in a script which sets variables too.
# -------------------------------------------------------------------
#
envvarlist = [
('adjunct_region_start_synchronized','0/false','','For message engines marked critcal, delay server open status until the critical MEs are fully active.'),
('adjunct_region_start_sib_waittime','300','s','Time server waits for critical MEs to start before taking action.'),
('adjunct_region_start_sib_abend','0/false','','0=issue WTO. 1=Abend server if critical MEs are not started after sib_waittime.'),
('control_region_dreg_on_no_srs','0/false','','Issue PAUSELISTENERS if there are no servants'),
('control_region_http_requeue_enabled','0/false','','Requeue HTTP requests with affinity to another servant if their affinity servant is down'),
('control_region_http_queue_timeout_percent','99','%','Reject work when this percentage of protocol_http_timeout_output is reached'),
('control_region_https_queue_timeout_percent','99','%','Reject work when this percentage of protocol_https_timeout_output is reached'),
('control_region_iiop_queue_timeout_percent','99','%','Reject work when this percentage of control_region_wlm_dispatch_timeout is reached'),
('control_region_mdb_queue_timeout_percent','99','%','Reject work when this percentage of control_region_mdb_request_timeout is reached'),
('control_region_sip_queue_timeout_percent','99','%','Reject work when this percentage of protocol_sip_timeout_output is reached'),
('control_region_sips_queue_timeout_percent','99','%','Reject work when this percentage of protocol_sips_timeout_output is reached'),
('control_region_timeout_delay','0','s','Time allowed for requests to end when a servant is scheduled for restart due to timeout'),
('control_region_timeout_dump_action','TRACEBACK','','Dump action when control region detects a timeout'),
('control_region_timeout_save_last_servant','0/false','','1=do not terminate last servant if all servants are scheduled to restart due to timeouts.'),
('protocol_accept_http_work_after_min_srs','1/true','','Allow HTTP work to start before min servants is reached'),
('protocol_accept_iiop_work_after_min_srs','0/false','','Allow IIOP work to start before min servants is reached'),
('protocol_http_timeout_output','300','s','HTTP dispatch timeout'),
('protocol_http_timeout_output_recovery','SERVANT','','SERVANT: Schedule servant for restart when timeout. SESSION: stall threads that timeout'),
('protocol_https_timeout_output','300','s','HTTPS dispatch timeout'),
('protocol_https_timeout_output_recovery','SERVANT','','SERVANT: Schedule servant for restart when timeout. SESSION: stall threads that timeout'),
('protocol_sip_timeout_output','300','s','sip dispatch timeout'),
('protocol_sip_timeout_output_recovery','SERVANT','','SERVANT: Schedule servant for restart when timeout. SESSION: stall threads that timeout'),
('protocol_sips_timeout_output','300','s','sips dispatch timeout'),
('protocol_sips_timeout_output_recovery','SERVANT','','SERVANT: Schedule servant for restart when timeout. SESSION: stall threads that timeout'),
('server_region_request_cputimeused_limit','0','ms','CPU limit for a request'),
('server_region_cputimeused_dump_action','TRACEBACK','','Dump action when a servant thread exceeds the cputimeused limit'),
('server_region_http_stalled_thread_dump_action','TRACEBACK','','Dump action when a servant http thread exceeds the stalled thread threshold'),
('server_region_https_stalled_thread_dump_action','TRACEBACK','','Dump action when a servant https thread exceeds the stalled thread threshold'),
('server_region_iiop_stalled_thread_dump_action','TRACEBACK','','Dump action when a servant iiop thread exceeds the stalled thread threshold'),
('server_region_mdb_stalled_thread_dump_action','TRACEBACK','','Dump action when a servant mdb thread exceeds the stalled thread threshold'),
('server_region_sip_stalled_thread_dump_action','TRACEBACK','','Dump action when a servant sip thread exceeds the stalled thread threshold'),
('server_region_sips_stalled_thread_dump_action','TRACEBACK','','Dump action when a servant sips thread exceeds the stalled thread threshold'),
('server_region_stalled_thread_threshold_percent','0','%','Percentage of servants threads allowed to stall before servant is scheduled for restart'),
('wlm_classification_file','','','Path to the WLM classification XML file'),
('wlm_stateful_session_placement_on','0/false','','Set to true to enable even distribution of load across servants')
]
# -------------------------------------------------------------------
#  List of timeout-related datasource custom properties
# -------------------------------------------------------------------
dscustproplist = [
# The second tuple is the default value. The third is a description.
# The fourth tuple is whether the property is required. The fifth is the java type for the value.
('blockingReadConnectionTimeout' ,
 '' ,
 's' ,
 'The amount of time in seconds before a connection socket read times out. This property applies only to type \
  4 connectivity, and affects all requests that are sent to the database server after a connection is \
  successfully established. The default value is 0, which means that there is no timeout.' ,
  'false' ,
 'java.lang.Integer') ,
('currentLockTimeout' ,
 '' ,
 's' ,
 'Specifies whether the database waits for a lock when the lock cannot be obtained immediately. \
 Possible values are between -1 and 32767, inclusive. The default behavior is to not wait for a lock.' ,
 'false' ,
 'java.lang.Integer') ,
('enableSysplexWLB' ,
 '' ,
 '' ,
 'Specifies whether Sysplex workload balancing is enabled (1/true) or not (0/false).' ,
 'false' ,
 'java.lang.Boolean') ,
('keepAliveTimeOut' ,
 '' ,
 's' ,
 'Specifies the maximum time in seconds before an unresponsive connection is detected as no longer alive. Default 15' ,
 'false' ,
 'java.lang.Integer') ,
('interruptProcessingMode',
 '' ,
 '' ,
 '0: Interrupts disabled. 1: (For DB2 LUW) Interrupts enabled. 2: (For DB2 z/OS) Interrupts enabled. Default 2' ,
 'false' ,
 'java.lang.Integer') ,
('loginTimeout' ,
 '0' ,
 's' ,
 'The maximum time in seconds to wait for the data source object to connect to the database. \
 A value of 0 means that the timeout value is the default system timeout value.' ,
 'false' ,
 'java.lang.Integer') ,
('queryTimeoutInterruptProcessingMode' ,
 '' ,
 '' ,
 'Specifies whether the IBM Data Server Driver for JDBC and SQLJ cancels the SQL statement or closes the \
 underlying connection when the query timeout interval for a Statement object expires.' ,
 'false' ,
 'java.lang.Integer') ,
('syncQueryTimeoutWithTransactionTimeout' ,
 '' ,
 '' ,
 'Use the time remaining (if any) in a JTA transaction as the default query timeout for SQL statements. \
 The default is false. The feature depends on driver and DB support for java.sql.Statement.setQueryTimeout. \
 For DB2 type 2 on z/OS, the following data source properties impact support for query timeout: \
 interruptProcessingMode, queryTimeoutInterruptProcessingMode. \
 Refer to the JDBC driver documentation for more information.' ,
 'false' ,
 'java.lang.Boolean') ,
('timerLevelForQueryTimeOut' ,
 '' ,
 '' ,
 '2: QUERYTIMEOUT_CONNECTION_LEVEL. 1: QUERYTIMEOUT_STATEMENT_LEVEL. -1: (default) QUERYTIMEOUT_DISABLED.' ,
 'false' ,
 'java.lang.Integer') ,
('webSphereDefaultQueryTimeout' ,
 '' ,
 's' ,
 'Sets a default query timeout, which is the number of seconds (0 means infinite) that a \
 SQL statement may execute before timing out. This default value is overridden during a JTA \
 transaction if custom property syncQueryTimeoutWithTransactionTimeout is enabled. \
 This feature depends on JDBC driver and database support for java.sql.Statement.setQueryTimeout. \
 For DB2 type 2 on z/OS, the following data source properties impact support for query timeout: \
 interruptProcessingMode, queryTimeoutInterruptProcessingMode. \
 Refer to the JDBC driver documentation for more information' ,
 'false' ,
 'java.lang.Integer')
]
# -------------------------------------------------------------------
#  List of timeout-related J2C Connection Factory custom properties
# -------------------------------------------------------------------
cfcustproplist = [
# The second tuple is the default value. The third is a description.
# The fourth tuple is whether the property is required. The fifth is the java type for the value.
('BusName' ,
 '' ,
 '' ,
 'The Service Integration Bus name' ,
  'false' ,
 'java.lang.String') ,
('connectionURL' ,
 'local:' ,
 '' ,
 'If local: it is a local-mode connection.\
  If tcp: or ssl: it is a remote mode connection through TCPIP.' ,
  'false' ,
 'java.lang.String') ,
('ipicHeartbeatInterval',
 '30' ,
 's' ,
 'In local mode, this parameter sets the time in seconds that an IPIC connection must \
  be inactive before heartbeats are sent to the CICS server.' ,
 'false' ,
 'java.lang.Integer') ,
('serverName',
 '' ,
 '' ,
 'For IPIC connections, the protocol:hostname:port of the target CICS. \
  For non-IPIC remote connection, the ServerName entry in the CTG daemon \
  configuration. For non-IPIC local: connections, any name for the target CICS.' ,
 'false' ,
 'java.lang.String') ,
('socketConnectTimeout' ,
 '0' ,
 'ms' ,
 'When connecting to a Gateway daemon in remote mode, this value is the maximum amount of time in \
  milliseconds that the Java Client application allows for the socket to connect successfully. \
  For a local-mode IPIC connection, this value is the maximum amount of time allowed for the \
  socket connection to made successfully. If the protocol is not tcp or IPIC this property is ignored.' ,
 'false' ,
 'java.lang.String'),
('DriverType' ,
 '' ,
 '' ,
 'The type of driver connectivity to use for an IMS DB RA Connection Factory',
 'false' ,
 'java.lang.String'),
('IMSConnectName' ,
 '' ,
 '' ,
 'The job name of the target IMS Connect server',
 'false' ,
 'java.lang.String'),
]
# -------------------------------------------------------------------
# List of WMQ Resource adapter properties we want to check.
# The second tuple is the default value. The third is the units. The fourth is the description.
# The fifth tuple is whether the property is required. The sixth is the java type for the value.
# -------------------------------------------------------------------
racustproplist = [
('reconnectionRetryInterval' ,
 '300000' ,
 'ms' ,
 'The time, in milliseconds, that the resource adapter waits before trying to reconnect to a WebSphere MQ queue manager.' ,
  'false' ,
 'java.lang.String') ,
('reconnectionRetryCount' ,
 '5' ,
 '' ,
 'The maximum number of attempts made by the resource adapter to reconnect to a WebSphere MQ queue manager if a connection fails.' ,
  'false' ,
 'java.lang.String') ,
('startupRetryInterval' ,
 '30000' ,
 'ms' ,
 'The default sleep time between start-up connection attempts (in milliseconds)' ,
  'false' ,
 'java.lang.String') ,
('startupRetryCount' ,
 '0' ,
 '' ,
 'The number of times to try and connect a MDB on start-up, if the queue manager is not running \
  when the application server is started.' ,
  'false' ,
 'java.lang.String')
]
#-----------------------------------------------------------------------
# End of sub-soutines
#-----------------------------------------------------------------------
# Main:  Start of main processing
#-----------------------------------------------------------------------
print "\nlistTimeoutsV85: Starting"
#
#  Validate arguments
#
errorOccurred = 0

if (len(sys.argv) != 1) and (len(sys.argv) != 2):
   print "\n   Syntax: wsadmin -lang jython -f ListTimeouts.py <Scope> <Verbose>"
   print "      Scope:   Either a cluster long name or a server long name."
   print "               Or 'allclus' for all clusters, or 'allserv' for all servers."
   print "      Verbose  An optional string to request reporting of all timeout-related properties."
   errorOccurred = 1
else:
   if len(sys.argv) == 1:
      verboseFlag = "false"
   else:
      verboseFlag = "true"
   targetScope = sys.argv[0]
   if targetScope  == 'allclus':
      targetScopeLong = 'All clusters in cell'
   elif targetScope  == 'allserv':
      targetScopeLong = 'All servers in cell'
   else:
      targetScopeLong = targetScope
   #endif

#  Print out arguments
   print "\n   Input parameters:"
   print "   Scope:      " + targetScopeLong
   print "   Verbose:    " + verboseFlag

   if targetScope == 'allserv':
      print "\n      Note:  Option 'allserv' was passed. The 'allserv' option should be used only when"
      print "             the cell contains managed servers but no clusters. If the cell has clusters,"
      print "             pass option 'allclus' to check timeout properties for all cluster members."
      print "             With option 'allserv', any properties set at cluster scope are ignored."

#
# Read in all the conection factories
# We need them all whether we are dealing with one server or all of them
#
   allV4Factories = AdminConfig.list("WAS40DataSource").split(lineSeparator)
   allV8Factories = AdminConfig.list("ConnectionFactory").split(lineSeparator)
   allRAs = AdminConfig.list("J2CResourceAdapter").splitlines()
   allSIBs = AdminTask.listSIBuses().split(lineSeparator)
#
# Process a single cluster or all clusters
#
   allClusters = AdminConfig.list( 'ServerCluster' ).split(lineSeparator)
   clusterFound = 'n'
   for thisClusterId in allClusters:
      if thisClusterId:
        thisClusterName = AdminConfig.showAttribute(thisClusterId, "name")
        if targetScope == "allclus":
           # Process all clusters in the cell ...
           clusterFound = 'y'
           checkCluster(thisClusterId)
        elif targetScope == "allserv":
           # Process all servers in the cell ...
           clusterFound = 'y'
           targetType = 'server'
           allServers = AdminConfig.list("Server").split(lineSeparator)
           for thisServer in allServers:
              thisServerName = AdminConfig.showAttribute(thisServer, "name")
  #           Ignore node agents and DMGRs
              if (thisServerName == "nodeagent") or (thisServerName == "dmgr"):
                 continue
              checkServer(thisServerName, thisServerName, "server")
        else:
  #        Check only the cluster name passed in ...
           if targetScope == thisClusterName:
              clusterFound = 'y'
              checkCluster(thisClusterId)
# If the cluster name passed in was not found, in the outer 'for' loop above,
# maybe it was a server name so try calling checkServer directly.
   if clusterFound == 'n':
      print "   Cluster " + targetScope + " was not found in cell " + cellName
      print "   Will try treating "  + targetScope + " as a server name ..."
      targetType = 'server'
      checkServer( targetScope, targetScope, "server")
#

if not errorOccurred:
   print "\nlistTimeoutsV85: Completed"
else:
   print "\nlistTimeoutsV85: Failed"
