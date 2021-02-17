//xxxxT JOB (ACCTNO,ROOM),'JAVA8 DM,NODES',CLASS=A,MSGLEVEL=(1,1),     
// MSGCLASS=G,REGION=0M,NOTIFY=&SYSUID,USER=UWXAA                        
/*XEQ ST00                                                               
//STEP1 EXEC PGM=BPXBATCH                                                
//STDIN DD DUMMY                                                         
//STDOUT DD SYSOUT=*                                                     
//STDERR DD SYSOUT=*                                                     
//SYSOUT DD SYSOUT=*                                                     
//SYSPRINT DD SYSOUT=*                                                   
//STDENV DD *                                                            
/*                                                                       
//* Description                                                          
//* CID variable = Cell name                                             
//* CNR variable = Cell id                                               
//* WROOT variable = WAS root directory                                  
//* WDIR variable = WAS directory for actual node to be configured       
//* JVM variable = Java version which needs to be set                    
//* parameters of managesdk.sh command                                   
//* -setNewProfileDefault = Changes the SDK name that is currently       
//* configured for all profiles that are created with manageprofiles.sh  
//* -setCommandDefault = Changes the SDK name that script commands in    
//* the app_server_root/bin, app_client_root/bin, or plugins_root/bin    
//* directory are enabled to use when no profile is specified by         
//* command and when no profile is defaulted by the command              
//* -enableProfileAll = Enables all profiles in an installation to use a 
//* specified SDK name                                                   
//* set SDK for dmgr,command default for dmgr and profile default        
//* for dmgr.Set SDK for node,command default for node51 and profile     
//* default for node51                                                   
//* Instead of using managesdk.sh you can use INSDKEX and INSDKFAL       
//STDPARM DD *                                                           
sh                                                                       
CID="x"  ;                                                               
CNR="x"   ;                                                              
WROOT="/data/WebSphere"    ;                                             
WDIR=$WROOT"/wx"$CID"domain/wx"$CID$CNR"0node/dm/bin";                   
JVM="1.8_64" ;                                                           
echo "set SDK for dmgr:";                                                
echo "-----------------";                                                
$WDIR/managesdk.sh -setNewProfileDefault -sdkname $JVM  ;                
$WDIR/managesdk.sh -setCommandDefault -sdkname $JVM  ;                   
$WDIR/managesdk.sh -enableProfile -sdkname $JVM -profileName default     
-user c49677 -password ;                                                 
echo "set SDK for Node"$CNR"1:";                                         
echo "------------------------";                                         
WDIR=$WROOT"/wx"$CID"domain/wx"$CID$CNR"1node/as/profiles/default/bin";  
$WDIR/managesdk.sh -setNewProfileDefault -sdkname $JVM  ;                
$WDIR/managesdk.sh -setCommandDefault -sdkname $JVM  ;                   
$WDIR/managesdk.sh -enableProfile -sdkname $JVM -profileName default     
-user xxxxx -password xxxxxx;                                                 
/*                                                                       
//VERIFYDM EXEC PGM=BPXBATCH                                             
//STDIN DD DUMMY                                                         
//STDOUT DD SYSOUT=*                                                     
//STDERR DD SYSOUT=*                                                     
//SYSOUT DD SYSOUT=*                                                    
//SYSPRINT DD SYSOUT=*                                                  
//STDENV DD *                                                           
/*                                                                      
//* List current SDK settings on dmgr and node 51                       
//STDPARM DD *                                                          
sh    ;                                                                 
CID="xxx"  ;                                                              
CNR="xxx"   ;                                                             
WROOT="/data/WebSphere"    ;                                            
WDIR=$WROOT"/wx"$CID"domain/wx"$CID$CNR"0node/dm/bin";                  
$WDIR/managesdk.sh -getNewProfileDefault         ;                      
$WDIR/managesdk.sh -getCommandDefault             ;                     
$WDIR/managesdk.sh -listEnabledProfileAll          ;                    
WDIR=$WROOT"/wx"$CID"domain/wx"$CID$CNR"1node/as/profiles/default/bin"; 
$WDIR/managesdk.sh -getNewProfileDefault         ;                      
$WDIR/managesdk.sh -getCommandDefault             ;                     
$WDIR/managesdk.sh -listEnabledProfileAll          ;                    
//                                                                      
//C49677X JOB (ACCTNO,ROOM),'JAVA8 52',CLASS=A,MSGLEVEL=(1,1),          
// MSGCLASS=G,REGION=0M,NOTIFY=&SYSUID,USER=UWXAA                       
/*XEQ SX00                                                              
//STEP1 EXEC PGM=BPXBATCH                                               
//STDIN DD DUMMY                                                        
//STDOUT DD SYSOUT=*                                                    
//STDERR DD SYSOUT=*                                                    
//SYSOUT DD SYSOUT=*                                                    
//SYSPRINT DD SYSOUT=*                                                  
//STDENV DD *                                                           
/*                                                                      
//* Set SDK for node,command default for node52 and profile             
//* default for node52                                                  
//STDPARM DD *                                                          
sh                                                                      
CID="x" ;                                                               
CNR="x"  ;                                                              
JVM="1.8_64" ;                                                          
WROOT="/data/WebSphere" ;                                               
echo "set SDK for Node"$CNR"2:";                                        
echo "------------------------";                                        
WDIR=$WROOT"/wx"$CID"domain/wx"$CID$CNR"2node/as/profiles/default/bin"; 
$WDIR/managesdk.sh -setNewProfileDefault -sdkname $JVM  ;               
$WDIR/managesdk.sh -setCommandDefault -sdkname $JVM  ;                  
$WDIR/managesdk.sh -enableProfile -sdkname $JVM -profileName default    
-user xxxxx -password xxxxx;                                                
/*                                                                      
//VERIFY52 EXEC PGM=BPXBATCH                                            
//STDIN DD DUMMY                                                        
//STDOUT DD SYSOUT=*                                                    
//STDERR DD SYSOUT=*                                                    
//SYSOUT DD SYSOUT=*                                                    
//SYSPRINT DD SYSOUT=*                                                  
//STDENV DD *                                                           
/*                                                                      
//* List current SDK settings on node 52                                
//STDPARM DD *                                                            
sh                                                                        
CID="x" ;                                                                 
CNR="x"  ;                                                                
WROOT="/data/WebSphere"                                                   
WDIR=$WROOT"/wx"$CID"domain/wx"$CID$CNR"2node/as/profiles/default/bin";   
$WDIR/managesdk.sh -getNewProfileDefault         ;                        
$WDIR/managesdk.sh -getCommandDefault             ;                       
$WDIR/managesdk.sh -listEnabledProfileAll          ;                      
