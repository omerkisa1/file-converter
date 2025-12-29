from typing import Dict, List, Optional
from .base_converter import BaseConverter


class UnsupportedFormatError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ConverterFactory:
    _converters: List[BaseConverter] = []
    
    FORMAT_MAPPING: Dict[str, str] = {
        "jpg": "image",
        "jpeg": "image",
        "png": "image",
        "webp": "image",
        "gif": "image",
        "bmp": "image",
        "pdf": "document",
        "docx": "document",
        "mp4": "media",
        "mp3": "media",
        "wav": "media",
        "avi": "media",
        "mkv": "media",
        "mov": "media",
        "flac": "media",
        "ogg": "media",
    }
    
    @classmethod
    def register_converter(cls, converter: BaseConverter) -> None:
        cls._converters.append(converter)
    
    @classmethod
    def get_converter(cls, input_format: str, output_format: str) -> BaseConverter:
        input_fmt = input_format.lower().lstrip(".")
        output_fmt = output_format.lower().lstrip(".")
        
        for converter in cls._converters:
            if converter.can_convert(input_fmt, output_fmt):
                return converter
        
        raise UnsupportedFormatError(
            f"Cannot convert from '{input_fmt}' to '{output_fmt}'. "
            f"This conversion is not supported."
        )
    
    @classmethod
    def get_available_formats(cls, input_format: str) -> List[str]:
        input_fmt = input_format.lower().lstrip(".")
        available = []
        
        for converter in cls._converters:
            if input_fmt in converter.supported_input_formats:
                for fmt in converter.supported_output_formats:
                    if fmt != input_fmt and fmt not in available:
                        available.append(fmt)
        
        return available
    
    @classmethod
    def get_all_supported_formats(cls) -> Dict[str, List[str]]:
        result = {"input": [], "output": []}
        
        for converter in cls._converters:
            for fmt in converter.supported_input_formats:
                if fmt not in result["input"]:
                    result["input"].append(fmt)
            for fmt in converter.supported_output_formats:
                if fmt not in result["output"]:
                    result["output"].append(fmt)
        
        return result
