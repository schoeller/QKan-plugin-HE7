# -*- coding: utf-8 -*-
import logging
import os
import tempfile
from datetime import datetime as dt
from qgis.utils import unloadPlugin

# Aufsetzen des Logging-Systems
logger = logging.getLogger('QKan')

if not logger.handlers:
    formatter = logging.Formatter('%(asctime)s %(name)s-%(levelname)s: %(message)s')

    # Consolen-Handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File-Handler
    dnam = dt.today().strftime("%Y%m%d")
    fnam = os.path.join(tempfile.gettempdir(), 'QKan{}.log'.format(dnam))
    fh = logging.FileHandler(fnam)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Warnlevel des Logging-Systems setzten
    logger.setLevel(logging.DEBUG)

    # Warnlever der Logging-Protokolle setzen
    ch.setLevel(logging.ERROR)
    fh.setLevel(logging.DEBUG)

    logger.info('Initialisierung logger erfolgreich!')
else:
    logger.info('Logger ist schon initialisiert')


def classFactory(iface):  # pylint: disable=invalid-name
    try:
        from qkan import Dummy as MainDummy
        if not MainDummy.instance:  # QKan isn't loaded
            raise Exception('The QKan main plugin has to be loaded before loading this extension.')

        dummy = Dummy(iface, MainDummy.instance)
        return dummy
    except ImportError:
        import traceback
        traceback.print_exc()
        unloadPlugin(__name__)
        raise Exception('The QKan main plugin has to be installed for this extension to work.')


class Dummy:
    instance = None
    name = __name__

    def __init__(self, iface, main):
        self.main = main
        self.actions = []

        from importhe import application as importhe
        from exporthe import application as exporthe
        from ganglinienhe import application as ganglinienhe
        self.plugins = [
            importhe.ImportFromHE(iface),
            exporthe.ExportToHE(iface),
            ganglinienhe.Application(iface)
        ]
        Dummy.instance = self

        # Register self
        self.main.register(self)

    def initGui(self):
        # Calls initGui on all known QKan plugins
        for plugin in self.plugins:
            plugin.initGui()

        self.main.sort_actions()

    def unload(self):
        # Call unload on all loaded plugins
        for plugin in self.plugins:
            plugin.unload()

        # Unload in main instance
        # Remove entries from menu
        for action in self.actions:
            self.main.menu.removeAction(action)
            self.main.toolbar.removeAction(action)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True,
                   status_tip=None, whats_this=None, parent=None):
        action = self.main.add_action(icon_path, text, callback, enabled_flag, add_to_menu, add_to_toolbar, status_tip,
                                      whats_this, parent)
        self.actions.append(action)
        return action
