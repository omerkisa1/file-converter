import os
from typing import List
from PIL import Image
from core.base_converter import BaseConverter


class ImageConverter(BaseConverter):
    
    @property
    def supported_input_formats(self) -> List[str]:
        return ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"]
    
    @property
    def supported_output_formats(self) -> List[str]:
        return ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"]
    
    def convert(self, input_path: str, output_format: str) -> str:
        output_format = output_format.lower().lstrip(".")
        
        if output_format == "jpg":
            output_format = "jpeg"
        
        base_name = os.path.splitext(input_path)[0]
        
        ext = "jpg" if output_format == "jpeg" else output_format
        output_path = f"{base_name}_converted.{ext}"
        
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "LA", "P") and output_format in ("jpeg", "jpg"):
                img = img.convert("RGB")
            
            save_kwargs = {}
            if output_format == "jpeg":
                save_kwargs["quality"] = 95
            elif output_format == "webp":
                save_kwargs["quality"] = 90
            elif output_format == "png":
                save_kwargs["optimize"] = True
            
            img.save(output_path, format=output_format.upper(), **save_kwargs)
        
        return output_path
