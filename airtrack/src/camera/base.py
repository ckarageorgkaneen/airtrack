"""Airtrack camera base module.

This module provides an interface (AirtrackCamera) for interacting with the
camera of the Airtrack system.

Example:

    from airtrack.src.definitions.camera import AirtrackCameraObject

    ac = AirtrackCamera()

    # Query the camera N times
    N = 500
    for i in range(N):
        if ac.find_subject():
            print('Mouse detected!')
            break

    ac.close()
"""
import logging

from airtrack.src.camera.pixy import PixyCam
from airtrack.src.definitions.camera import AirtrackCameraObject
from airtrack.src.errors import on_error_raise
from airtrack.src.errors import PixyCamError
from airtrack.src.errors import AirtrackCameraError

logger = logging.getLogger(__name__)


handle_pixy_error = on_error_raise(
    AirtrackCameraError,
    logger,
    catch_error=PixyCamError)


class AirtrackCamera:
    """Airtrack camera interface."""

    def __init__(self):
        self._pixy_cam = PixyCam()

    @handle_pixy_error
    def _find_signature(self, signature):
        return self._pixy_cam.find_targets(
            [signature])

    def _find_object(self, object_enum):
        signature = object_enum.value
        signature_found = self._find_signature(signature)
        return signature_found

    def find_subject(self):
        """Find subject (e.g. mouse).

        :return: ``True`` if the subject was found, otherwise ``False``
        :rtype: ``bool``
        """
        object_found = self._find_object(AirtrackCameraObject.SUBJECT)
        return object_found

    def close(self):
        """Close the camera."""
        self._pixy_cam.close()
