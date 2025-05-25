import os
import random
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class ContentGenerator:
    def __init__(self):
        print("Initializing Baby Finance Podcast Content Generator...")
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.themes = [
            "saving money",
            "investing basics",
            "emergency funds",
            "budgeting tips",
            "credit card traps",
            "compound interest",
            "side hustle ideas",
            "money mindset",
            "financial freedom",
            "passive income for beginners"
        ]
        print("✅ Ready to generate baby-style financial advice")

    def generate_script(self):
        print("\n🍼 Generating baby podcast script...")
        theme = random.choice(self.themes)
        print(f"Selected theme: {theme}")
        
        prompt = f"""You are a cute Indian baby giving funny but wise financial advice in a podcast style.
Create a 50-word YouTube Short script about "{theme}" in Hindi with:
- a baby-style hook in the first 3 seconds (make it cute)
- 1 surprising or useful fact
- a call to action at the end
Return as JSON with keys: title, script, hashtags"""
        
        try:
            print("Calling OpenAI API...")
            response = self.openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8
            )
            content = response.choices[0].message.content
            print("Received API response")
            
            try:
                script = json.loads(content)
                print("✅ Script generated successfully")
                return script
            except json.JSONDecodeError:
                print("⚠️ API returned non-JSON response, using fallback formatting")
                return {
                    "title": f"Cute Baby Talks: {theme.title()}",
                    "script": content,
                    "hashtags": "#babyfinance #podcastshorts #indianbaby"
                }
                
        except Exception as e:
            print(f"❌ Error generating script: {e}")
            return self._default_script(theme)

    def _default_script(self, theme):
        print("⚠️ Using fallback script")
        return {
            "title": f"Baby's Tip on {theme.title()}",
            "script": f"Namaste! Baby kehta hai, {theme} zaroori hai. Paisa bachaao, kal banaao! Follow karo aur seekho!",
            "hashtags": "#babyfinance #shorts #funnybaby"
        }

    def get_random_assets(self):
        print("\n🎨 Selecting baby podcast assets...")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        baby_images_dir = os.path.join(base_dir, "assets", "AI_baby_image")
        
        print(f"Looking for images in: {baby_images_dir}")
        images = [f for f in os.listdir(baby_images_dir) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if not images:
            raise ValueError("❌ No baby images found in assets/AI_baby_image")
        
        thumbs_dir = os.path.join(base_dir, "assets", "thum")
        thumbs = []
        if os.path.exists(thumbs_dir):
            thumbs = [f for f in os.listdir(thumbs_dir) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        selected_image = random.choice(images)
        print(f"Selected image: {selected_image}")
        
        return {
            "image": os.path.join(baby_images_dir, selected_image),
            "thumb": os.path.join(thumbs_dir, random.choice(thumbs)) if thumbs else ""
        }