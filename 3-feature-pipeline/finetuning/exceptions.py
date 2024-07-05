class DatasetError(Exception):
    pass


class FileNotFoundError(DatasetError):
    pass


class JSONDecodeError(DatasetError):
    pass


class APICommunicationError(DatasetError):
    pass
