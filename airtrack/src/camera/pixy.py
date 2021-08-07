"""Airtrack Pixy2 camera module.

This module provides a wrapper interface (PixyCam) for interacting with a
Pixy2 camera (https://pixycam.com/pixy2/) underlying the camera of the
Airtrack system.

Example:

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
import sys
import logging
import functools
import signal

from airtrack.src.errors import err
from airtrack.src.errors import PixyCamError

logger = logging.getLogger(__name__)


class PixyCam:
    MAX_BLOCKS = 100
    PROGRAM_CCC = 'color_connected_components'
    CONNECT_ERROR_MSG = 'Could not connect to PixyCam.'

    def __init__(self):
        self.__pixy = None
        self.__blocks = None
        self._initiated = False
        # Register segmentation fault handler
        signal.signal(signal.SIGSEGV, functools.partial(
            err, PixyCamError, logger, message=self.CONNECT_ERROR_MSG))

    @property
    def _pixy(self):
        if self.__pixy is None:
            from airtrack.submodules.pixy2.build.python_demos import pixy
            self.__pixy = pixy
            if pixy.init() == -1:
                sys.modules.pop('pixy')
                err(PixyCamError, logger, message=self.CONNECT_ERROR_MSG)
            self.__pixy.change_prog(self.PROGRAM_CCC)
            self._toggle_lamp()
            self._initiated = True
        return self.__pixy

    @property
    def _blocks(self):
        if self.__blocks is None:
            self.__blocks = self._pixy.BlockArray(self.MAX_BLOCKS)
        return self.__blocks

    def _toggle_lamp(self, on=True):
        self._pixy.set_lamp(int(on), 0)

    def _get_blocks(self):
        return self._pixy.ccc_get_blocks(100, self._blocks)

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
