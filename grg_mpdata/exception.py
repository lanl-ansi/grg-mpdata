'''a collection of all grg_mpdata exception classes'''


class MPDataException(Exception):
    '''root class for all MPData Exceptions'''
    pass


class MPDataParsingError(MPDataException):
    '''for errors that occur while attempting to parse a matpower data file'''
    pass


class MPDataValidationError(MPDataException):
    '''for errors that occur while attempting to validate the correctness of
        a parsed matpower data file
    '''
    pass


class MPDataWarning(Warning):
    '''root class for all MPData Warnings'''
    pass
