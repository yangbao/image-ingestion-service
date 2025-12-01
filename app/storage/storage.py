# app/storage/storage.py

from abc import ABC, abstractmethod
from fastapi import UploadFile


class Uploader(ABC):
    """
    Abstract Base Class (ABC) for all storage uploaders (Local, S3, OSS, etc.).
    This defines the standardized interface required by the application's main logic.
    """

    @abstractmethod
    def save(self, file: UploadFile, destination: str) -> str:
        """
        Saves the uploaded file to the specific storage destination.

        Args:
            file: The file object to save.
            destination: The target prefix/directory.

        Returns:
            The unique, standardized path/key to the stored file.
        """
        pass