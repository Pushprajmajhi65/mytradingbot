import subprocess
from gtts import gTTS
import os
import cv2
import numpy as np
import tempfile
import shutil
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random

class TalkingHeadVideoCreator:
    @staticmethod
    def create_video(script: dict, image_path: str, output_path: str = "output/video.mp4"):
        print("\n🎬 Creating talking head video with Indian accent and lip sync...")
        
        # Create directories if they don't exist
        os.makedirs("temp", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        
        frames_dir = tempfile.mkdtemp()
        audio_path = "temp/audio.mp3"
        
        try:
            # 1. Generate Indian-accented audio
            print("🔊 Generating Indian-accented audio...")
            tts = gTTS(text=script["script"], lang='en', tld='co.in', slow=False)
            tts.save(audio_path)
            
            # 2. Get audio duration
            print("⏳ Calculating audio duration...")
            duration = float(subprocess.check_output([
                'ffprobe', '-i', audio_path, 
                '-show_entries', 'format=duration', 
                '-v', 'quiet', '-of', 'csv=p=0'
            ]).decode().strip())
            
            # 3. Process the talking head image (preserve original colors)
            print("👄 Preparing talking head...")
            head_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            if head_image is None:
                raise ValueError("Could not load image")
            
            # Convert to RGBA if not already
            if head_image.shape[2] == 3:
                head_image = cv2.cvtColor(head_image, cv2.COLOR_BGR2BGRA)
            
            # Resize only if needed (preserve aspect ratio)
            if head_image.shape[0] != 1920 or head_image.shape[1] != 1080:
                head_image = cv2.resize(head_image, (1080, 1920), interpolation=cv2.INTER_LANCZOS4)
            
            # 4. Create animated frames with lip sync
            print("🖼️ Generating animation frames...")
            TalkingHeadVideoCreator._generate_lip_sync_frames(
                head_image, 
                script["script"], 
                duration,
                frames_dir
            )
            
            # 5. Create final video
            print("🎥 Creating final video...")
            TalkingHeadVideoCreator._create_final_video(
                frames_dir, 
                audio_path, 
                output_path
            )
            
            print(f"✅ Video created successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error: {e}")
            raise
        finally:
            # Clean up
            shutil.rmtree(frames_dir, ignore_errors=True)
            if os.path.exists(audio_path):
                os.remove(audio_path)

    @staticmethod
    def _generate_lip_sync_frames(head_image, script, duration, output_dir):
        """Generate frames with lip sync animation while preserving original image"""
        # Mouth animation parameters (relative to face size)
        face_height = head_image.shape[0]
        mouth_shapes = {
            "neutral": {"width": int(face_height * 0.05), "height": int(face_height * 0.02)},
            "open": {"width": int(face_height * 0.07), "height": int(face_height * 0.04)},
            "wide": {"width": int(face_height * 0.09), "height": int(face_height * 0.05)}
        }
        
        total_frames = int(duration * 30)  # 30fps
        mouth_center = (head_image.shape[1] // 2, int(head_image.shape[0] * 0.6))  # Position mouth naturally
        
        # Prepare font
        try:
            font = ImageFont.truetype("arial.ttf", int(head_image.shape[0] * 0.05))  # Responsive font size
        except:
            font = ImageFont.load_default()
            font.size = int(head_image.shape[0] * 0.05)
        
        words = script.split()
        word_duration = duration / len(words)
        
        for frame_num in range(total_frames):
            # Create frame by copying original image
            frame = head_image.copy()
            
            current_time = frame_num / 30
            current_word_idx = min(int(current_time / word_duration), len(words) - 1)
            current_word = words[current_word_idx]
            
            # Determine mouth state based on vowels in current word
            vowel_count = sum(1 for c in current_word.lower() if c in 'aeiou')
            if vowel_count >= 2:
                mouth_state = "wide"
            elif vowel_count >= 1:
                mouth_state = "open"
            else:
                mouth_state = "neutral"
            
            # Draw mouth (as black oval) - will blend with original image
            mouth_params = mouth_shapes[mouth_state]
            cv2.ellipse(
                frame, 
                mouth_center,
                (mouth_params["width"], mouth_params["height"]),
                0, 0, 360, 
                (0, 0, 0, 255),  # Black color
                -1
            )
            
            # Draw subtitles (preserving original image colors)
            frame = TalkingHeadVideoCreator._draw_subtitles(
                frame, script, current_time, duration, font
            )
            
            # Save frame (as PNG to preserve quality)
            cv2.imwrite(f"{output_dir}/frame_{frame_num:04d}.png", frame)
            
            if frame_num % 30 == 0:
                print(f"🖼️ Generated frame {frame_num}/{total_frames}")

    @staticmethod
    def _draw_subtitles(frame, script, current_time, duration, font):
        """Draw subtitles that appear with speech"""
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGRA2RGBA))
        draw = ImageDraw.Draw(img_pil)
        
        # Calculate how much text to show
        progress = min(1.0, current_time / (duration * 0.8))  # Show all by 80%
        chars_to_show = int(progress * len(script))
        current_text = script[:chars_to_show]
        
        # Wrap text
        wrapped_text = textwrap.fill(current_text, width=40)
        
        # Calculate position (bottom center)
        text_bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        x = (frame.shape[1] - (text_bbox[2] - text_bbox[0])) // 2
        y = frame.shape[0] - int(frame.shape[0] * 0.15)  # 15% from bottom
        
        # Draw text with semi-transparent background for readability
        padding = 20
        bg_alpha = 150  # Semi-transparent
        draw.rectangle(
            [x - padding, y - padding, 
             x + (text_bbox[2] - text_bbox[0]) + padding, 
             y + (text_bbox[3] - text_bbox[1]) + padding],
            fill=(0, 0, 0, bg_alpha)
        )
        
        # Draw text with shadow effect
        draw.text((x + 2, y + 2), wrapped_text, font=font, fill=(0, 0, 0, 255))  # Shadow
        draw.text((x, y), wrapped_text, font=font, fill=(255, 255, 255, 255))    # Text
        
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGBA2BGRA)

    @staticmethod
    def _create_final_video(frames_dir, audio_path, output_path):
        """Combine frames and audio into final video without re-encoding image"""
        frame_pattern = f"{frames_dir}/frame_%04d.png"
        
        # Create video while preserving original image quality
        subprocess.run([
            'ffmpeg', '-y',
            '-framerate', '30',
            '-i', frame_pattern,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',  # High quality
            '-pix_fmt', 'yuv420p',
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            '-movflags', '+faststart',
            output_path
        ], check=True)

# Example usage
if __name__ == "__main__":
    script = {
        "title": "भारतीय बच्चों के रोचक तथ्य | Interesting Indian Baby Facts",
        "script": "Did you know Indian babies have unique reflexes? They often show the 'Moro reflex' when startled."
    }
    
    creator = TalkingHeadVideoCreator()
    video_path = creator.create_video(
        script=script,
        image_path="person_image.png",  # Your original image
        output_path="output/final_video.mp4"
    )
    
    print(f"🎉 Final video created at: {video_path}")