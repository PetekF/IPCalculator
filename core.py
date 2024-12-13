def isValidIPSegment(segment, binaryMode = False):
    base = 10
    if binaryMode:
        base = 2

    try:
        segmentNum = int(segment, base)
    except ValueError:
        return False

    return segmentNum >= 0 and segmentNum <= 255

def isValidIPAddress(ip, binaryMode = False):
    segments = ip.split('.')

    if len(segments) != 4:
        return False

    for seg in segments:
        if not isValidIPSegment(seg, binaryMode):
            return False

    return True

def convertSegmentToBinarySegment(segment):
    if not isValidIPSegment(segment):
        return ''

    num = int(segment, 10)
    formatted = format(num, 'b')

    return formatted

def convertBinarySegmentToSegment(binarySegment):
    if not isValidIPSegment(binarySegment, True):
        return ''

    num = int(binarySegment, 2)
    formatted = format(num, 'd')

    return formatted