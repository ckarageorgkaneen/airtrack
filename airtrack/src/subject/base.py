"""Airtrack subject base module.

This module provides an interface (AirtrackSubject) for querying subject
(e.g. mouse) information of the Airtrack system.

Example:

    subject = AirtrackSubject()
    if subject.is_inside_lane():
        print('Gotcha!')
    subject.clean_up()
"""
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
    """Airtrack subject information interface."""

    def __init__(self):
        self._camera = AirtrackCamera()

    @handle_camera_error
    def is_inside_lane(self):
        """Query subject for being inside or outside the airtable lane.

        :return: ``True`` if the subject is inside the lane,
            otherwise ``False``
        :rtype: ``bool``
        """
        return not self._camera.detect_object(
            AirtrackCameraObject.MOUSE_SIG_1.name)

    def clean_up(self):
        """Clean up the object."""
        self._camera.close()
