import subprocess

def convert_video_to_audio(video_path, output_path):
    """Convert video to audio using the system's FFmpeg installation."""
    try:
        # Call FFmpeg command to convert video to audio
        command = ['ffmpeg', '-i', video_path, output_path]
        print(f"Running command: {' '.join(command)}")
        subprocess.run(command, check=True)
        return f"Audio saved at {output_path}"
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg command failed: {e}")
        return f"FFmpeg error: {e}"
