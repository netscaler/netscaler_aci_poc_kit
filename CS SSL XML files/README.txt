# The MIT License (MIT)

# Copyright (c) 2015 Citrix Systems, Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

This document lists steps on how to create a ServiceGraph on APIC from ground up using XMLs provided below.
It can be adapted to use in other environment by modifying few values as required.
This holds good for physical Domain for non virtualized servers.  (MPX or VMs in SDX)


This can also be VMM environment (vCenter controlling VPX, client and servers  on ESX ) by making more changes  (in future XMLs can be provided)
This document assume the following 
APIC is up and running FCS+6 release (1.0 (4h) or above (as of now Cisco 1.1 (3f), is the latest image.
Netscaler DevicePackage :DevicePackage-10.1-129.62.zip

Netscaler SDX is up and running with 2 NS instances and HA is formed between them.
In this example, I have the following IP …

NS1: 10.217.194.206
NS2 :10.217.194.207
Mgmt SNIP : 10.217.194.208

APIC Controller IPs : 
APIC1: 10.217.194.197
APIC3: 10.217.194.198
APIC3: 10.217.194.199


10/1 of NS is connected to ACI switch leaf1 (id 101) port  eth1/5
10/2 of NS is connected to ACI switch leaf1 (id 101) port  eth1/6

Test client is connected to : ACI switch leaf1 (id 101) port eth1/7
Test server is connected to : ACI switch leaf1 (id 101) port eth1/8

Client network : 2.2.2.x
Server network: 1.1.1.x


Objects names used in XMLs : 
Tenant: tenant_parik1
L3 network context : cokectx1
Client side bridge domain: BD2
Server side bridge domain: BD1
Physical Domain for DUT:  phys_DUT
Physical Domain for Clients,Servers : phys_BW
Dynamic Vlan pool for DUT :VLAN4DUT (Vlan Range : 601-700)  
Static Vlan pool for Clients/Server : VLAN4BWS (Vlan Range : 1001-1200) 
In this sample graph , I have statically assigned vlan-1001 (in app EPG) to Client side, vlan-1002 (to web EPG)  to server side 


Application Profile: AP1
Client side EPG: client
Server side EPG: server  (All Netscaler Parameters go into this EPG)
Contract : webCtrct_CS
ServiceGraph : WebGraph_CS_SSL_AP1
ServiceGraph Function Node: Node_CS_SSL (of type ContentSwitching)

You can either run all the steps in a single batch script like this ..
./request.py request_CS_SSL.cfg   
#APIC IP :10.217.194.197 used in this .cfg script

Or you can run individual XML scripts using this ..

./post_xml.py  <XML script>  <APIC IP>

For example: 
./post_xml.py Tenant.xml  10.217.194.197  
./post_xml.py CreateCDev_HA.xml  10.217.194.197
./post_xml.py CreateLDevVip_HA.xml  10.217.194.197


Brief description of what individual XMLs do …

1) CreatePhysDomP_DUT.xml
This is where Physical Domain phys_DUT is created and assigned vlan pool VLAN4DUT

2) CreatePhysDomP_Client_Server.xml
This is where Physical Domain phys_BW is created and assigned clan pool VLAN4BWS
 
3) InfraNodePolicy_Client_Server.xml
This is where Ports connected to Client/Server are opened/enabled at Leaf1 (id: 101). eth1/5, and eth1/6 

4) InfraNodePolicy_DUT.xml
This is where Ports connected to DUT are opened/enabled at Leaf1 (id: 101). eth1/7, and eth1/8 

5) CreateVlanNamespace.xml
This is where VLAN pools  VLAN4DUT, VLAN4BWS

#Upto here is the APIC infra xmls..
#Now rest of the config is done within Tenant space .
#At this stage DevicePackage should be uploaded either APIC GUI or XML (see commented line inside request_CS_SSL.cfg )

6) Tenant.xml
This is where tenant tenant_parik1, network context : cokectx1, Bridge Domains: BD1,BD2 are created

#Steps 7,8,9 are steps to register NS (Standalone or HA pair) into Tenant space. In APIC GUI It is part of Create L4-L7 Devices in a Tenant.
7) CreateLDevVip_HA.xml
Assign  SNIP as logical ADC Cluster ,Give Login Credentials, enable NS features and modes et all.

8) CreateCDev_HA.xml
Assign NSIPs, Assign Interfaces for NS devices, Give Login Credentials et all.

9) CreateLIf_HA.xml
Create Logical Interface representing client/side side and representing HA as one logical  interface ADC cluster.

10) CreateAppProfile_cs_ssl_ap1.xml
Create Application Profile AP1, create EPGs client, server, assign Bridge Domains,Subnet IPs to EPGs, assign client/server side vlans to EPGs
Create all the required folders which represent a client/server side SNIPs,CS vip with lb vips with services and the cs policies bound to it

11) CreateDeviceSelectionPolicy_CS_SSL_ap1.xml
Assign the above created Device to the servicegroup. 

12) CreateContract_CS_SSL_ap1.xnl
Create a contract.

13) CreateGraph_CS_SSL_ap1.xml
Create a ServiceGraph with Function Node of type ContentSwitching.

14) AttachGraphToContract_CS_SSL_ap1.xml
Attach Graph to contract.

Once the above steps are done .. Check the following in APIC GUI
In Tenant (tenant_parik1)  —> L4-L7 Services  —> L4-L7 Devices 
15) Check for ADC Device ADCCluster1 created and Configuration state is Stable

In Tenant  (tenant_parik1) —> L4-L7 Services —> L4-L7 Service Graph Template
16) Graph WebGraph_CS_SSL is created

In Tenant (tenant_parik1) - Application Profiles —> 
17 AP1  with two EPGs client,server are created (Verify NS parameters in EPG server  —> L4-L7 ServiceParameters

If there are no Faults in config, then appropriate entries in Deployed Graph Instances and Deployed Devices will be seen.
Also relevant config (Vlans, CS vip, lb vips, services, CS policies, SNIP et all ) in NS will be populated. 


Actual config pushed on Netscaler.

add service cssvc1 1.1.10.111 HTTP 80 
add service cssvc2 1.1.10.112 HTTP 80 
add service cssvc3 1.1.10.113 HTTP 80 

add lb vserver cslb1 HTTP 0.0.0.0 0 
add lb vserver cslb2 HTTP 0.0.0.0 0 
add lb vserver cslb3 HTTP 0.0.0.0 0 

bind lb vserver cslb1 cssvc1
bind lb vserver cslb2 cssvc2
bind lb vserver cslb3 cssvc3

add cs policy cspol1_html -rule "HTTP.REQ.URL.CONTAINS("html")"
add cs policy cspol2_txt -rule "HTTP.REQ.URL.CONTAINS("txt")"

add cs vserver cs_ssl_ap1 SSL 2.2.20.106 443 

add ssl certKey certkey3 -cert rsaserver4096.pem -key rsaserver4096.key
bind ssl vserver cs_ssl_ap1 -certkeyName certkey3

bind cs vserver cs_ssl_ap1 -policyName cspol1_html -targetLBVserver cslb1 -priority 101
bind cs vserver cs_ssl_ap1 -policyName cspol2_txt -targetLBVserver cslb2 -priority 102
bind cs vserver cs_ssl_ap1 -lbvserver cslb3







