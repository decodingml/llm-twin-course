import structlog


def get_logger(cls: str):
    return structlog.get_logger().bind(cls=cls)