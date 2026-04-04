import markdown
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()


def markdown_to_html(md_content: str) -> str:
    return markdown.markdown(md_content, extensions=["extra", "codehilite", "tables"])


def _preprocess_markdown(md: str) -> dict:
    """
    Extract structured elements from markdown BEFORE html conversion.
    Returns cleaned markdown + extracted metadata.
    """
    extracted = {
        "day_num": 1,
        "total_days": 30,
        "title": "",
        "hook_headline": "",
    }

    # Extract module banner: ╔══ MODULE 1 OF 30 ══╗
    banner_match = re.search(
        r"╔[═]+╗\s*║\s*MODULE\s+(\d+)\s+OF\s+(\d+)\s*║\s*║\s*(.+?)\s*║\s*╚[═]+╝",
        md,
        re.DOTALL,
    )
    if banner_match:
        extracted["day_num"] = int(banner_match.group(1))
        extracted["total_days"] = int(banner_match.group(2))
        extracted["title"] = banner_match.group(3).strip()
        md = re.sub(
            r"╔[═]+╗\s*║\s*MODULE\s+\d+\s+OF\s+\d+\s*║\s*║\s*.+?\s*║\s*╚[═]+╝",
            "",
            md,
            flags=re.DOTALL,
        ).strip()

    # Extract rocket hook headline
    rocket_match = re.search(r"##\s*🚀\s*(.+)", md)
    if rocket_match:
        extracted["hook_headline"] = rocket_match.group(1).strip()

    # Convert section dividers (━━) to <hr class="section-divider">
    md = re.sub(r"━{8,}", '<hr class="section-divider">', md)

    # Convert "Did you know?" callouts to HTML divs
    md = re.sub(
        r"💡\s*\*\*Did you know\?\*\*\s*(.+)",
        r'<div class="callout fun-fact">'
        r'<div class="callout-icon">💡</div>'
        r'<div class="callout-content">'
        r'<span class="callout-label">Did you know?</span>'
        r'\1'
        r'</div>'
        r'</div>',
        md,
    )

    # Convert "Further Reading" section to HTML div
    # Matches: 📖 **Further Reading:**\n- [Title] — URL\n- [Title] — URL
    def _replace_further_reading(match):
        links_html = match.group(1).strip()
        # Convert each "- [Title] — URL" line to a link item
        lines = links_html.split("\n")
        link_items = ""
        for line in lines:
            line = line.strip()
            if line.startswith("- "):
                line = line[2:]  # Remove "- " prefix
            # Convert markdown links to HTML links
            md_link = re.search(r"\[([^\]]+)\]\s*—\s*(https?://[^\s]+)", line)
            if md_link:
                link_title = md_link.group(1)
                link_url = md_link.group(2)
                link_items += (
                    f'<a href="{link_url}" class="further-link" target="_blank" rel="noopener">'
                    f'<span class="link-title">{link_title}</span>'
                    f'<span class="link-arrow">→</span>'
                    f'</a>'
                )
            else:
                # Fallback: just use the raw text
                link_items += f'<span class="link-item">{line}</span>'

        return (
            f'<div class="callout further-reading">'
            f'<div class="callout-icon">📚</div>'
            f'<div class="callout-content">'
            f'<span class="callout-label">Further Reading</span>'
            f'<div class="link-list">{link_items}</div>'
            f'</div>'
            f'</div>'
        )

    md = re.sub(
        r"📖\s*\*\*Further Reading:\*\*\s*\n((?:- .+\n?)+)",
        _replace_further_reading,
        md,
        flags=re.MULTILINE,
    )

    # Style mission heading
    md = re.sub(
        r"##\s*🎯\s*YOUR MISSION TODAY",
        '<h2 class="mission-heading">🎯 Your Mission Today</h2>',
        md,
    )

    # Style reflection heading
    md = re.sub(
        r"##\s*💭\s*FOOD FOR THOUGHT",
        '<h2 class="reflection-heading">💭 Food for Thought</h2>',
        md,
    )

    return md, extracted


