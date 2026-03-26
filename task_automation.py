import csv
import json
import urllib.request
import urllib.parse
from datetime import datetime
import time
import os

# ============================================================
#  CONFIGURATION
# ============================================================
TELEGRAM_TOKEN = "8637316009:AAEujvSg-vGTL_1Nn2qY4UoNg9Uu1xYyZE0"
CHAT_ID = None  # Will be auto-detected
SAMPLE_DATA_FILE = "tasks.csv"

# ============================================================
#  TELEGRAM
# ============================================================
def get_chat_id(token):
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    with urllib.request.urlopen(url, timeout=5) as r:
        data = json.loads(r.read())
    if data["result"]:
        return data["result"][-1]["message"]["chat"]["id"]
    return None

def send_telegram(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "HTML"}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())

# ============================================================
#  CREATE SAMPLE CSV
# ============================================================
def create_sample_csv():
    tasks = [
        {"id": "1", "task": "Follow up with client A", "due_date": "2026-03-26", "priority": "High", "status": "Pending"},
        {"id": "2", "task": "Submit project report", "due_date": "2026-03-27", "priority": "High", "status": "Pending"},
        {"id": "3", "task": "Review pull requests", "due_date": "2026-03-28", "priority": "Medium", "status": "Pending"},
        {"id": "4", "task": "Update documentation", "due_date": "2026-03-29", "priority": "Low", "status": "Pending"},
        {"id": "5", "task": "Deploy to production", "due_date": "2026-03-26", "priority": "High", "status": "Pending"},
    ]
    with open(SAMPLE_DATA_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "task", "due_date", "priority", "status"])
        writer.writeheader()
        writer.writerows(tasks)
    print(f"  ✅ Created sample data: {SAMPLE_DATA_FILE}")

# ============================================================
#  READ & FILTER TASKS
# ============================================================
def read_tasks():
    tasks = []
    with open(SAMPLE_DATA_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(row)
    return tasks

def filter_urgent(tasks):
    today = datetime.now().strftime("%Y-%m-%d")
    return [t for t in tasks if t["due_date"] <= today and t["status"] == "Pending"]

def filter_by_priority(tasks, priority):
    return [t for t in tasks if t["priority"] == priority]

# ============================================================
#  REPORT
# ============================================================
def generate_report(tasks):
    total = len(tasks)
    urgent = len(filter_urgent(tasks))
    high = len(filter_by_priority(tasks, "High"))
    medium = len(filter_by_priority(tasks, "Medium"))
    low = len(filter_by_priority(tasks, "Low"))

    report = (
        f"📋 <b>Task Automation Report</b>\n"
        f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"📊 <b>Summary:</b>\n"
        f"  • Total tasks: {total}\n"
        f"  • 🔴 Urgent (due today): {urgent}\n"
        f"  • High priority: {high}\n"
        f"  • Medium priority: {medium}\n"
        f"  • Low priority: {low}\n\n"
    )

    if urgent > 0:
        report += "⚠️ <b>Urgent Tasks:</b>\n"
        for t in filter_urgent(tasks):
            report += f"  • [{t['priority']}] {t['task']}\n"

    return report

# ============================================================
#  MAIN
# ============================================================
def main():
    print("=" * 55)
    print("  ⚙️  Task Automation System")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    # Step 1: Create sample data
    print("\n  📁 Step 1: Loading task data...")
    create_sample_csv()

    # Step 2: Read & analyze
    print("  📊 Step 2: Analyzing tasks...")
    tasks = read_tasks()
    urgent = filter_urgent(tasks)
    print(f"  Found {len(tasks)} total tasks, {len(urgent)} urgent")

    # Step 3: Generate report
    print("  📝 Step 3: Generating report...")
    report = generate_report(tasks)
    print("\n" + "-" * 55)
    print(report.replace("<b>", "").replace("</b>", ""))

    # Step 4: Send Telegram notification
    print("  📲 Step 4: Sending Telegram notification...")
    chat_id = get_chat_id(TELEGRAM_TOKEN)
    if chat_id:
        send_telegram(TELEGRAM_TOKEN, chat_id, report)
        print(f"  ✅ Notification sent to chat {chat_id}")
    else:
        print("  ⚠️  No chat ID found — send any message to your bot first")

    print("=" * 55)
    print("  ✅ Automation complete!")
    print("=" * 55)

if __name__ == "__main__":
    main()
