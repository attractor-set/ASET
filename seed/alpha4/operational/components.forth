: OBSERVE-UNKNOWN  ( state evidence -- state )  UNKNOWN? OBSERVE ;
: RECOGNIZE-ALLOW  ( state evidence -- state )  UNKNOWN? LOCAL-ALLOW! ;
: RECOGNIZE-BLOCK  ( state evidence -- state )  UNKNOWN? LOCAL-BLOCK! ;
: PRESERVE-UNKNOWN ( state -- state )  UNKNOWN? NOP ;
: PRESERVE-ALLOW   ( state -- state )  ALLOW? NOP ;
: PRESERVE-BLOCK   ( state -- state )  BLOCK? NOP ;
