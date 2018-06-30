# from pysnmp.hlapi import *
from pysnmp.hlapi.asyncore import *

# 解析MIB获取到的信息
class ParseMibInfo(object):
    def __init__(self):
        pass


class GetSnmp(object):

    def __init__(self, oid):
        self.engin = SnmpEngine()
        self.community = CommunityData("xi'an-ctc-5328-201408")
        self.udp = UdpTransportTarget(('111.111.111.111', 161))
        self.mib = ObjectType(ObjectIdentity(oid))

    def get_snmp_table(self):
        try:
            info = next(nextCmd(self.engin, self.community, self.udp, ContextData(), self.mib, lexicographicMode=False))
        except Exception:
            info = None
        return info


def callBack(snmpEngine, sendRequestHandle, errorIndication, errorStatus, errorIndex, varBinds, cbCtx):
    if errorIndex:
        print(errorIndex)
    if errorStatus:
        print(errorStatus)
    print(varBinds[0][0])
    # 返回None则停止获取，返回1或者True则继续获取
    return 1

from pysnmp.proto.rfc1902 import OctetString
engin = SnmpEngine()

nextCmd(engin, CommunityData("xi'an-ctc-5328-201408"),UdpTransportTarget(("111.111.111.111", 161)), ContextData(), ObjectType(ObjectIdentity(".111.111.111.111")), cbFun=callBack)
nextCmd(engin, CommunityData("xi'an-ctc-5328-201408"),UdpTransportTarget(("111.111.111.111", 161)), ContextData(), ObjectType(ObjectIdentity('.111.111.111.111')), cbFun=callBack)

engin.transportDispatcher.runDispatcher()


