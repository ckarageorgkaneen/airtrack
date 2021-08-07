"""Airtrack camera base module.

This module provides an interface (AirtrackCamera) for interacting with the
camera of the Airtrack system.

Example:

    from airtrack.src.definitions.camera import AirtrackCameraObject

    ac = AirtrackCamera()

    # Query the camera N times
    N = 500
    for i in range(N):
        mout_detected = ac.detect_object(AirtrackCameraObject.MOUSE_SIG_1.name)
        if mouse_detected:
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
    """Airtrack camera interface."""

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
        """Detect an object by name.

        :keyword  name:  The value of a AirtrackCameraObject enum.
            (e.g. MOUSE_SIG_1)
        :type     name:  ``str``

        :return: ``True`` if the object was detected, otherwise ``False``
        :rtype: ``bool``
        """
        signature = self._object(name).value
        object_detected = self._find_signature(signature)
        return object_detected

    def detect_objects(self, *names, detect_any_object=False):
        """Detect objects by name.

        :keyword  names:  A list of values AirtrackCameraObject enums.
            (e.g. MOUSE_SIG_1, MOUSE_SIG_2)
        :type     names:  ``list`` of ``str``

        :keyword  detect_any_object:  Return ``True`` if any one of the
            objects are detected.
        :type     detect_any_object:  ``bool``

        :return: ``True`` if objects were detected, otherwise ``False``
        :rtype: ``bool``
        """

        objects_detected = [self.detect_object(name) for name in names]
        if detect_any_object:
            return any(objects_detected)
        return all(objects_detected)

    def close(self):
        """Close the camera."""
        self._pixy_cam.close()
