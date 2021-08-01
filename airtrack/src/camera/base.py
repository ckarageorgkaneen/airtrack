"""Interface for the Airtrack Camera"""
import logging

from airtrack.src.camera.pixy import PixyCam
from airtrack.src.definitions.camera import AirtrackCameraObject
from airtrack.src.errors import on_error_raise
from airtrack.src.errors import PixyCamError
from airtrack.src.errors import AirtrackCameraError

logger = logging.getLogger(__name__)

handle_bad_object = on_error_raise(
    AirtrackCameraError,
    logger,
    message=f'Invalid object. Must be one of: {AirtrackCameraObject}',
    catch_error=KeyError)
handle_pixy_error = on_error_raise(
    AirtrackCameraError,
    logger,
    catch_error=PixyCamError)


class AirtrackCamera:
    def __init__(self):
        self._pixy_cam = PixyCam()

    @handle_bad_object
    def _object(self, name):
        return AirtrackCameraObject[name]

    @handle_pixy_error
    def _find_signature(self, signature):
        return self._pixy_cam.find_targets(
            [signature])

    def detect_object(self, name):
        signature = self._object(name).value
        object_detected = self._find_signature(signature)
        return object_detected

    def detect_objects(self, *names, detect_any_object=False):
        objects_detected = [self.detect_object(name) for name in names]
        if detect_any_object:
            return any(objects_detected)
        return all(objects_detected)

    def close(self):
        self._pixy_cam.close()
