import math

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

def binaryOctetToOctet(binaryOctet:str) -> str:
    if not isValidIPOctet(binaryOctet, True):
        return ''

    num = int(binaryOctet, 2)
    formatted = format(num, 'd')

    return formatted

def networkBitsToOctetValue(networkBits:int) -> int:
    if networkBits < 0 or networkBits > 8:
        return -1

    return pow(2, 8) - pow(2, 8 - networkBits)

def networkBitsInOctetValue(octetValue:int) -> int:
    if octetValue not in [255, 254, 252, 248, 240, 224, 192, 128, 0]:
        return -1

    return int(8 - math.log(256 - octetValue) / math.log(2))