"""Interface for the Airtrack subject (mouse)"""
import logging

from airtrack.src.camera.base import AirtrackCamera
from airtrack.src.definitions.camera import AirtrackCameraObject
from airtrack.src.errors import on_error_raise
from airtrack.src.errors import AirtrackCameraError
from airtrack.src.errors import AirtrackSubjectError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handle_camera_error = on_error_raise(
    AirtrackSubjectError,
    logger,
    catch_error=AirtrackCameraError)


class AirtrackSubject:
    def __init__(self):
        self._camera = AirtrackCamera()

    @handle_camera_error
    def is_inside_lane(self):
        return not self._camera.detect_object(
            AirtrackCameraObject.MOUSE_SIG_1.name)

    def clean_up(self):
        self._camera.close()
