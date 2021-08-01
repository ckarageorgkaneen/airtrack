"""
Interface for the Pixy2 PixyCam

For more, see: https://pixycam.com/pixy2/
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
        nblocks = self._get_blocks()
        signatures = set()
        for i in range(0, nblocks):
            sign = self._blocks[i].m_signature
            logger.debug(f'Got block with signature: {sign}')
            signatures.add(sign)
        return list(signatures)

    def find_targets(self, signatures=None):
        if signatures is None:
            return False
        found_targets = list(set(signatures).intersection(
            self.get_signatures()))
        if found_targets:
            logger.debug(f'Found targets: {found_targets}')
        return signatures == found_targets

    def close(self):
        if self._initiated:
            self._toggle_lamp(on=False)
