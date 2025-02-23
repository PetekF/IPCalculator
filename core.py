import math

# Parsing and conversion

def parseOctet(octet:str, binaryMode = False) -> int:
    base = 10
    if binaryMode:
        base = 2

    try:
        parsed = int(octet, base)
        return parsed
    except ValueError:
        return -1

def parseIpAddress(ipAddress: str, binaryMode = False) -> []:
    octets = ipAddress.split('.')
    if len(octets) != 4:
        return []

    for i in range(4):
        octets[i] = parseOctet(octets[i], binaryMode)

    return octets

def serializeOctet(octet:int, binaryMode = False) -> str:
    fmt = 'd'
    if binaryMode:
        fmt = 'b'

    formatted = format(octet, fmt)

    if binaryMode:
        filler = ''
        for i in range(8 - len(formatted)):
            filler = filler + '0'

        formatted = filler + formatted

    return formatted

def serializeIpAddress(ipAddress: [], binaryMode = False) -> str:
    for i in ipAddress:
        ipAddress[i] = serializeOctet(i, binaryMode)

    return '.'.join(ipAddress)

# Validation

def isValidIpOctet(octet:int) -> bool:
    return octet >= 0 and octet <= 255

def isValidIpAddress(ipAddress:[]) -> bool:
    if len(ipAddress) != 4:
        return False

    isValid = True
    for i in range(4):
        if not isValidIpOctet(ipAddress[i]):
            isValid = False
            break

    return isValid

def isValidSubnetOctet(octet:int) -> bool:
    return octet in [255, 254, 252, 248, 240, 224, 192, 128, 0]

def isValidSubnetMask(subnetMask:[]) -> bool:
    if len(subnetMask) != 4:
        return False

    isValid = True
    prevOctet = 255 #Fake initial value to make the loop work

    for i in range(4):
        currentOctet = subnetMask[i]
        currentNetworkBits = networkBitsInOctetValue(currentOctet)

        if not isValidSubnetOctet(currentOctet) or currentNetworkBits > 0 and prevOctet != 255:
            isValid = False
            break
        prevOctet = currentOctet

    return isValid

# Address calculations

def networkBitsInOctetValue(octetValue:int) -> int:
    if octetValue not in [255, 254, 252, 248, 240, 224, 192, 128, 0]:
        return -1

    return int(8 - math.log(256 - octetValue) / math.log(2))

def networkBitsInSubnetMask(subnetMask:[]) -> int:
    prevOctet = 255  # Fake initial value to make the loop work
    networkBits = 0

    for i in range(4):
        currentOctet = subnetMask[i]
        currentNetworkBits = networkBitsInOctetValue(currentOctet)

        if currentNetworkBits == -1 or currentNetworkBits > 0 and prevOctet != 255:
            networkBits = -1
            break

        networkBits += currentNetworkBits
        prevOctet = currentOctet

    return networkBits

def networkBitsToOctetValue(networkBits:int) -> int:
    if networkBits < 0 or networkBits > 8:
        return -1

    return pow(2, 8) - pow(2, 8 - networkBits)

def calculateSubnetMaskFromShortMask(shortMask:int) -> []:
    if shortMask < 0 or shortMask > 32:
        return []

    mask = []
    fullOctets = int(shortMask / 8)
    lastOctetBits = shortMask % 8

    for i in range(fullOctets):
        mask.append(255)

    mask.append(networkBitsToOctetValue(lastOctetBits))

    for i in range(4-fullOctets):
        mask.append(0)

    return mask

def calculateNetworkAddress(ip:[], subnet:[]) -> []:
    networkAddress = []
    for i in range(4):
        networkAddress.append(ip[i] & subnet[i])

    return networkAddress

def calculateBroadcastAddress(ip:[], subnet:[]) -> []:
    broadcastAddress = []
    for i in range(4):
        broadcastAddress.append(ip[i] | (255 - subnet[i]))

    return broadcastAddress

def calculateFirstAndLastAddress(networkAddress:[], broadcastAddress:[]) -> tuple[[], []]:
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

def calculateAddressRange(lowerAddress:[], higherAddress:[]) -> int:
    firstAddress = (lowerAddress[0] << 24 | lowerAddress[1] << 16 | lowerAddress[2] << 8 | lowerAddress[3])
    lastAddress = (higherAddress[0] << 24 | higherAddress[1] << 16 | higherAddress[2] << 8 | higherAddress[3])

    return lastAddress - firstAddress + 1