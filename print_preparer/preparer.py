from .upscaler import Upscaler
from .image import Image
from pathlib import Path
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
            image: Image = Image(file_path)
            image = self.__upscaler.upscale(image)
            if self.__must_be_rotated(image):
                image.rotate(90)
            output_file_path: Path = image.save(Path(file_path.parent, 'output', f'{file_path.stem}.jpg'))
            self.__output_file_paths.append(output_file_path)
            queue.put(output_file_path)
        queue.put(None)
        return self.__output_file_paths

    @staticmethod
    def __must_be_rotated(image: Image) -> bool:
        height, width = image.get_size()
        if height < width:
            return True
        return False

    @staticmethod
    def __must_be_resized(image: Image) -> bool:
        height, width = image.get_size()
        if round(height / width, 3) != 2 ** 0.5:
            return True
        return False
