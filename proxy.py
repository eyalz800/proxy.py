# pyright: strict

from typing import Callable, Any

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
            class meta(type(cls)): # type: ignore [misc] # pyright: ignore [reportUntypedBaseClass]
                def __dir__(self):
                    combined_members = set(dir(cls))
                    combined_members.update(dir(proxied))
                    return list(combined_members)

            def new(cls: type[ProxyType], *args: Any, **kwargs: Any) -> ProxyType:
                proxy = super(cls, cls).__new__(cls) # type: ignore [misc]
                proxy._proxied = None # type: ignore [attr-defined] # pyright: ignore [reportAttributeAccessIssue]
                return proxy

            def init(self: ProxyType, *args: Any, **kwargs: Any):
                if cls.__init__ is not proxied.__init__:
                    cls.__init__(self, *args, **kwargs)

            def get(self: ProxyType, name: str):
                return getattr(self._proxied, name) # type: ignore [attr-defined] # pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownArgumentType]

            def dir_(self: ProxyType):
                combined_members = set(dir(cls))
                combined_members.update(self.__dict__.keys())
                combined_members.update(dir(self._proxied)) # type: ignore [attr-defined] # pyright: ignore [reportUnknownMemberType, reportAttributeAccessIssue, reportUnknownArgumentType]
                return list(combined_members)

            bases = tuple(b for b in cls.__bases__ if b is not proxied)
            members = {k: v for k, v in cls.__dict__.items() if k not in ('__dict__', '__weakref__')}
            members.update({
                '__new__': new,
                '__init__': init,
                '__getattr__': get,
                '__dir__': dir_,
            })
            return meta(cls.__name__, bases, members) # type: ignore [return-value] # pyright: ignore [reportReturnType]
        return make_proxy

    @staticmethod
    def create[ProxyType](proxy: type[ProxyType], proxied: Any, *args: Any, **kwargs: Any) -> ProxyType:
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
        proxy_obj = object.__new__(proxy)
        Proxy.set(proxy_obj, proxied)
        proxy_obj.__init__(*args, **kwargs) # type: ignore [misc]
        return proxy_obj

    @staticmethod
    def get[Proxied](_: type[Proxied], proxy: Any) -> Proxied:
        """
        Retrieves the original proxied object from a proxy instance.
        This is useful when you need to access the underlying object directly.
        """
        return proxy._proxied

    @staticmethod
    def set(proxy: Any, proxied: Any):
        """
        Sets a new proxy object in place of the previous one.
        This is useful when you need to set the underlying object directly.
        """
        proxy._proxied = proxied

proxy = Proxy()
