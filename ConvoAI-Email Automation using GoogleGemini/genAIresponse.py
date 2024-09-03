def responses(unread_emails):
    responses_dict = {}
    for email in unread_emails:
        sender = email['sender']
        message = email['message']
        # Generate response
        #response = f"Dear {sender},\n\nThank you for your message:\n\n{message}\n\nBest regards,\n[Your Name]"
        response = f"Dear {sender},\n\nThank you for your message and Best regards,\n[by contactcenter]"
        # Append response to responses_dict
        if sender in responses_dict:
            responses_dict[sender].append(response)
        else:
            responses_dict[sender] = [response]
    return responses_dict
