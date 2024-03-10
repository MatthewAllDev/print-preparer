from .upscaler import Upscaler
from pathlib import Path
from cv2 import imread, imwrite, rotate, ROTATE_90_CLOCKWISE
from typing import Sequence
from numpy import ndarray
from multiprocessing import SimpleQueue


class Preparer:
    def __init__(self, file_paths: Sequence[Path], dpi: int = 300):
        self.__original_file_paths: Sequence[Path] = file_paths
        self.__output_file_paths: list[Path] = []
        self.__upscaler: Upscaler = Upscaler(dpi)

    def prepare(self, queue: SimpleQueue) -> list[Path]:
        for file_path in self.__original_file_paths:
            image: ndarray = imread(str(file_path))
            image = self.__upscaler.upscale(image)
            if self.__must_be_rotated(image):
                image = rotate(image, ROTATE_90_CLOCKWISE)
            output_file_path: Path = self.__save_image(image, Path(file_path.parent, 'output', f'{file_path.stem}.jpg'))
            self.__output_file_paths.append(output_file_path)
            queue.put(output_file_path)
        queue.put(None)
        return self.__output_file_paths

    @staticmethod
    def __save_image(image, path: Path) -> Path:
        if not path.parent.exists():
            path.parent.mkdir()
        imwrite(str(path), image)
        return path

    @staticmethod
    def __must_be_rotated(image: ndarray) -> bool:
        height, width, _ = image.shape
        if height < width:
            return True
        return False
