import os
from typing import List
from PIL import Image
from core.base_converter import BaseConverter


class ImageConverter(BaseConverter):
    
    @property
    def supported_input_formats(self) -> List[str]:
        return ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "ico", "svg", "heic", "heif"]
    
    @property
    def supported_output_formats(self) -> List[str]:
        return ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "ico"]
    
    def convert(self, input_path: str, output_format: str) -> str:
        output_format = output_format.lower().lstrip(".")
        input_ext = os.path.splitext(input_path)[1].lower().lstrip(".")
        
        if output_format == "jpg":
            output_format = "jpeg"
        
        base_name = os.path.splitext(input_path)[0]
        ext = "jpg" if output_format == "jpeg" else output_format
        output_path = f"{base_name}_converted.{ext}"
        
        if input_ext == "svg":
            return self._convert_svg(input_path, output_path, output_format)
        
        if input_ext in ("heic", "heif"):
            return self._convert_heic(input_path, output_path, output_format)
        
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
            elif output_format == "ico":
                sizes = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]
                save_kwargs["sizes"] = sizes
            
            img.save(output_path, format=output_format.upper(), **save_kwargs)
        
        return output_path
    
    def _convert_svg(self, input_path: str, output_path: str, output_format: str) -> str:
        try:
            import cairosvg
        except ImportError:
            raise RuntimeError("SVG conversion requires cairosvg: pip install cairosvg")
        
        if output_format == "png":
            cairosvg.svg2png(url=input_path, write_to=output_path)
        elif output_format in ("jpeg", "jpg"):
            png_temp = output_path.replace(".jpg", "_temp.png").replace(".jpeg", "_temp.png")
            cairosvg.svg2png(url=input_path, write_to=png_temp)
            with Image.open(png_temp) as img:
                rgb_img = img.convert("RGB")
                rgb_img.save(output_path, "JPEG", quality=95)
            os.remove(png_temp)
        else:
            png_temp = output_path.rsplit(".", 1)[0] + "_temp.png"
            cairosvg.svg2png(url=input_path, write_to=png_temp)
            with Image.open(png_temp) as img:
                if img.mode in ("RGBA", "LA", "P") and output_format in ("jpeg", "jpg"):
                    img = img.convert("RGB")
                img.save(output_path)
            os.remove(png_temp)
        
        return output_path
    
    def _convert_heic(self, input_path: str, output_path: str, output_format: str) -> str:
        try:
            from pillow_heif import register_heif_opener
            register_heif_opener()
        except ImportError:
            raise RuntimeError("HEIC conversion requires pillow-heif: pip install pillow-heif")
        
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "LA", "P") and output_format in ("jpeg", "jpg"):
                img = img.convert("RGB")
            
            save_kwargs = {}
            if output_format == "jpeg":
                save_kwargs["quality"] = 95
            
            img.save(output_path, format=output_format.upper(), **save_kwargs)
        
        return output_path

