import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from content_generator import ContentGenerator
from video_editor import TalkingHeadVideoCreator
from youtube_uploader import YouTubeUploader

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_banner():
    logger.info("""
    *********************************
    *  YOUTUBE SHORTS AUTOMATION    *
    *       v1.0 - PRODUCTION       *
    *********************************
    """)

def cleanup():
    """Remove temporary files"""
    temp_dir = "temp"
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.error(f"Failed to delete {file_path}: {e}")

def test_upload():
    try:
        print_banner()
        start_time = time.time()
        
        # 1. Generate content
        logger.info("\n=== STEP 1: CONTENT GENERATION ===")
        content = ContentGenerator()
        script = content.generate_script()
        logger.info(f"\nGenerated Script:\nTitle: {script['title']}\nHashtags: {script['hashtags']}")
        
        # 2. Get assets
        logger.info("\n=== STEP 2: ASSET SELECTION ===")
        assets = content.get_random_assets()
        logger.info(f"Selected assets:\nImage: {assets['image']}\nThumbnail: {assets['thumb']}")
        
        # 3. Create video
        logger.info("\n=== STEP 3: VIDEO CREATION ===")
        video_creator = TalkingHeadVideoCreator()
        video_path = video_creator.create_video(script, assets["image"])
        
        # 4. Upload to YouTube
        logger.info("\n=== STEP 4: YOUTUBE UPLOAD ===")
        uploader = YouTubeUploader()
        response = uploader.upload(video_path, script)
        
        logger.info(f"\n🎉 SUCCESS! Video published: https://youtu.be/{response['id']}")
        logger.info(f"⏱️ Total execution time: {time.time() - start_time:.2f} seconds")
        
        return response['id']
        
    except Exception as e:
        logger.error(f"\n❌ ERROR: {str(e)}", exc_info=True)
        raise
    finally:
        cleanup()

if __name__ == "__main__":
    # Create required folders
    os.makedirs("output", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    # Add random delay (0-30 minutes) if running in automation
    if os.getenv('AUTOMATED_RUN'):
        delay = int(os.getenv('DELAY_SECONDS', '0'))
        logger.info(f"⏳ Adding random delay of {delay//60} minutes")
        time.sleep(delay)
    
    test_upload()
    logger.info("\nProcess completed. Check the output folder for your video.")