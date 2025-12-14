import keyring
import getpass
import time
import os

SERVICE_NAME = "confluence_chatbot"

def show_token_creation_steps():
    print("\n🔧 How to Create a Confluence API Token")
    print("----------------------------------------")
    print("1. Open this link in your browser:")
    print("   https://id.atlassian.com/manage-profile/security/api-tokens\n")
    print("2. Click the button:  Create API token")
    print("3. Give it a label (example: chatbot-access)")
    print("4. Click Create")
    print("5. Copy the generated token")
    print("6. Return here and choose option 1 to enter your email + token\n")
    input("Press Enter to return to the menu...")
    print("\nReturning to setup...\n")
    time.sleep(1)


def prompt_for_credentials():
    """
    Prompts user for email + API token and stores them securely.
    """
    print("\n🔐 Confluence Authentication Setup")
    print("----------------------------------")
    email = input("Enter your Atlassian email: ").strip()
    token = getpass.getpass("Enter your Confluence API token: ").strip()

    keyring.set_password(SERVICE_NAME, "email", email)
    keyring.set_password(SERVICE_NAME, "api_token", token)

    print("\n✅ Credentials saved securely. You won't be asked again.\n")
    return email, token


def get_credentials():
    """
    Returns (email, token). If missing, shows a menu for first-time setup.
    Always returns a tuple.
    """
    email = keyring.get_password(SERVICE_NAME, "email")
    token = keyring.get_password(SERVICE_NAME, "api_token")

    # ✅ If credentials already exist, return them
    if email and token:
        return email, token

    # ✅ First-time setup menu
    while True:
        print("\n🚀 First-Time Confluence Setup")
        print("--------------------------------")
        print("1. Enter my Confluence email + API token")
        print("2. Show me how to create an API token")
        print("3. Exit setup\n")

        choice = input("Choose an option (1/2/3): ").strip()

        if choice == "1":
            return prompt_for_credentials()

        elif choice == "2":
            show_token_creation_steps()

        elif choice == "3":
            print("\nSetup cancelled. Exiting...\n")
            os._exit(0)

        else:
            print("\n❌ Invalid choice. Please try again.\n")
    
def reset_credentials():
    """
    Deletes stored credentials from the OS keychain.
    """
    try:
        keyring.delete_password(SERVICE_NAME, "email")
    except keyring.errors.PasswordDeleteError:
        pass

    try:
        keyring.delete_password(SERVICE_NAME, "api_token")
    except keyring.errors.PasswordDeleteError:
        pass

    print("\n✅ Credentials cleared. You will be asked to enter them again next time.\n")


    # First-time setup menu
    while True:
        print("\n🚀 First-Time Confluence Setup")
        print("--------------------------------")
        print("1. Enter my Confluence email + API token")
        print("2. Show me how to create an API token")
        print("3. Exit setup\n")

        choice = input("Choose an option (1/2/3): ").strip()

        if choice == "1":
            return prompt_for_credentials()

        elif choice == "2":
            show_token_creation_steps()

        elif choice == "3":
            print("\nSetup cancelled. Exiting...\n")
            os._exit(0)

        else:
            print("\n❌ Invalid choice. Please try again.\n")