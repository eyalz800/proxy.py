from typing import Callable

class Proxy:
    @staticmethod
    def __call__[ProxyType, Proxied](proxied: type[Proxied]) -> Callable[[type[ProxyType]], type[ProxyType]]:
        def make_proxy(cls: type[ProxyType]) -> type[ProxyType]:
            def init(self, proxied: Proxied, *args, **kwargs):
                self._proxied = proxied
                cls.__init__(self, *args, **kwargs)

            def get(self, name: str):
                return getattr(self._proxied, name)

            bases = tuple(b for b in cls.__bases__ if b is not proxied)
            members = dict(cls.__dict__)
            members.update({
                '__init__': init,
                '__getattr__': get,
            })
            return type(cls.__name__, bases, members) # type: ignore
        return make_proxy

    @staticmethod
    def create[ProxyType](proxy: type[ProxyType], proxied, *args, **kwargs) -> ProxyType:
        return proxy(proxied, *args, **kwargs) # type: ignore

    @staticmethod
    def get[Proxied](_: type[Proxied], self) -> Proxied:
        return self._proxied

proxy = Proxy()
