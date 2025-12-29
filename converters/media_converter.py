import os
from typing import List
from core.base_converter import BaseConverter


class MediaConverter(BaseConverter):
    
    @property
    def supported_input_formats(self) -> List[str]:
        return ["mp4", "avi", "mkv", "mov", "webm", "mp3", "wav", "flac", "ogg", "aac"]
    
    @property
    def supported_output_formats(self) -> List[str]:
        return ["mp4", "avi", "mkv", "mov", "webm", "mp3", "wav", "flac", "ogg", "aac"]
    
    VIDEO_FORMATS = {"mp4", "avi", "mkv", "mov", "webm"}
    AUDIO_FORMATS = {"mp3", "wav", "flac", "ogg", "aac"}
    
    def convert(self, input_path: str, output_format: str) -> str:
        from moviepy.editor import VideoFileClip, AudioFileClip
        
        input_ext = os.path.splitext(input_path)[1].lower().lstrip(".")
        output_format = output_format.lower().lstrip(".")
        
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}_converted.{output_format}"
        
        input_is_video = input_ext in self.VIDEO_FORMATS
        output_is_video = output_format in self.VIDEO_FORMATS
        output_is_audio = output_format in self.AUDIO_FORMATS
        
        if input_is_video and output_is_video:
            return self._convert_video_to_video(input_path, output_path, output_format)
        elif input_is_video and output_is_audio:
            return self._extract_audio_from_video(input_path, output_path, output_format)
        elif not input_is_video and output_is_audio:
            return self._convert_audio_to_audio(input_path, output_path, output_format)
        else:
            raise ValueError(f"Cannot convert {input_ext} to {output_format}")
    
    def _convert_video_to_video(self, input_path: str, output_path: str, output_format: str) -> str:
        from moviepy.editor import VideoFileClip
        
        codec_map = {
            "mp4": "libx264",
            "avi": "mpeg4",
            "mkv": "libx264",
            "mov": "libx264",
            "webm": "libvpx",
        }
        
        clip = VideoFileClip(input_path)
        codec = codec_map.get(output_format, "libx264")
        clip.write_videofile(output_path, codec=codec, logger=None)
        clip.close()
        
        return output_path
    
    def _extract_audio_from_video(self, input_path: str, output_path: str, output_format: str) -> str:
        from moviepy.editor import VideoFileClip
        
        clip = VideoFileClip(input_path)
        audio = clip.audio
        
        if output_format == "mp3":
            audio.write_audiofile(output_path, codec="libmp3lame", logger=None)
        elif output_format == "wav":
            audio.write_audiofile(output_path, codec="pcm_s16le", logger=None)
        elif output_format == "flac":
            audio.write_audiofile(output_path, codec="flac", logger=None)
        elif output_format == "ogg":
            audio.write_audiofile(output_path, codec="libvorbis", logger=None)
        elif output_format == "aac":
            audio.write_audiofile(output_path, codec="aac", logger=None)
        else:
            audio.write_audiofile(output_path, logger=None)
        
        audio.close()
        clip.close()
        
        return output_path
    
    def _convert_audio_to_audio(self, input_path: str, output_path: str, output_format: str) -> str:
        from moviepy.editor import AudioFileClip
        
        clip = AudioFileClip(input_path)
        
        if output_format == "mp3":
            clip.write_audiofile(output_path, codec="libmp3lame", logger=None)
        elif output_format == "wav":
            clip.write_audiofile(output_path, codec="pcm_s16le", logger=None)
        elif output_format == "flac":
            clip.write_audiofile(output_path, codec="flac", logger=None)
        elif output_format == "ogg":
            clip.write_audiofile(output_path, codec="libvorbis", logger=None)
        elif output_format == "aac":
            clip.write_audiofile(output_path, codec="aac", logger=None)
        else:
            clip.write_audiofile(output_path, logger=None)
        
        clip.close()
        
        return output_path
