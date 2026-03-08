import os
import smtplib
from email.message import EmailMessage
from utils.logger import logger

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

def send_email_sync(to_email: str, subject: str, html_content: str):
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning(f"SMTP credentials missing. Mocking email to {to_email}: {subject}")
        # In hackathon mode, if no email is configured, we just print the OTP/Email to logs
        print("====== MOCK EMAIL ======")
        print(f"TO: {to_email}")
        print(f"SUBJECT: {subject}")
        print(f"BODY:\n{html_content}")
        print("========================")
        return True

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = f"TruthLens <{SMTP_USER}>"
        msg['To'] = to_email
        msg.set_content("Please enable HTML to view this email.")
        msg.add_alternative(html_content, subtype='html')

        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
            
        logger.info(f"Email successfully sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def send_otp_email(to_email: str, otp: str):
    subject = "TruthLens - Verify Your Account"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #080c10; color: #e6edf3; padding: 30px; border: 1px solid #00e5ff; border-radius: 8px;">
        <h2 style="color: #00e5ff; text-align: center;">TruthLens Account Verification</h2>
        <p>Your verification code is:</p>
        <div style="text-align: center; margin: 30px 0;">
            <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; background: #161b22; padding: 15px 30px; border-radius: 8px; border: 1px solid #00e5ff;">{otp}</span>
        </div>
        <p>Enter this code in the app to activate your operative account.</p>
        <p style="font-size: 12px; color: #7d8590; text-align: center; margin-top: 40px;">TruthLens © 2026</p>
    </div>
    """
    return send_email_sync(to_email, subject, html)

def send_welcome_email(to_email: str, name: str, user_id: str):
    subject = "Welcome to the Network - TruthLens Operative Kit"
    html = f"""
    <div style="font-family: 'Courier New', Courier, monospace; max-width: 600px; margin: 0 auto; background-color: #050505; color: #00ffcc; padding: 40px; border: 2px solid #00ffcc; border-radius: 12px; box-shadow: 0 0 30px rgba(0, 255, 204, 0.2);">
        <div style="text-align: center; border-bottom: 1px solid #00ffcc; padding-bottom: 20px; margin-bottom: 30px;">
            <h1 style="font-size: 28px; letter-spacing: 5px; margin: 0;">WELCOME TO TRUTHLENS</h1>
            <p style="color: #666; font-size: 10px; margin-top: 5px;">ACCOUNT ACTIVATION SUCCESSFUL</p>
        </div>
        
        <p style="font-size: 14px; color: #fff;">Hello, Operative <strong>{name}</strong>,</p>
        <p style="font-size: 14px; line-height: 1.6;">Your neural node has been successfully integrated into the TruthLens Network. You are now equipped with dual-core AI fact-checking capabilities.</p>
        
        <div style="background: rgba(0, 255, 204, 0.05); padding: 25px; border-radius: 8px; border: 1px dashed #00ffcc; margin: 30px 0;">
            <h3 style="margin-top: 0; font-size: 12px; letter-spacing: 2px;">OPERATIVE IDENTITY KEY:</h3>
            <p style="font-size: 18px; font-weight: bold; color: #fff; margin: 10px 0;">ID: {user_id}</p>
            <p style="font-size: 11px; color: #666; margin-bottom: 0;">* Keep this ID private. It identifies your node in the global synapse.</p>
        </div>
        
        <h3 style="font-size: 12px; letter-spacing: 2px;">YOUR MISSION:</h3>
        <ul style="font-size: 13px; color: #888; padding-left: 20px;">
            <li>Input claims into the Neural Analyzer.</li>
            <li>Receive high-confidence analytical verdicts.</li>
            <li>Expose coordinated misinformation campaigns.</li>
        </ul>
        
        <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #222;">
            <p style="font-size: 12px; color: #444;">TRUTHLENS V2.0 ALPHA | DECODE THE TRUTH</p>
            <p style="font-size: 10px; color: #222;">&copy; 2026 HUMANITY-FIRST AI</p>
        </div>
    </div>
    """
    return send_email_sync(to_email, subject, html)

def send_report_email(to_email: str, claim: str, result_dict: dict):
    subject = f"TruthLens Report: {result_dict.get('verdict', 'Analysis Copy')}"
    score = result_dict.get('score', 0)
    color = "#00ffcc" if score > 70 else "#f7b731" if score > 40 else "#ff3e6c"
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #080c10; color: #e6edf3; padding: 30px; border: 1px solid {color}; border-radius: 8px;">
        <h2 style="color: {color}; text-align: center;">TruthLens Analysis Report</h2>
        <h3 style="color: #7d8590; font-size: 12px; letter-spacing: 2px;">CLAIM ANALYZED:</h3>
        <p style="background: #161b22; padding: 15px; border-radius: 4px; border-left: 3px solid #00ffcc;">"{claim}"</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <p style="font-size: 14px; color: #7d8590; margin: 0;">VERDICT</p>
            <h1 style="color: {color}; margin: 5px 0; font-size: 28px; letter-spacing: 2px;">{result_dict.get('verdict', 'UNKNOWN')}</h1>
            <h2 style="font-size: 48px; margin: 0; color: {color};">{score}/100</h2>
        </div>
        
        <h3 style="color: #7d8590; font-size: 12px; letter-spacing: 2px;">AI SUMMARY:</h3>
        <p style="line-height: 1.6;">{result_dict.get('summary', 'No summary available.')}</p>
        
        <p style="font-size: 12px; color: #7d8590; text-align: center; margin-top: 40px;">TruthLens © 2026 — AI Fact Checking</p>
    </div>
    """
    return send_email_sync(to_email, subject, html)

def send_delete_otp_email(to_email: str, otp: str):
    subject = "ACTION REQUIRED: Account Deletion Request"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #0d0d0d; color: #ffffff; padding: 40px; border: 2px solid #ff0055; border-radius: 12px;">
        <h2 style="color: #ff0055; text-align: center;">Security Alert</h2>
        <p>Warning: You have requested to delete your TruthLens account.</p>
        <div style="text-align: center; margin: 30px 0;">
            <span style="font-size: 42px; font-weight: 800; color: #ff0055; background: #1a1a1a; padding: 15px 40px; border-radius: 10px;">{otp}</span>
        </div>
        <p style="font-size: 12px; color: #666; text-align: center;">Entering this code will permanently erase all data. Irreversible. If not requested by you, change your password immediately.</p>
    </div>
    """
    return send_email_sync(to_email, subject, html)

def send_identity_key_msg(to_email: str, user_id: str):
    subject = "TruthLens - Your Operative Identity Key"
    html = f"""
    <div style="font-family: 'Courier New', Courier, monospace; max-width: 600px; margin: 0 auto; background-color: #050505; color: #00ffcc; padding: 40px; border: 2px solid #00ffcc; border-radius: 12px;">
        <h2 style="text-align: center; letter-spacing: 3px;">IDENTITY RETRIEVAL</h2>
        <p>Your requested Operative Identity Key is provided below:</p>
        <div style="background: rgba(0, 255, 204, 0.05); padding: 25px; border-radius: 8px; border: 1px dashed #00ffcc; margin: 30px 0; text-align: center;">
            <p style="font-size: 16px; font-weight: bold; color: #fff; word-break: break-all;">{user_id}</p>
        </div>
        <p style="font-size: 11px; color: #666; text-align: center;">Use this key for high-clearance actions like account neutralization.</p>
    </div>
    """
    return send_email_sync(to_email, subject, html)

def send_deletion_scheduled_email(to_email: str):
    subject = "TruthLens - Account Neutralization Scheduled"
    html = f"""
    <div style="font-family: 'Courier New', Courier, monospace; max-width: 600px; margin: 0 auto; background-color: #050505; color: #ff0055; padding: 40px; border: 2px solid #ff0055; border-radius: 12px;">
        <h2 style="text-align: center; letter-spacing: 3px;">NEUTRALIZATION PENDING</h2>
        <p style="color: #fff;">Protocol initiated: Your TruthLens account is scheduled for permanent deletion in <strong>48 hours</strong>.</p>
        
        <div style="background: rgba(255, 0, 85, 0.05); padding: 25px; border-radius: 8px; border: 1px dashed #ff0055; margin: 30px 0;">
            <p style="font-size: 13px; color: #fff;">If this was a mistake, you can <strong>CANCEL</strong> this process from your Profile dashboard within the next 48 hours.</p>
        </div>
        
        <p style="font-size: 11px; color: #666; text-align: center;">After 48 hours, all your analyses and identity data will be permanently purged from the neural network.</p>
    </div>
    """
    return send_email_sync(to_email, subject, html)

def send_deletion_cancelled_email(to_email: str):
    subject = "TruthLens - Neutralization Terminated"
    html = f"""
    <div style="font-family: 'Courier New', Courier, monospace; max-width: 600px; margin: 0 auto; background-color: #050505; color: #00ffcc; padding: 40px; border: 2px solid #00ffcc; border-radius: 12px;">
        <h2 style="text-align: center; letter-spacing: 3px;">RECOVERY SUCCESSFUL</h2>
        <p style="color: #fff;">Operative, your account neutralization request has been <strong>TERMINATED</strong>.</p>
        <p>Your node remains active in the network. No data was purged.</p>
        <p style="font-size: 11px; color: #666; text-align: center;">Welcome back to the synapse.</p>
    </div>
    """
    return send_email_sync(to_email, subject, html)
