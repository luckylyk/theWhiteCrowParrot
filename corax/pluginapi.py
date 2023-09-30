from abc import abstractmethod, abstractproperty


class CoraxPluginShape():
    """
    Abstract classes defining all the methods and properties necessary to
    implement a custom behavior in the Corax Engine. Note that the entire
    Corax sources are available and importable from those modules.
    """
    ptype = 'plugin_shape'

    def __init__(self, name: str, scene, data: dict):
        super().__init__()
        self.name = name
        self.scene = scene
        self.data = data

    @abstractmethod
    def evaluate(self):
        """
        This method is triggered at each frame evaluation.
        """
        pass

    @abstractproperty
    def pixel_position(self) -> list:
        pass

    @abstractproperty
    def visible(self) -> bool:
        pass

    @abstractproperty
    def images(self) -> str:
        pass

    @abstractproperty
    def deph(self) -> float:
        pass

    @abstractmethod
    def collect_value(self, command) -> bool:
        pass

    @abstractmethod
    def execute_command(self, command: str) -> int:
        pass

    def render_debug(self, surface, layer_deph, camera):
        """
        Optionnal method to implement to implement a custom render in
        debugmode.
        """
        pass
