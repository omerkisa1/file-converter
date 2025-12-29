from abc import ABC, abstractmethod
from typing import List


class BaseConverter(ABC):
    
    @property
    @abstractmethod
    def supported_input_formats(self) -> List[str]:
        pass
    
    @property
    @abstractmethod
    def supported_output_formats(self) -> List[str]:
        pass
    
    @abstractmethod
    def convert(self, input_path: str, output_format: str) -> str:
        pass
    
    def can_convert(self, input_format: str, output_format: str) -> bool:
        return (
            input_format.lower() in self.supported_input_formats and
            output_format.lower() in self.supported_output_formats
        )
