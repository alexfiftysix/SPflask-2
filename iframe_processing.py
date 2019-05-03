# TODO: Some unit testing for these guys


def valid_bandcamp(iframe):
    """
    returns true if bandcamp link is acceptable
    :param iframe:
    :return:
    """
    splitty = iframe.split(' ')

    if len(splitty) < 10:
        return False
    elif splitty[0] != '<iframe':
        return False
    elif splitty[3] != 'width:':
        return False
    elif splitty[5] != 'height:':
        return False
    elif splitty[7].find('src="https://bandcamp.com/EmbeddedPlayer/') != 0:
        return False
    elif splitty[8] != 'seamless><a':
        return False
    elif splitty[9].find('href="http://streetpieces.bandcamp.com/') != 0:
        return False

    # We made it
    return True


def valid_youtube(iframe):
    """
    Returns True if iframe is a valid youtube embed
    :param iframe:
    :return:
    """
    # TODO: Work out how to validate that it's a Street Pieces video?

    splitty = iframe.split(' ')

    if splitty[0] != '<iframe':
        return False
    elif splitty[3].find('src="https://www.youtube') != 0:
        return False

    return True
