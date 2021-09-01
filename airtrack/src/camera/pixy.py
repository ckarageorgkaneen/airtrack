"""Airtrack Pixy2 camera module.

This module provides a wrapper interface (PixyCam) for interacting with a
Pixy2 camera (https://pixycam.com/pixy2/) underlying the camera of the
Airtrack system.

Example:

    from airtrack.src.camera.pixy import PixyCam

    pc = PixyCam()

    # Get detected signatures
    signatures = pc.get_signatures()
    print(signatures)

    # Find target signatures
    target_signatures = [1, 2]
    found_targets = pc.find_targets(target_signatures)

    if found_targets:
        print(f'Found signatures: {target_signatures}')
    else:
        print(f'Did not find signatures: {target_signatures}')

    pc.close()
"""
import functools
import signal

from airtrack.src import utils

from airtrack.src.errors import err
from airtrack.src.errors import PixyCamError

from airtrack.submodules.pixy2.build.python_demos import pixy

logger = utils.create_logger(__name__)


class PixyCam:
    MAX_BLOCKS = 100
    PROGRAM_CCC = 'color_connected_components'
    CONNECT_ERROR_MSG = 'Could not connect to PixyCam.'

    def __init__(self):
        if pixy.init() == -1:
            err(PixyCamError, logger, message=self.CONNECT_ERROR_MSG)
        pixy.change_prog(self.PROGRAM_CCC)
        self._toggle_lamp()
        self._initiated = True
        self._blocks = pixy.BlockArray(self.MAX_BLOCKS)
        # Register segmentation fault handler
        signal.signal(signal.SIGSEGV, functools.partial(
            err, PixyCamError, logger, message=self.CONNECT_ERROR_MSG))

    def _toggle_lamp(self, on=True):
        pixy.set_lamp(int(on), 0)

    def _get_blocks(self):
        return pixy.ccc_get_blocks(100, self._blocks)

    def get_signatures(self):
        """Return a list of detected signatures.

        :rtype: ``list`` of ``int``
        """
        nblocks = self._get_blocks()
        signatures = set()
        for i in range(0, nblocks):
            sign = self._blocks[i].m_signature
            logger.debug(f'Got block with signature: {sign}')
            signatures.add(sign)
        return list(signatures)

    def find_targets(self, signatures=None):
        """Find signatures.

        :keyword  signatures:  A list of Pixy2 cam signatures.
        :type     signatures:  ``list`` of ``int``

        :return: ``True`` if the given signatures were found,
            otherwise ``False``
        :rtype: ``bool``
        """
        if signatures is None:
            return False
        found_targets = list(set(signatures).intersection(
            self.get_signatures()))
        if found_targets:
            logger.debug(f'Found targets: {found_targets}')
        return signatures == found_targets

    def close(self):
        """Close Pixy2 cam."""
        if self._initiated:
            self._toggle_lamp(on=False)
