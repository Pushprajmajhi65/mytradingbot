# from apscheduler.schedulers.blocking import BlockingScheduler
# from datetime import datetime
# import random
# import time
# import logging
# from main import test_upload

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('automation.log'),
#         logging.StreamHandler()
#     ]
# )

# def job():
#     try:
#         logging.info("🚀 Starting scheduled video creation job")
#         current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         logging.info(f"⏰ Execution time: {current_time}")
        
#         # Add random delay (0-30 minutes)
#         delay_minutes = random.randint(0, 30)
#         logging.info(f"⏳ Adding random delay of {delay_minutes} minutes")
#         time.sleep(delay_minutes * 60)
        
#         test_upload()
        
#     except Exception as e:
#         logging.error(f"❌ Error in scheduled job: {str(e)}")

# if __name__ == "__main__":
#     scheduler = BlockingScheduler()
    
#     # Schedule for 9-11 AM, 12-2 PM, and 6-9 PM windows (UTC time)
#     # Adjust these times according to your timezone (UTC+5:30 for IST)
#     scheduler.add_job(job, 'cron', hour='3-5', minute='0')      # 9-11 AM IST
#     scheduler.add_job(job, 'cron', hour='6-8', minute='0')      # 12-2 PM IST
#     scheduler.add_job(job, 'cron', hour='12-15', minute='0')    # 6-9 PM IST
    
#     logging.info("⏰ Scheduler started. Waiting for scheduled jobs...")
#     try:
#         scheduler.start()
#     except (KeyboardInterrupt, SystemExit):
#         logging.info("🛑 Scheduler stopped")