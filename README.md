# logicTester

This is a POC (proof-of-concept) of a simple but configurable 'SSI'-logic I.C-tester,

The idea is to split the low-level measuring tasks from the hight-level data 
generation and comparison tasks. The low-level functionality is implemented in
an Arduino sketch which communicates with the high-level functionality build in
Python. The Python script does contain the I.C. data, this is read from a text-
based configuration file. As long as the behaviour at the output pins can be defined
in Boolean logic, the chip can be tested. 

The current version is limited to stateless gates and inverters. So far I didn't 
try to define a machine-parsable notation for I.C.s with clocked or register
functionality. A limitation of the Arduino sketch is that it currently only 
supports 14 and 16 pin I.C.s and the switch is manual. 

Only the logic behaviour is tested, not wether the I.C. conforms to TTL or CMOS 
specifications.
