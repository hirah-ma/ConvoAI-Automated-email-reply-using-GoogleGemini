import os.path
import time
from email_sent import *
from genAIresponse import *
from gemini import *
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

unread_emails = []
# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
    """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        # results = service.users().labels().list(userId="me").execute()
        # labels = results.get("labels", [])

        results = service.users().messages().list(userId="me", labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])
        if not messages:
            print("You have no new messages.")
        else:

            message_count = 0
            for message in messages:
                msg = service.users().messages().get(userId="me", id=message['id']).execute()
                message_count = message_count + 1

            print("You have " + str(message_count) + " unread message")
            new_message_choice = input("Would you like to see your messages?").lower()
            if new_message_choice == "yes" or "y" or "Y" or "YES":
                for message in messages:

                    msg = service.users().messages().get(userId="me", id=message['id']).execute()
                    email_data = msg['payload']['headers']
                    for values in email_data:
                        name = values["name"]
                        if name == "From":
                            from_name = values["value"]

                            print("You have a new message from: "+ from_name)
                            print("       "+ msg["snippet"]+"...")
                            print("\n")
                            unread_emails.append({'sender': from_name, 'message': msg["snippet"]})

                            time.sleep(1)










    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

    ##passing unread
    emails = unread_emails
    # print(responses(unread_emails))
    numof_emails = len(emails)
    sender_reslist = []  # it has{sender: emailid, response_email': gen_res
    for email in emails:
        sender = email['sender']
        message = email['message']
        # Assuming sender's email ID is extracted from the 'sender' field
        # You may need to further process 'sender' to extract the email ID
        email_id: str = sender.split('<')[1].split('>')[0].strip() if '<' in sender else sender
        # Pass email ID and message to the function h
        gen_res = generated_response(message, email_id)
        print(gen_res)
        # print("select the responses which u want to sent")
        sender_response = {'sender': sender, 'response_email': gen_res}
        print(sender_response)
        sender_reslist.append(sender_response)

        # Append the dictionary to the list
        # .append(sender_response)
    print(numof_emails)
    print(len(sender_reslist))
    print(sender_reslist)
    disappproved_outputs = []

    def approve_outputs(numof_emails, sender_reslist):
        approved_outputs = []

        for i in range(numof_emails):
            print("Output " + str(i) + ":")
            while True:
                choice = input("Approve this output to ?"+sender_reslist[i]['sender'] +" (yes/no): " ).lower()
                if choice in ["yes", "no"]:
                    break
                else:
                    print("Invalid choice. Please enter 'yes' or 'no'.")

            if choice == "yes":
                approved_outputs.append(sender_reslist[i])
            else :
                disappproved_outputs.append(sender_reslist[i])

        return approved_outputs



    approve_out_send=approve_outputs(numof_emails, sender_reslist)
    print(approve_out_send)
    print(disappproved_outputs)
    print(emails)
    #new_list = [{'sender': d1['sender'], 'response_email': d2['response_email']} for d1 in list1 for d2 in list2 if
               # d1['sender'].split('<')[-1].strip('>') == d2['sender'].split('<')[-1].strip('>')]
    new_list = [{'sender': d1['sender'], 'message': d2['message']} for d1 in disappproved_outputs for d2 in emails if
                d1['sender'] == d2['sender']]
    print(new_list)
    if (input("so you want to send email?")=="y"):
        email_send(approve_out_send)
    if(input("do you want to regenerate responses for the disapproved outputs?")=="y"):
        for email, email2 in zip(new_list, disappproved_outputs):
            sender = email['sender']
            message = email['message']
            prev_res = email2['response_email']
            # Assuming sender's email ID is extracted from the 'sender' field
            # You may need to further process 'sender' to extract the email ID
            email_id: str = sender.split('<')[1].split('>')[0].strip() if '<' in sender else sender
            # Pass email ID and message to the function h
            regen_res = regenerate_response(message, email_id, prev_res)
            print(regen_res)





if __name__ == "__main__":
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
