import requests
from bs4 import BeautifulSoup
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Database setup
DB_NAME = "jobs.db"

def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            link TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def save_job_to_db(title, company, location, link):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO jobs (title, company, location, link)
            VALUES (?, ?, ?, ?)
        ''', (title, company, location, link))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Skip duplicate links
    conn.close()

# Web scraping
def scrape_jobs():
    url = "https://in.indeed.com/jobs?q=python+developer&l=remote"  # Example URL
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = soup.find_all("div", class_="job_seen_beacon")
    new_jobs = []
    for job in jobs:
        title = job.find("h2", class_="jobTitle").text.strip()
        company = job.find("span", class_="companyName").text.strip()
        location = job.find("div", class_="companyLocation").text.strip()
        link = "https://in.indeed.com" + job.find("a")["href"]
        save_job_to_db(title, company, location, link)
        new_jobs.append((title, company, location, link))
    return new_jobs

# Email notification
def send_email(new_jobs):
    sender_email = "billubhavika@gmail.com"
    sender_password = "Bh@v!y@d@v8142"
    receiver_email = "billubhaviyadav@gmail.com"

    subject = "New Job Listings for Python Developers"
    body = "Here are the latest job listings:\n\n"
    for job in new_jobs:
        body += f"Title: {job[0]}\nCompany: {job[1]}\nLocation: {job[2]}\nLink: {job[3]}\n\n"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Main function
def main():
    initialize_database()
    new_jobs = scrape_jobs()
    if new_jobs:
        send_email(new_jobs)
    else:
        print("No new jobs found.")

if __name__ == "__main__":
    main()
