class Container:
    def __init__(self):
        self.dependencies = {}

    def register(self, name, dependency):
        self.dependencies[name] = dependency

    def resolve(self, name):
        return self.dependencies.get(name)


container = Container()


def inject(**kwargs):
    def decorator(cls):
        original_init = cls.__init__

        def new_init(self, *args, **new_kwargs):
            for name, dependency_name in kwargs.items():
                setattr(self, name, container.resolve(dependency_name))
            original_init(self, *args, **new_kwargs)

        cls.__init__ = new_init
        return cls

    return decorator
