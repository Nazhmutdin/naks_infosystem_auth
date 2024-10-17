from dishka import make_async_container

from app.main.dependencies.application import ApplicationProvider
from app.main.dependencies.core import CoreProvider


class MainProvider(ApplicationProvider, CoreProvider): ...


provider = MainProvider()
container = make_async_container(provider)
