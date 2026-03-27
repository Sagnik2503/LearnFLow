import markdown
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()


def markdown_to_html(md_content: str) -> str:
    return markdown.markdown(md_content, extensions=["extra", "codehilite", "tables"])


def wrap_email_html(
    title: str, html_body: str, day_num: int = 1, total_days: int = 30
) -> str:
    progress = int((day_num / total_days) * 100)

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0; padding:0; background:#f4f1ed; font-family:Arial, sans-serif;">

    <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
    <td align="center">

    <!-- MAIN CARD -->
    <table width="600" cellpadding="0" cellspacing="0" 
    style="background:#ffffff; border-radius:16px; overflow:hidden; margin-top:30px;">

        <!-- HERO -->
        <tr>
        <td style="background:#FDF4EE; padding:50px;">
            <div style="font-size:11px; letter-spacing:2px; color:#8C3A14; margin-bottom:15px;">
                ● DAILY KNOWLEDGE RECAP
            </div>

            <h1 style="font-family:Georgia, serif; font-size:38px; margin:0; color:#1A1410;">
                {title}
            </h1>

            <p style="font-size:13px; color:#7A6A58; margin-top:10px;">
                {total_days - day_num} lessons remaining
            </p>
        </td>
        </tr>

        <!-- PROGRESS -->
        <tr>
        <td style="padding:20px 50px;">
            <div style="height:6px; background:#eee; border-radius:3px;">
                <div style="width:{progress}%; height:6px; background:#D4622A;"></div>
            </div>
            <p style="font-size:12px; color:#7A6A58;">Day {day_num} of {total_days}</p>
        </td>
        </tr>

        <!-- BODY -->
        <tr>
        <td style="padding:40px 50px; color:#3D3028; font-size:16px; line-height:1.8;">
            {html_body}
        </td>
        </tr>

        <!-- CTA -->
        <tr>
        <td align="center" style="padding:30px;">
            <a href="#" style="background:#1A1410; color:white; padding:14px 28px; 
            border-radius:8px; text-decoration:none; font-size:14px;">
            Mark as Learned ✓
            </a>
        </td>
        </tr>

    </table>

    <!-- FOOTER -->
    <table width="600" cellpadding="0" cellspacing="0" style="margin-top:20px;">
        <tr>
        <td align="center" style="font-size:12px; color:#7A6A58;">
            "Knowledge is the only asset that grows when shared."
        </td>
        </tr>
    </table>

    </td>
    </tr>
    </table>

    </body>
    </html>
    """


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
):
    sender_email = "sagniksengupta2503@gmail.com"
    app_password = os.getenv("EMAIL_APP_PASSWORD")  # ⚠️ use Gmail App Password

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, to_email, msg.as_string())

        print(f"✅ Email sent to {to_email}")

    except Exception as e:
        print("❌ Failed to send email:", str(e))


def send_newsletter_email(
    to_email: str,
    subject: str,
    markdown_content: str,
):
    # 1. Convert markdown → HTML
    html_body = markdown_to_html(markdown_content)

    # 2. Beautify
    full_html = wrap_email_html(subject, html_body)

    # 3. Send
    send_email(to_email, subject, full_html)
