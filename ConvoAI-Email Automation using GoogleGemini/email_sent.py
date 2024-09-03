import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def email_send(approved_outputs):
    # Define your email credentials
    sender_email = ""  # Your email address
    password = ""  # Your email password. Allow apps to use the api password in gmailAPIs

    # Define the SMTP server details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Define the list of responses
    reply_emails = approved_outputs
    #connect to the smptp server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, password)

    # Iterate through the reply emails and send responses
    for email in reply_emails:
        sender = email['sender']
        response_email = email['response_email']

        # Extract the email ID from the sender field
        sender_email = sender.split('<')[1].split('>')[0].strip()

        # Create a MIME multipart message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = sender  # Sending response to the email in the 'sender' field
        msg['Subject'] = "Re: Your recent inquiry"

        # Add the response email content
        body = response_email
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server.sendmail(sender_email, sender_email, msg.as_string())

    # Quit the SMTP server
    server.quit()

    print("Response emails sent successfully!")
