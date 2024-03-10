from .settings import Settings
from .preparer import Preparer
from .printer import Printer
from .progress_bar import ProgressBar
import easygui
from pathlib import Path
from multiprocessing import SimpleQueue, Process
from time import sleep


class App:
    def __init__(self):
        self.__settings: Settings = Settings()
        self.printer: Printer = Printer()
        print_after_prepare: bool = self.__question_print_after_prepare()
        if print_after_prepare:
            self.printer.set_printer(self.__choice_printer(self.printer.get_printers()))
        file_paths_for_preparation = self.__get_files(self.__settings.default_files_path)
        if not len(file_paths_for_preparation):
            return
        elif file_paths_for_preparation[0].parent != self.__settings.default_files_path:
            self.__settings.default_files_path = file_paths_for_preparation[0].parent
            self.__settings.save()
        preparer: Preparer = Preparer(file_paths_for_preparation, self.__settings.dpi)
        prepared_files: SimpleQueue = SimpleQueue()
        if print_after_prepare:
            print('Preparing and printing images...')
        else:
            print('Preparing images...')
        progress_bar: ProgressBar = ProgressBar(len(file_paths_for_preparation))
        progress_bar.show()
        process: Process = Process(target=preparer.prepare, args=(prepared_files, ))
        process.start()
        while True:
            sleep(1)
            if prepared_files.empty():
                continue
            prepared_file_path: Path = prepared_files.get()
            if prepared_file_path is None:
                return
            if print_after_prepare:
                while self.printer.has_active_jobs():
                    sleep(1)
                self.printer.print(prepared_file_path)
            progress_bar.inc()
            progress_bar.show()

    @staticmethod
    def __question_print_after_prepare() -> bool:
        answer: bool = easygui.ynbox('Print images after preparation?', 'Question')
        if answer is None:
            exit()
        return answer

    @staticmethod
    def __choice_printer(printers: list) -> str:
        if len(printers) == 0:
            easygui.msgbox('You do not have any printers installed on your system. The program will be terminated.')
            exit()
        elif len(printers) == 1:
            answer: bool = easygui.ynbox(f'You have only one printer installed: "{printers[0]}". '
                                         f'Continue using it?', 'Question')
            if not answer:
                exit()
            return printers[0]
        return easygui.choicebox('Choose your printer:', 'Question', printers)

    @staticmethod
    def __get_files(default_path: Path) -> tuple[Path]:
        files = easygui.fileopenbox('Choice your files...',
                                    default=f'{str(default_path)}/',
                                    filetypes=['*.jpg', '*.jpeg',
                                               '*.png', '*.webp'],
                                    multiple=True)
        return tuple(map(lambda x: Path(x), files)) if files is not None else ()

    @staticmethod
    def get_merge_mode() -> bool:
        msg = 'Choice mode:'
        choices = ['Upscale', 'Upscale + Merge']
        if easygui.buttonbox(msg, choices=choices) == 'Upscale':
            return False
        return True
