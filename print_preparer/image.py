from pathlib import Path
from numpy import ndarray, argwhere, concatenate, array, max as np_max, min as np_min, full
from cv2 import imread, imwrite, rotate, resize, IMREAD_UNCHANGED
from typing import TypeVar, Optional, Self, Tuple


Color = TypeVar('Color', Tuple[int, int, int], Tuple[int, int, int, int])
FilterByColor = TypeVar('FilterByColor',
                        Tuple[Optional[int], Optional[int], Optional[int]],
                        Tuple[Optional[int], Optional[int], Optional[int], Optional[int]])


class Image:
    __data: ndarray

    def __init__(self, path: Path):
        self.__data = imread(str(path), IMREAD_UNCHANGED)

    def get_data(self) -> ndarray:
        return self.__data

    def set_data(self, data: ndarray):
        self.__data = data

    def save(self, path: Path) -> Path:
        if not path.parent.exists():
            path.parent.mkdir()
        imwrite(str(path), self.__data)
        return path

    def get_size(self) -> Tuple[int, int]:
        height, width, _ = self.__data.shape
        return height, width

    def get_not_empty_range(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        height, width = self.get_size()
        if self.__data.shape[2] > 3:
            mask: ndarray = array([[[False, False, False, True]] * width] * height)
            filter_condition: ndarray = (self.__data != 0) & mask
        else:
            filter_condition: ndarray = self.__data < 255
        res_matrix: ndarray[ndarray[int]] = argwhere(filter_condition)
        return ((np_min(res_matrix[:, 0]), np_max(res_matrix[:, 0])),
                (np_min(res_matrix[:, 1]), np_max(res_matrix[:, 1])))

    def rotate(self, angle: int) -> Self:
        if angle % 360 == 0:
            return self
        if angle % 90 > 0:
            raise RuntimeError('Angle must be a multiple of 90')
        while angle < 0:
            angle += 360
        while angle > 360:
            angle -= 360
        self.__data = rotate(self.__data, angle // 90 - 1)
        return self

    def crop(self, y: Tuple[int, int], x: Tuple[int, int]) -> Self:
        self.__data = self.__data[y[0]:y[1], x[0]: x[1]]
        return self

    def resize_canvas(self, height: int, width: int, color: Color = (255, 255, 255, 0)) -> Self:
        h, w, c = self.__data.shape
        to_fill = color
        if len(color) < c:
            to_fill = (*color, 0)
        height_diff: int = height - h
        width_diff: int = width - w
        if width_diff < 0 or height_diff < 0:
            self.resize(height, width, True)
        if height_diff > 0:
            top_diff: int = round(height_diff / 2 + 0.49)
            bottom_dif: int = height_diff - top_diff
            self.__data = concatenate((
                array([[to_fill] * w] * top_diff),
                self.__data,
                array([[to_fill] * w] * bottom_dif)
            ), axis=0)
            h, w, c = self.__data.shape
        if width_diff > 0:
            left_diff: int = round(width_diff / 2 + 0.49)
            right_diff: int = width_diff - left_diff
            self.__data = concatenate((
                array([[to_fill] * left_diff] * h),
                self.__data,
                array([[to_fill] * right_diff] * h)
            ), axis=1)
        return self

    def resize(self, height: int = None, width: int = None, save_ratio: bool = False) -> Self:
        h, w = self.get_size()
        current_ratio: float = h / w
        if height is None and width is None:
            raise RuntimeError('At least one parameter must be defined: height or width')
        if height is None:
            height: int = round(current_ratio * width) if save_ratio else h
        elif width is None:
            width: int = round(height / current_ratio) if save_ratio else w
        elif save_ratio:
            t_height: int = round(current_ratio * width)
            t_width: int = round(height / current_ratio)
            if t_height * width < t_width * height:
                height = t_height
                width = width
            else:
                height = height
                width = t_width
        self.__data = resize(self.__data, (width, height))
        return self

    def change_transparency_color(self, color: Color = (255, 255, 255, 0)) -> Self:
        if self.__data.shape[2] < 4:
            return self
        if len(color) < 4:
            color = (*color, 0)
        return self.change_color((None, None, None, 0), color)

    def change_color(self, current_color: FilterByColor, replacement_color: Color) -> Self:
        channels: int = self.__data.shape[-1]
        if channels == 4:
            if channels - len(current_color) == 1:
                current_color = (*current_color, None)
            if channels - len(replacement_color) == 1:
                replacement_color = (*replacement_color, 255)
        if max(len(current_color), len(replacement_color)) > channels:
            raise ValueError("Filter dimensionality must match the last dimension of the array.")
        condition = full(self.__data.shape[:-1], True)
        for i in range(len(current_color)):
            if current_color[i] is not None:
                condition &= (self.__data[:, :, i] == current_color[i])
        self.__data[condition] = replacement_color
        return self

    def auto_crop(self) -> Self:
        not_empty_range = self.get_not_empty_range()
        return self.crop(*not_empty_range)