def wrap_email_html(
    title: str,
    html_body: str,
    day_num: int = 1,
    total_days: int = 30,
) -> str:
    progress = int((day_num / total_days) * 100)
    lessons_remaining = total_days - day_num

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin: 0; padding: 0;
                background-color: #f5f0eb;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                -webkit-font-smoothing: antialiased;
                color: #3d3028;
            }}
            .email-wrapper {{ width: 100%; table-layout: fixed; background-color: #f5f0eb; padding-bottom: 40px; }}
            .email-content {{ max-width: 600px; margin: 0 auto; width: 100%; }}
            .card {{
                background-color: #ffffff; border-radius: 16px;
                overflow: hidden; margin-top: 30px;
                box-shadow: 0 2px 24px rgba(60,48,40,0.06);
            }}

            /* ── HERO ── */
            .hero {{
                background: linear-gradient(135deg, #fdf0e6 0%, #f8e4d4 100%);
                padding: 44px 50px 32px;
                text-align: left;
                border-bottom: 1px solid #f0e0d0;
            }}
            .hero-label {{
                font-size: 11px; font-weight: 700; letter-spacing: 2px;
                color: #c47a5a; margin-bottom: 14px; text-transform: uppercase;
            }}
            .hero h1 {{
                font-family: "Georgia", "Times New Roman", serif;
                font-size: 30px; margin: 0; color: #1a1410; line-height: 1.25;
                font-weight: 400;
            }}
            .hero-subtitle {{
                font-size: 15px; color: #8a7560; margin-top: 10px; margin-bottom: 0;
                font-style: italic;
            }}

            /* ── PROGRESS ── */
            .progress-container {{ padding: 20px 50px; border-bottom: 1px solid #f0e0d0; }}
            .progress-bar-bg {{ height: 5px; background-color: #e8ddd4; border-radius: 3px; overflow: hidden; }}
            .progress-bar-fill {{
                width: {progress}%; height: 100%;
                background: linear-gradient(90deg, #c47a5a, #d4926a);
                border-radius: 3px;
            }}
            .progress-text {{
                font-size: 12px; color: #8a7560; margin-top: 8px;
                font-weight: 600; display: block; letter-spacing: 0.5px;
            }}

            /* ── BODY CONTENT ── */
            .body-content {{ padding: 40px 50px; }}
            .body-content h1, .body-content h2, .body-content h3, .body-content h4 {{
                font-family: "Georgia", "Times New Roman", serif;
                color: #1a1410; margin-top: 1.8em; margin-bottom: 0.6em; line-height: 1.35;
            }}
            .body-content h1:first-child, .body-content h2:first-child {{ margin-top: 0; }}
            .body-content h2 {{
                font-size: 22px;
                border-bottom: 2px solid #f0e0d0;
                padding-bottom: 10px;
            }}
            .body-content h3 {{ font-size: 18px; color: #c47a5a; }}
            .body-content p {{
                font-size: 16px; line-height: 1.75; margin-bottom: 1.4em; color: #4a3c30;
            }}
            .body-content ul, .body-content ol {{
                margin-bottom: 1.5em; padding-left: 1.5em;
            }}
            .body-content li {{
                font-size: 16px; line-height: 1.7; margin-bottom: 0.6em; color: #4a3c30;
            }}
            .body-content blockquote {{
                border-left: 4px solid #d4926a; margin: 1.8em 0; padding: 1em 1.4em;
                color: #5a4a3a; background-color: #fdf5ee; font-style: italic;
                border-radius: 0 8px 8px 0;
            }}
            .body-content strong {{ color: #1a1410; font-weight: 600; }}
            .body-content a {{
                color: #c47a5a; text-decoration: none; font-weight: 500;
                border-bottom: 1px solid transparent;
            }}
            .body-content a:hover {{ border-bottom-color: #c47a5a; }}
            .body-content code {{
                background-color: #f5f0eb; padding: 2px 8px; border-radius: 4px;
                font-size: 14px; color: #c47a5a; font-family: "SF Mono", "Fira Code", monospace;
            }}

            /* ── SECTION DIVIDERS ── */
            .section-divider {{
                border: 0; height: 1px; margin: 2.5em 0;
                background: linear-gradient(90deg, transparent, #e8ddd4, transparent);
            }}

            /* ── CALLOUT BOXES ── */
            .callout {{
                border-radius: 10px; padding: 16px 20px;
                margin: 1.5em 0; display: table; width: 100%;
                box-sizing: border-box;
            }}
            .callout-icon {{
                font-size: 20px; display: table-cell; width: 36px;
                vertical-align: top; padding-right: 12px;
            }}
            .callout-content {{
                display: table-cell; vertical-align: middle;
                font-size: 15px; line-height: 1.6;
            }}
            .callout-label {{
                font-weight: 700; display: block; margin-bottom: 4px;
                font-size: 12px; letter-spacing: 1px; text-transform: uppercase;
            }}

            .fun-fact {{
                background-color: #fef9f0; border: 1px solid #f0e0c0;
            }}
            .fun-fact .callout-label {{ color: #b8922a; }}

            .dive-deeper {{
                background-color: #f0f7f4; border: 1px solid #d4e8dc;
            }}
            .dive-deeper .callout-label {{ color: #5a9a7a; }}

            /* ── FURTHER READING ── */
            .further-reading {{
                background-color: #f4f0fa; border: 1px solid #d8c8e8;
            }}
            .further-reading .callout-label {{ color: #7a6a8a; }}
            .link-list {{
                display: flex; flex-direction: column; gap: 8px; margin-top: 6px;
            }}
            .further-link {{
                display: flex; align-items: center; justify-content: space-between;
                padding: 8px 12px; border-radius: 6px;
                background-color: #ffffff; border: 1px solid #e4d8f0;
                text-decoration: none !important; transition: background-color 0.2s;
            }}
            .further-link:hover {{
                background-color: #f8f0ff; border-color: #c8b4e0;
            }}
            .link-title {{
                font-size: 14px; color: #4a3c5a; font-weight: 500;
                text-decoration: none !important;
            }}
            .link-arrow {{
                font-size: 16px; color: #7a6a8a; font-weight: 600;
            }}
            .link-item {{
                font-size: 14px; color: #4a3c5a;
            }}

            /* ── MISSION SECTION ── */
            .mission-heading {{
                color: #5a8a5a !important;
                border-bottom-color: #d4e8dc !important;
            }}

            /* ── REFLECTION SECTION ── */
            .reflection-heading {{
                color: #7a6a8a !important;
                border-bottom-color: #e0d4ec !important;
            }}

            /* ── CTA ── */
            .cta-section {{ padding: 10px 50px 40px; text-align: center; }}
            .cta-btn {{
                background-color: #1a1410; color: #ffffff !important; padding: 14px 32px;
                border-radius: 10px; text-decoration: none; font-size: 15px; font-weight: 500;
                display: inline-block; letter-spacing: 0.3px;
            }}

            /* ── FOOTER ── */
            .footer {{ text-align: center; margin-top: 24px; padding: 0 20px; }}
            .footer p {{
                font-size: 13px; color: #8a7560; font-style: italic; margin: 0;
                letter-spacing: 0.2px;
            }}

            /* ── MOBILE ── */
            @media only screen and (max-width: 600px) {{
                .hero, .progress-container, .body-content, .cta-section {{
                    padding-left: 20px; padding-right: 20px;
                }}
                .hero h1 {{ font-size: 24px; }}
                .card {{ border-radius: 12px; margin-top: 16px; }}
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
                        <p class="hero-subtitle">{lessons_remaining} lessons remaining</p>
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
    app_password = os.getenv("EMAIL_APP_PASSWORD")

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
    # 1. Preprocess markdown: extract banner, convert callouts to HTML
    cleaned_md, extracted = _preprocess_markdown(markdown_content)

    # 2. Convert cleaned markdown → HTML
    html_body = markdown_to_html(cleaned_md)

    # 3. Use extracted metadata or fallback to defaults
    title = extracted["title"] or subject
    day_num = extracted["day_num"]
    total_days = extracted["total_days"]

    # 4. Wrap in beautiful email template
    full_html = wrap_email_html(
        title=title,
        html_body=html_body,
        day_num=day_num,
        total_days=total_days,
    )

    # 5. Send
    send_email(to_email, subject, full_html)
