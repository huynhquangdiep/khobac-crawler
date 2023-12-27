import schedule
import time
import subprocess

def job():
    subprocess.run(['python', 'crawler.py'])

# Schedule the job to run every day at 3:30 PM
# schedule.every(3).seconds.do(job)
schedule.every().day.at("15:08").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)