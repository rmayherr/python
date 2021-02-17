
---
Keystore/Truststore

AdminTask.createKeyStore('[-keyStoreName xx_test -scopeName (cell):????ell:(node):????1node:(server):????t -keyStoreDescription -keyStoreLocation safkeyring:///?????ns -keyStoreType JCERACFKS -keyStoreInitAtStartup false -keyStoreReadOnly true -keyStoreStashFile false -keyStoreUsage SSLKeys ]')
AdminTask.listKeyStores('[-all true -keyStoreUsage SSLKeys ]')
----
JSSE

AdminTask.createSSLConfig('[-alias xxxtest_jsse -type JSSE -scopeName (cell):???ell:(node):??node:(server):??t -keyStoreName NodeDefaultKeyStore -keyStoreScopeName (cell):???cell:(node):???ode -trustStoreName NodeDefaultTrustStore -trustStoreScopeName (cell):???ell:(node):??node -serverKeyAlias "???T" -clientKeyAlias "??T" ]')
AdminTask.listSSLConfigs('[-all true -displayObjectName true ]')
----
Tlsv1.2

AdminTask.modifySSLConfig('[-alias ???_test_jsse -scopeName (cell):??ell:(node):??node:(server):??t -keyStoreName NodeDefaultKeyStore -keyStoreScopeName (cell):???ell:(node):???1node -trustStoreName NodeDefaultTrustStore -trustStoreScopeName (cell):??cell:(node):???node -jsseProvider IBMJSSE2 -sslProtocol SSL_TLSv2 -clientAuthentication false -clientAuthenticationSupported false -securityLevel HIGH -enabledCiphers ]')
AdminTask.listSSLConfigs('[-all true -displayObjectName true ]')

----
Outbound

AdminTask.createDynamicSSLConfigSelection('[-dynSSLConfigSelectionName ???test -scopeName (cell):????cell:(node):????node:(server):???1wxt -dynSSLConfigSelectionDescription "from aaa to bbc" -dynSSLConfigSelectionInfo *,hostname.com,9443 -sslConfigName aaa_test_jsse -sslConfigScope (cell):???cell:(node):????1node:(server):???wxt -certificateAlias "????T" ]')
AdminTask.listDynamicSSLConfigSelections('[-all true ]')

                    