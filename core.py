import math

# Validators and converters

def isValidIPOctet(octet:str, binaryMode = False) -> bool:
    base = 10
    if binaryMode:
        base = 2

    try:
        octetNum = int(octet, base)
    except ValueError:
        return False

    return octetNum >= 0 and octetNum <= 255

def isValidIPAddress(ip:str, binaryMode = False) -> bool:
    octets = ip.split('.')

    if len(octets) != 4:
        return False

    for seg in octets:
        if not isValidIPOctet(seg, binaryMode):
            return False

    return True

#TODO: decimalToBinaryOctet
def octetToBinaryOctet(octet:str) -> str:
    if not isValidIPOctet(octet):
        return ''

    num = int(octet, 10)
    formatted = format(num, 'b')

    filler = ''
    for i in range(8 - len(formatted)):
        filler = filler + '0'

    formatted = filler + formatted

    return formatted

#TODO: binaryToDecimalOctet
def binaryOctetToOctet(binaryOctet:str) -> str:
    if not isValidIPOctet(binaryOctet, True):
        return ''

    num = int(binaryOctet, 2)
    formatted = format(num, 'd')

    return formatted

# Proper core functions

def networkBitsToOctetValue(networkBits:int) -> int:
    if networkBits < 0 or networkBits > 8:
        return -1

    return pow(2, 8) - pow(2, 8 - networkBits)

def networkBitsInOctetValue(octetValue:int) -> int:
    if octetValue not in [255, 254, 252, 248, 240, 224, 192, 128, 0]:
        return -1

    return int(8 - math.log(256 - octetValue) / math.log(2))

# THIS IS WRONG APPROACH!
# Core 'engine' shouldn't take into account the format user input. It should
# do its work using its own data types for parameters. Other methods
# have to mediate between core and user input and convert data from one format
# to another
def calculateNetworkAddress(ipAddress:str, subnetMask:str) -> str:
    ip = ipAddress.split('.')
    subnet = subnetMask.split('.')

    for i in range(4):
        ip[i] = int(ip[i])
        subnet[i] = int(subnet[i])

    network = _calculateNetworkAddress(ip, subnet)
    return '.'.join(network)

def _calculateNetworkAddress(ip:[], subnet:[]) -> []:
    networkAddress = []
    for i in range(4):
        networkAddress.append(ip[i] & subnet[i])

    return networkAddress

def calculateBroadcastAddress(ipAddress:str, subnetMask:str) -> str:
    ip = ipAddress.split('.')
    subnet = subnetMask.split('.')

    for i in range(4):
        ip[i] = int(ip[i])
        subnet[i] = int(subnet[i])

    broadcast = _calculateBroadcastAddress(ip, subnet)
    return '.'.join(broadcast)

def _calculateBroadcastAddress(ip:[], subnet:[]) -> []:
    # networkAddress = calculateNetworkAddress(ip, subnet)
    #
    # broadcastAddress = []
    # for i in range(4):
    #     broadcastAddress.append(networkAddress[i] | (255 - subnet[i]))

    broadcastAddress = []
    for i in range(4):
        broadcastAddress.append(ip[i] | (255 - subnet[i]))

    return broadcastAddress

# def firstAndLastUsefulAddress(ipAddress:str, subnetMask:str) -> tuple[str, str]:

def _firstAndLastUsefulAddress(ip:[], subnet:[]) -> tuple[[], []]:
    networkAddress = _calculateNetworkAddress(ip, subnet)
    broadcastAddress = _calculateBroadcastAddress(ip, subnet)

    networkAddressNum = (
            networkAddress[0] << 24
            | networkAddress[1] << 16
            | networkAddress[2] << 8
            | networkAddress[3])

    firstAddressNum = networkAddressNum + 1

    firstAddress = []
    firstAddress.append(firstAddressNum >> 24 & 0xFF)
    firstAddress.append(firstAddressNum >> 16 & 0xFF)
    firstAddress.append(firstAddressNum >> 8 & 0xFF)
    firstAddress.append(firstAddressNum & 0xFF)

    broadcastAddressNum = (
            broadcastAddress[0] << 24
            | broadcastAddress[1] << 16
            | broadcastAddress[2] << 8
            | broadcastAddress[3])

    lastAddressNum = broadcastAddressNum - 1

    lastAddress = []
    lastAddress.append(lastAddressNum >> 24 & 0xFF)
    lastAddress.append(lastAddressNum >> 16 & 0xFF)
    lastAddress.append(lastAddressNum >> 8 & 0xFF)
    lastAddress.append(lastAddressNum & 0xFF)

    return firstAddress, lastAddress