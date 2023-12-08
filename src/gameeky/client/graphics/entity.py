from typing import Dict, List, Tuple

from gi.repository import Gdk, GdkPixbuf

from ...common.definitions import Direction, State
from ...common.entity import Entity as CommonEntity
from ...common.scanner import Description
from ...common.utils import get_time_milliseconds, division
from ...common.utils import get_data_path, clamp


class Animation:
    def __init__(
        self,
        duration: float,
        scale_x: float,
        scale_y: float,
        frames: List[Gdk.Texture],
    ) -> None:
        self._frames = frames
        self._duration = duration * 1000
        self._scale_x = scale_x
        self._scale_y = scale_y

        self._frame_duration = division(self._duration, len(self._frames))
        self._timestamp_start = get_time_milliseconds()

    def get_frame(self) -> Tuple[float, float, Gdk.Texture]:
        if not self._frames:
            return -1, -1, None

        if not self._frame_duration:
            return self._scale_x, self._scale_y, self._frames[0]

        timestamp = get_time_milliseconds()
        elapsed_since_start = timestamp - self._timestamp_start

        if elapsed_since_start > self._duration:
            self._timestamp_start = timestamp
            index = 0

        index = int(elapsed_since_start / self._frame_duration) % len(self._frames)

        return self._scale_x, self._scale_y, self._frames[index]


class Entity:
    def __init__(
        self,
        type_id: int,
        default: Animation,
    ) -> None:
        self.type_id = type_id
        self._default = default
        self._animations: Dict[State, Dict[Direction, Animation]] = {}

    def get_texture(self, entity: CommonEntity) -> Tuple[float, float, Gdk.Texture]:
        if entity.state not in self._animations:
            return self.get_default_texture()
        if entity.direction not in self._animations[entity.state]:
            return self.get_default_texture()

        return self._animations[entity.state][entity.direction].get_frame()

    def get_default_texture(self) -> Gdk.Texture:
        return self._default.get_frame()

    def add_animation(
        self,
        state: State,
        direction: Direction,
        animation: Animation,
    ) -> None:
        if state not in self._animations:
            self._animations[state] = {}

        self._animations[state][direction] = animation


class EntityRegistry:
    __entities__: Dict[int, Entity] = {}

    @classmethod
    def reset(cls) -> None:
        cls.__entities__ = {}

    @classmethod
    def get_texture(cls, entity: CommonEntity) -> Tuple[float, float, Gdk.Texture]:
        return cls.__entities__[entity.type_id].get_texture(entity)

    @classmethod
    def get_default_texture(cls, type_id: int) -> Gdk.Texture:
        return cls.__entities__[type_id].get_default_texture()

    @classmethod
    def register(cls, description: Description) -> None:
        default = cls.create_animation_from_description(description.graphics.default)

        entity = Entity(type_id=description.id, default=default)

        for state in description.graphics.states:
            for direction in state.directions:
                animation = cls.create_animation_from_description(direction.animation)
                entity.add_animation(
                    State[state.name.upper()],
                    Direction[direction.name.upper()],
                    animation,
                )

        cls.__entities__[entity.type_id] = entity

    @classmethod
    def create_animation_from_description(
        cls,
        description: Description,
    ) -> Animation:
        frames = []

        pixbufs = cls.load_pixbufs_from_image(
            columns=description.columns,
            rows=description.rows,
            tiles_x=description.tiles_x,
            tiles_y=description.tiles_y,
            path=get_data_path(description.path),
        )

        for pixbuf in pixbufs[description.first_frame : description.last_frame + 1]:
            pixbuf = cls.transform_pixbuf(
                pixbuf=pixbuf,
                crop_x=description.crop_x,
                crop_y=description.crop_y,
                flip_x=description.flip_x,
                flip_y=description.flip_y,
                rotate=description.rotate,
            )

            frames.append(Gdk.Texture.new_for_pixbuf(pixbuf))

        return Animation(
            duration=description.duration,
            scale_x=description.scale_x,
            scale_y=description.scale_y,
            frames=frames,
        )

    @classmethod
    def transform_pixbuf(
        cls,
        pixbuf: GdkPixbuf.Pixbuf,
        crop_x: int = 0,
        crop_y: int = 0,
        flip_x: bool = False,
        flip_y: bool = False,
        rotate: float = 0.0,
    ) -> GdkPixbuf.Pixbuf:
        if flip_x is True:
            pixbuf = pixbuf.flip(horizontal=True)
        if flip_y is True:
            pixbuf = pixbuf.flip(horizontal=False)
        if crop_x > 0:
            pixbuf = pixbuf.new_subpixbuf(
                crop_x,
                0,
                pixbuf.get_width() - crop_x,
                pixbuf.get_height(),
            )
        if crop_y > 0:
            pixbuf = pixbuf.new_subpixbuf(
                0,
                crop_y,
                pixbuf.get_width(),
                pixbuf.get_height() - crop_y,
            )
        if rotate > 0.0:
            pixbuf = pixbuf.rotate_simple(rotate)

        return pixbuf

    @classmethod
    def load_pixbufs_from_image(
        cls,
        columns: int,
        rows: int,
        tiles_x: int,
        tiles_y: int,
        path: str,
    ) -> List[GdkPixbuf.Pixbuf]:
        pixbufs = []

        src_pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)

        tileset_width = src_pixbuf.get_width()
        tileset_height = src_pixbuf.get_height()

        width = int(tileset_width / columns)
        height = int(tileset_height / rows)

        for row in range(rows):
            for column in range(columns):
                rect_x = column * width
                rect_y = row * height

                available_width = tileset_width - rect_x
                available_height = tileset_height - rect_y

                rect_width = clamp(available_width, width, width * tiles_x)
                rect_height = clamp(available_height, height, height * tiles_y)

                pixbuf = src_pixbuf.new_subpixbuf(
                    rect_x,
                    rect_y,
                    rect_width,
                    rect_height,
                )
                pixbufs.append(pixbuf)

        return pixbufs