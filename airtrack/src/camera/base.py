"""Interface for the Airtrack Camera"""
import logging

from airtrack.src.camera.pixy import PixyCam
from airtrack.src.camera.pixy import PixyCamError
from airtrack.src.definitions.camera import AirtrackCameraObject

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AirtrackCameraError(Exception):
    """AirtrackCamera error"""


def err(message):
    logger.debug(message)
    raise AirtrackCameraError(message)


class AirtrackCamera:
    def __init__(self):
        self._pixy_cam = PixyCam()

    def detect_object(self, name):
        try:
            airtrack_obj = AirtrackCameraObject[name]
        except KeyError:
            err(f'No such object: {name} in {AirtrackCameraObject}')
        try:
            obj_detected = self._pixy_cam.find_targets(
                [airtrack_obj.value])
        except PixyCamError as e:
            err(str(e))
        return obj_detected

    def detect_objects(self, *names, detect_any_object=False):
        objects_detected = [self.detect_object(name) for name in names]
        if detect_any_object:
            return any(objects_detected)
        return all(objects_detected)

    def close(self):
        self._pixy_cam.close()