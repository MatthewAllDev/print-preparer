import cups
from pathlib import Path


class Printer:
    __printer: str = None

    def __init__(self):
        self.__connection: cups.Connection = cups.Connection()
        self.__active_jobs: list = []

    def print(self, file_path: Path) -> int:
        job_id: int = self.__connection.printFile(self.__printer, str(file_path), 'auto_printing', options={})
        self.__active_jobs.append(job_id)
        return job_id

    def has_active_jobs(self) -> bool:
        for job in self.__active_jobs:
            if self.__connection.getJobs().get(job, None) is None:
                self.__active_jobs.remove(job)
        return bool(len(self.__active_jobs))

    def get_printers(self) -> list[str]:
        return list(self.__connection.getPrinters().keys())

    def set_printer(self, name: str):
        self.__printer = name
