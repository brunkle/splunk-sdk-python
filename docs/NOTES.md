## HTTP proxies

HTTPS and HTTP proxy is supported by adding proxyhost=<hostname> and 
proxyport=<proxyport> to the CLI (or .splunkrc file) or the **kwargs in the
connect API. host and port should still continue to address the splunkd server.

## Socket timeout

Socket timeout is supported in the following manner:

* If not specified, the system default is used.

* If specified in the connect api **kwargs (timeout=<value>) the initial
  connection and subsequent get/post/delete/etc operations all use the timeout
  value.

* If specified on the connect api, individual get/post/delete can be 
  individually overridden by adding timeout=<value>.


## SSL Certificate:

Add a ca file specification to the connect request. For example:

     opts.kwargs['ca_file'] = "/home/wcolgate/ca.pem"
     service = connect(**opts.kwargs)

Where the ca.pem file is in the standard form. Below is the pem file for a
test splunk server:

-----BEGIN CERTIFICATE-----
MIICdTCCAd4CCQDAsfQhOfrWaTANBgkqhkiG9w0BAQUFADB/MQswCQYDVQQGEwJV
UzELMAkGA1UECBMCQ0ExFjAUBgNVBAcTDVNhbiBGcmFuY2lzY28xDzANBgNVBAoT
BlNwbHVuazEXMBUGA1UEAxMOU3BsdW5rQ29tbW9uQ0ExITAfBgkqhkiG9w0BCQEW
EnN1cHBvcnRAc3BsdW5rLmNvbTAeFw0wNjA3MjQxNzEyMTlaFw0xNjA3MjExNzEy
MTlaMH8xCzAJBgNVBAYTAlVTMQswCQYDVQQIEwJDQTEWMBQGA1UEBxMNU2FuIEZy
YW5jaXNjbzEPMA0GA1UEChMGU3BsdW5rMRcwFQYDVQQDEw5TcGx1bmtDb21tb25D
QTEhMB8GCSqGSIb3DQEJARYSc3VwcG9ydEBzcGx1bmsuY29tMIGfMA0GCSqGSIb3
DQEBAQUAA4GNADCBiQKBgQDJmb55yvam1GqGgTK0dfHXWJiB0Fh8fsdJFRc5dxBJ
PFaC/klmtbLFLbYuXdC2Jh4cm/uhj1/FWmA0Wbhb02roAV03Z3SX0pHyFa3Udyqr
9f5ERJ0AYFA+y5UhbMnD9zlhs7J8ucub3XvA8rn79ejkYtDX2rMQWPNZYPcrxUEh
iwIDAQABMA0GCSqGSIb3DQEBBQUAA4GBAKW37NFwTikJOMo9Z8cjmJDz9wa4yckB
MlEA1/s6k6OmzZH0gkAssLstRkBavlr1uIBPZ2Jfse6FjoJ5ekC1AoXkInwmCspW
GTVCoe8rwhU0xaj0GsC+wA3ykL+UKuXz6iE3oDcnLr0qxiNT2OxdTxz+EB9T0ynR
x/F2KL1hdfCR
-----END CERTIFICATE-----
