//xxxxxS JOB (ACCTNO,ROOM),'JAVA8 Switch',CLASS=A,MSGLEVEL=(1,1),        
// MSGCLASS=G,REGION=0M,NOTIFY=&SYSUID                                    
//*XEQ SX00                                                               
//STEP1 EXEC PGM=BPXBATCH                                                 
//STDIN DD DUMMY                                                          
//STDOUT DD SYSOUT=*                                                      
//STDERR DD SYSOUT=*                                                      
//SYSOUT DD SYSOUT=*                                                      
//SYSPRINT DD SYSOUT=*                                                    
//STDENV DD *                                                             
/*                                                                        
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
/*                                                                        
//                                                                        
//VERIFY EXEC PGM=BPXBATCH                                                
//STDIN DD DUMMY                                                          
//STDOUT DD SYSOUT=*                                                      
//STDERR DD SYSOUT=*                                                      
//SYSOUT DD SYSOUT=*                                                      
//SYSPRINT DD SYSOUT=*                                                    
//STDENV DD *                                                             
/*                                                                        
//STDPARM DD *                                                            
sh                                                                        
CID="a" ;                                                                 
CNR="9"  ;                                                                
WROOT="/data/WebSphere"                                                   
WDIR=$WROOT"/wx"$CID"domain/wx"$CID$CNR"2node/as/profiles/default/bin";   
$WDIR/managesdk.sh -getNewProfileDefault         ;                        
$WDIR/managesdk.sh -getCommandDefault             ;                       
$WDIR/managesdk.sh -listEnabledProfileAll          ;                      

