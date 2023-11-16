import os

__dir__ = os.path.dirname(os.path.abspath(__file__))

from typing import Optional

from gi.repository import Gio, Gtk, Adw, GObject

from ...common.logger import logger
from ...common.utils import get_data_path
from ...common.scanner import Description


@Gtk.Template(filename=os.path.join(__dir__, "scene_open_window.ui"))
class SceneOpenWindow(Adw.Window):
    __gtype_name__ = "SceneOpenWindow"

    __gsignals__ = {
        "done": (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    path = Gtk.Template.Child()
    scene = Gtk.Template.Child()

    def __init__(self, *args, **kargs) -> None:
        super().__init__(*args, **kargs)
        self._description: Optional[Description] = None
        self.path.props.text = get_data_path("")

    @Gtk.Template.Callback("on_cancel_clicked")
    def __on_cancel_clicked(self, button: Gtk.Button) -> None:
        self.destroy()

    @Gtk.Template.Callback("on_open_clicked")
    def __on_open_clicked(self, button: Gtk.Button) -> None:
        self.emit("done")
        self.close()

    @Gtk.Template.Callback("on_path_open_clicked")
    def __on_path_open_clicked(self, button: Gtk.Button) -> None:
        dialog = Gtk.FileDialog()
        dialog.open(callback=self.__on_path_open_finish)

    def __on_path_open_finish(
        self,
        dialog: Gtk.FileDialog,
        result: Gio.AsyncResult,
    ) -> None:
        try:
            file = dialog.open_finish(result)
        except Exception as e:
            logger.error(e)
        else:
            self.path.props.text = file.get_path()

    @Gtk.Template.Callback("on_scene_open_clicked")
    def __on_scene_open_clicked(self, button: Gtk.Button) -> None:
        dialog = Gtk.FileDialog()
        dialog.open(callback=self.__on_scene_open_finish)

    def __on_scene_open_finish(
        self,
        dialog: Gtk.FileDialog,
        result: Gio.AsyncResult,
    ) -> None:
        try:
            file = dialog.open_finish(result)
        except Exception as e:
            logger.error(e)
        else:
            path = file.get_path()
            self.scene.props.text = path
            self._description = Description.new_from_json(path)

    @property
    def data_path(self) -> None:
        return self.path.props.text

    @property
    def description(self) -> Optional[Description]:
        return self._description