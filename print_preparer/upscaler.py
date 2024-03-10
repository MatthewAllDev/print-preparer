from cv2 import dnn_superres
from numpy import ndarray


class Upscaler:
    def __init__(self, dpi: int = 300):
        self.__dpi: int = dpi
        self.__sr: dnn_superres.DnnSuperResImpl = dnn_superres.DnnSuperResImpl_create()
        self.__sr.readModel(self.__get_model_path(4))
        self.__sr.setModel('fsrcnn', 4)

    def upscale(self, image: ndarray, scale: int = None) -> ndarray:
        target_scale: int
        if scale is None:
            scale = self.get_recommended_scale(image, self.__dpi)
        if scale < 2:
            return image
        elif scale > 4:
            target_scale = 4
        else:
            target_scale = scale
        scale = scale - target_scale
        if target_scale != self.__sr.getScale():
            self.__sr.readModel(self.__get_model_path(target_scale))
            self.__sr.setModel('fsrcnn', target_scale)
        image: ndarray = self.__sr.upsample(image)
        return self.upscale(image, scale)

    @staticmethod
    def get_recommended_scale(image: ndarray, dpi: int = 300) -> int:
        height, width, _ = image.shape
        return round(11.69 * dpi / height + 0.49)

    @staticmethod
    def __get_model_path(scale: int):
        return f'print_preparer/models/FSRCNN_x{scale}.pb'
