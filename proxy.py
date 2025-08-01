from typing import Callable

class Proxy:
    """
    A utility class for creating proxy objects that delegate attribute access
    and method calls to an underlying proxied object, while allowing the
    proxy class to define its own behavior. This is designed to work well
    with LSP autocompletions.
    """
    @staticmethod
    def __call__[ProxyType, Proxied](proxied: type[Proxied]) -> Callable[[type[ProxyType]], type[ProxyType]]:
        def make_proxy(cls: type[ProxyType]) -> type[ProxyType]:
            def init(self, proxied: Proxied, *args, **kwargs):
                self._proxied = proxied
                if cls.__init__ is not proxied.__class__.__init__:
                    cls.__init__(self, *args, **kwargs)

            def get(self, name: str):
                return getattr(self._proxied, name)

            def dir_(self):
                combined_members = set(dir(cls))
                combined_members.update(self.__dict__.keys())
                combined_members.update(dir(self._proxied))
                return list(combined_members)

            bases = tuple(b for b in cls.__bases__ if b is not proxied)
            members = dict(cls.__dict__)
            members.update({
                '__init__': init,
                '__getattr__': get,
                '__dir__': dir_,
            })
            return type(cls.__name__, bases, members) # type: ignore
        return make_proxy

    @staticmethod
    def create[ProxyType](proxy: type[ProxyType], proxied, *args, **kwargs) -> ProxyType:
        """
        Creates an instance of a proxy class, binding it to a proxied object.

        This is the recommended way to instantiate a proxy object.

        Args:
            proxy: The proxy class (decorated with `@proxy`).
            proxied: The object to be proxied.
            *args: Arguments to pass to the proxy class's `__init__` method.
            **kwargs: Keyword arguments to pass to the proxy class's `__init__` method.

        Returns:
            An instance of the proxy class.
        """
        return proxy(proxied, *args, **kwargs) # type: ignore

    @staticmethod
    def get[Proxied](_: type[Proxied], self) -> Proxied:
        """
        Retrieves the original proxied object from a proxy instance.
        This is useful when you need to access the underlying object directly.
        """
        return self._proxied

proxy = Proxy()
