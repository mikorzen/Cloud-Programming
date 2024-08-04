import msgspec
from litestar.datastructures import UploadFile


class FileUpload(msgspec.Struct):
    name: str
    file: UploadFile
