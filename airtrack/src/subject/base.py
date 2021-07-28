"""Interface for the Airtrack subject (mouse)"""
import logging

from airtrack.src.camera.base import AirtrackCamera
from airtrack.src.camera.base import AirtrackCameraError
from airtrack.src.definitions.camera import AirtrackCameraObject

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AirtrackSubjectError(Exception):
    """AirtrackCamera error"""


def err(message):
    logger.debug(message)
    raise AirtrackSubjectError(message)


class AirtrackSubject:
    def __init__(self):
        self._camera = AirtrackCamera()

    def is_inside_lane(self):
        try:
            is_inside_lane = not self._camera.detect_object(
                AirtrackCameraObject.MOUSE_SIG_1.name)
        except AirtrackCameraError as e:
            err(str(e))
        return is_inside_lane

    def clean_up(self):
        self._camera.close()
