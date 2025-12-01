from typing import Protocol
from fastapi import UploadFile

class StorageUploader(Protocol):
    """
    Storage Upload Abstract Interface (Protocol).
    All specific storage implementations (Local, OSS, COS) must follow this interface.
    """
    def save(self, file: UploadFile, destination: str) -> str:
        """
        保Save the file and return the storage path/key/URL.
        :param file: The uploaded file stream.
        :param destination: Storage destination path (such as local folder name or directory prefix within an OSS bucket).
        :return: The final storage path/key for the file.
        """
        ...