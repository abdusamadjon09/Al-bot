import asyncio
import os
import shutil
from pathlib import Path

async def edit_video(input_path: str, action: str):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return None
    out = str(Path(input_path).with_name(Path(input_path).stem + f"_{action}.mp4"))
    if action == "mp4":
        cmd = [ffmpeg, "-y", "-i", input_path, "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", out]
    elif action == "mute":
        cmd = [ffmpeg, "-y", "-i", input_path, "-an", "-c:v", "libx264", "-movflags", "+faststart", out]
    elif action == "916":
        cmd = [ffmpeg, "-y", "-i", input_path, "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2", "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", out]
    elif action == "169":
        cmd = [ffmpeg, "-y", "-i", input_path, "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2", "-c:v", "libx264", "-c:a", "aac", "-movflags", "+faststart", out]
    else:
        return None
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            return None
        return out
    except Exception:
        return None
