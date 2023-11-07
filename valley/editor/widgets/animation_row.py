import os

__dir__ = os.path.dirname(os.path.abspath(__file__))

from gi.repository import Gtk

from .animation import Animation
from .tile import Tile
from .entity import Entity


@Gtk.Template(filename=os.path.join(__dir__, "animation_row.ui"))
class AnimationRow(Gtk.Box):
    __gtype_name__ = "AnimationRow"

    settings = Gtk.Template.Child()
    graphics = Gtk.Template.Child()

    def __init__(self, *args, **kargs) -> None:
        super().__init__(*args, **kargs)

        self._animation = Animation()
        self._animation.props.hexpand = True
        self._animation.props.vexpand = True
        self._animation.connect("changed", self.__on_animation_changed)

        self.settings.props.child = self._animation

        self._entity = Entity()
        self._entity.props.hexpand = True
        self._entity.props.vexpand = True

        self._tile = Tile()
        self._tile.props.hexpand = True
        self._tile.props.vexpand = True

        self.graphics.append(self._tile)
        self.graphics.append(self._entity)

    def __on_animation_changed(self, animation: Animation) -> None:
        self._entity.update(animation.description)
        self._tile.update(animation.description)
