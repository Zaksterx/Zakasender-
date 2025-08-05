import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import traceback
import os

# ========== معلومات المستخدم ==========
user_email = "zakariaouadighcih@gmail.com"
speciality_keywords = [
    "réseau", "système", "infrastructure", "IT", 
    "technicien", "support", "windows server", "linux", 
    "administration", "informatique", "cisco"
]

# ========== Gmail الخاص بالإرسال ==========
GMAIL_ADRESSE = "zakariaouadigh16@gmail.com"
GMAIL_APP_PASSWORD = "cqnb bomx jbis vjak"  # ⚠️ تأكد أنها App Password صالحة

# ========== Scraper: stagiaire.ma ==========
def scrape_stagiaire():
    try:
        url = "https://stagiaire.ma/offres-stage"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        for job in soup.select(".job-title a")[:10]:
            title = job.text.strip()
            link = "https://stagiaire.ma" + job['href']
            results.append(f"📌 {title}\n🔗 {link}")
        return results
    except Exception as e:
        print(f"❌ Error scraping stagiaire.ma: {e}")
        traceback.print_exc()
        return []

# ========== Scraper: marocannonces.com ==========
def scrape_marocannonces():
    try:
        url = "https://www.marocannonces.com/maroc/emplois-offres/informatique-multimedia-internet/21.html"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        results = []
        for a in soup.select("ul.cars-list .title a")[:10]:
            title = a.text.strip()
            link = a['href']
            if not link.startswith('http'):
                link = "https://www.marocannonces.com" + link
            results.append(f"📌 {title}\n🔗 {link}")
        return results
    except Exception as e:
        print(f"❌ Error scraping marocannonces.com: {e}")
        traceback.print_exc()
        return []

# ========== إرسال الإيميل ==========
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_ADRESSE
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ADRESSE, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADRESSE, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email successfully sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        traceback.print_exc()

# ========== فلترة العروض ==========
def filter_offers(offers, keywords):
    return [offer for offer in offers if any(kw.lower() in offer.lower() for kw in keywords)]

# ========== إرسال رسالة ترحيبية أول مرة فقط ==========
def send_welcome_once():
    if not os.path.exists("first_run.txt"):
        msg = "✅ connected! غادي نرسل ليك العروض كل نهار.\n\n– Zakasender"
        send_email(user_email, "🤖 Zakasender", msg)
        with open("first_run.txt", "w") as f:
            f.write("done")

# ========== البرنامج الرئيسي ==========
def main():
    print("--- Starting Job Scan ---")
    send_welcome_once()

    print("🔎 Fetching new job offers...")
    all_offers = scrape_stagiaire() + scrape_marocannonces()

    print(f"✅ Total scraped offers: {len(all_offers)}")
    relevant = filter_offers(all_offers, speciality_keywords)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if relevant:
        subject = f"📢 {len(relevant)} عرض عمل جديد في تخصصك!"
        message = f"مرحباً،\n\nتم العثور على {len(relevant)} عرض عمل جديد قد يهمك:\n\n"
        message += "\n\n---\n\n".join(relevant)
        message += f"\n\n--- \nتم البحث في: {now}"
        send_email(user_email, subject, message)
        print(f"📨 Email sent to {user_email} with {len(relevant)} relevant offers.")
    else:
        subject = "✔️ تقرير يومي: لا توجد عروض جديدة"
        message = f"مرحباً،\n\n لم يتم العثور على عروض سطاج  او عمل اليوم.\n\n--- \nوقت التشغيل: {now}"
        send_email(user_email, subject, message)
        print("⚠️ No relevant offers found. A report email has been sent.")

    print("--- Scan Finished ---")

if __name__ == "__main__":
    main()
