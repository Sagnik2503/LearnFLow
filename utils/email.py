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
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0; padding: 0; background-color: #f4f1ed;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                -webkit-font-smoothing: antialiased;
                color: #3d3028;
            }}
            .email-wrapper {{ width: 100%; table-layout: fixed; background-color: #f4f1ed; padding-bottom: 40px; }}
            .email-content {{ max-width: 600px; margin: 0 auto; width: 100%; }}
            .card {{
                background-color: #ffffff; border-radius: 12px;
                overflow: hidden; margin-top: 30px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            }}
            .hero {{ background-color: #FDF4EE; padding: 40px 50px; text-align: left; }}
            .hero-label {{ font-size: 12px; font-weight: 600; letter-spacing: 1.5px; color: #D4622A; margin-bottom: 12px; text-transform: uppercase; }}
            .hero h1 {{ font-family: "Georgia", serif; font-size: 32px; margin: 0; color: #1a1410; line-height: 1.2; }}
            .hero p {{ font-size: 14px; color: #7a6a58; margin-top: 12px; margin-bottom: 0; }}
            
            .progress-container {{ padding: 20px 50px; border-bottom: 1px solid #f4f1ed; }}
            .progress-bar-bg {{ height: 6px; background-color: #eee; border-radius: 3px; overflow: hidden; }}
            .progress-bar-fill {{ width: {progress}%; height: 100%; background-color: #D4622A; border-radius: 3px; }}
            .progress-text {{ font-size: 13px; color: #7a6a58; margin-top: 8px; font-weight: 500; display: block; }}
            
            .body-content {{ padding: 40px 50px; }}
            .body-content h1, .body-content h2, .body-content h3, .body-content h4 {{
                font-family: "Georgia", serif; color: #1a1410; margin-top: 1.8em; margin-bottom: 0.6em; line-height: 1.3;
            }}
            .body-content h2 {{ font-size: 24px; border-bottom: 1px solid #eaeaea; padding-bottom: 8px; }}
            .body-content h3 {{ font-size: 20px; color: #D4622A; }}
            .body-content p {{ font-size: 16px; line-height: 1.7; margin-bottom: 1.5em; color: #3d3028; }}
            .body-content ul, .body-content ol {{ margin-bottom: 1.5em; padding-left: 1.5em; }}
            .body-content li {{ font-size: 16px; line-height: 1.7; margin-bottom: 0.5em; color: #3d3028; }}
            .body-content blockquote {{
                border-left: 4px solid #D4622A; margin: 1.8em 0; padding: 0.8em 1.2em;
                color: #555; background-color: #fafafa; font-style: italic; border-radius: 0 8px 8px 0;
            }}
            .body-content strong {{ color: #1a1410; font-weight: 600; }}
            .body-content a {{ color: #D4622A; text-decoration: none; font-weight: 500; }}
            .body-content a:hover {{ text-decoration: underline; }}
            .body-content hr {{ border: 0; border-top: 1px solid #eaeaea; margin: 2.5em 0; }}
            .body-content code {{ background-color: #f4f1ed; padding: 2px 6px; border-radius: 4px; font-size: 14px; color: #D4622A; font-family: monospace; }}
            
            .cta-section {{ padding: 10px 50px 40px; text-align: center; }}
            .cta-btn {{
                background-color: #1a1410; color: #ffffff !important; padding: 14px 28px;
                border-radius: 8px; text-decoration: none; font-size: 15px; font-weight: 500;
                display: inline-block;
            }}
            
            .footer {{ text-align: center; margin-top: 24px; padding: 0 20px; }}
            .footer p {{ font-size: 13px; color: #7a6a58; font-style: italic; margin: 0; }}
            
            @media only screen and (max-width: 600px) {{
                .hero, .progress-container, .body-content, .cta-section {{ padding-left: 20px; padding-right: 20px; }}
                .hero h1 {{ font-size: 26px; }}
            }}
        </style>
    </head>
    <body>
        <div class="email-wrapper">
            <div class="email-content">
                <div class="card">
                    <!-- HERO -->
                    <div class="hero">
                        <div class="hero-label">● DAILY KNOWLEDGE RECAP</div>
                        <h1>{title}</h1>
                        <p>{total_days - day_num} lessons remaining</p>
                    </div>

                    <!-- PROGRESS -->
                    <div class="progress-container">
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill"></div>
                        </div>
                        <span class="progress-text">Day {day_num} of {total_days}</span>
                    </div>

                    <!-- BODY -->
                    <div class="body-content">
                        {html_body}
                    </div>

                    <!-- CTA -->
                    <div class="cta-section">
                        <a href="#" class="cta-btn">Mark as Learned ✓</a>
                    </div>
                </div>

                <!-- FOOTER -->
                <div class="footer">
                    <p>"Knowledge is the only asset that grows when shared."</p>
                </div>
            </div>
        </div>
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
