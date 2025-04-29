from services.fetch_emails import get_gmail_service

if __name__ == "__main__":
    """
    Perform Gmail authorization by obtaining a service instance.
    """
    service = get_gmail_service()
    print("Gmail authorization completed successfully.")
