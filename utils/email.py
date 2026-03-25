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
    # Calculate progress percentage for the top bar
    progress = min(max((day_num / total_days) * 100, 2), 100)

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    </head>
    <body style="margin:0; padding:0; background-color:#fcfcfd; font-family:'Inter', Helvetica, Arial, sans-serif; -webkit-font-smoothing:antialiased;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #fcfcfd;">
            <tr>
                <td align="center" style="padding: 20px 0 50px 0;">
                    
                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; margin-bottom: 20px;">
                        <tr>
                            <td style="font-size: 10px; color: #94a3b8; text-transform: uppercase; letter-spacing: 2px; padding-bottom: 8px;">
                                Progress: Day {day_num} of {total_days}
                            </td>
                        </tr>
                        <tr>
                            <td height="4" style="background-color: #f1f5f9; border-radius: 2px;">
                                <div style="background-color: #6366f1; width: {progress}%; height: 4px; border-radius: 2px;"></div>
                            </td>
                        </tr>
                    </table>

                    <table width="600" border="0" cellspacing="0" cellpadding="0" 
                           style="max-width: 600px; background-color: #ffffff; border: 1px solid #f1f5f9; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.03); overflow: hidden;">
                        
                        <tr>
                            <td style="padding: 60px 50px 40px 50px; text-align: left; border-bottom: 1px solid #f8fafc;">
                                <div style="color: #6366f1; font-weight: 700; font-size: 13px; margin-bottom: 15px; letter-spacing: 1px;">
                                    DAILY KNOWLEDGE RECAP
                                </div>
                                <h1 style="margin: 0; font-family: 'Playfair Display', serif; font-size: 42px; line-height: 1.1; color: #0f172a; letter-spacing: -1px;">
                                    {title}
                                </h1>
                            </td>
                        </tr>

                        <tr>
                            <td style="padding: 40px 50px; color: #334155; font-size: 17px; line-height: 1.8;">
                                <div style="color: #475569;">
                                    {html_body}
                                </div>
                            </td>
                        </tr>

                        <tr>
                            <td style="padding: 0 50px 60px 50px;">
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="border-top: 1px solid #f1f5f9; padding-top: 40px;">
                                    <tr>
                                        <td align="center">
                                            <p style="font-size: 14px; color: #94a3b8; margin-bottom: 20px; font-style: italic;">
                                                "Knowledge is the only asset that grows when shared."
                                            </p>
                                            <a href="#" style="background-color: #0f172a; color: #ffffff; padding: 18px 35px; border-radius: 12px; font-size: 15px; font-weight: 600; text-decoration: none; display: inline-block;">
                                                Mark Lesson as Learned
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>

                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; margin-top: 30px;">
                        <tr>
                            <td align="center" style="color: #94a3b8; font-size: 12px;">
                                <p style="margin: 5px 0;">Sent with ❤️ from Daily Knowledge</p>
                                <p style="margin: 5px 0;">
                                    <a href="#" style="color: #6366f1; text-decoration: none;">Profile</a> &nbsp;•&nbsp; 
                                    <a href="#" style="color: #6366f1; text-decoration: none;">Preferences</a> &nbsp;•&nbsp; 
                                    <a href="#" style="color: #6366f1; text-decoration: none;">Unsubscribe</a>
                                </p>
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
