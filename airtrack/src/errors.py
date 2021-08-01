class AirtrackBaseError(Exception):
    """AirtrackBase error"""


class AirtrackError(AirtrackBaseError):
    """Airtrack error"""


class AirtrackSubjectError(AirtrackError):
    """AirtrackCamera error"""


class AirtrackStateMachineError(AirtrackError):
    """AirtrackStateMachine error"""


class AirtrackCameraError(AirtrackError):
    """AirtrackCamera error"""


class AirtrackActuatorError(AirtrackError):
    """AirtrackActuator error"""


class PixyCamError(Exception):
    """PixyCam error"""


def err(error, logger, message):
    logger.debug(message)
    raise error(message)


def on_error_raise(error, logger, catch_error=None, message=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except catch_error or Exception as e:
                err(error, logger, message or str(e))
        return wrapper
    return decorator
