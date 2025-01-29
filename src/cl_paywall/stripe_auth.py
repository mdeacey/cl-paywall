import os
import stripe
import urllib.parse
import chainlit as cl

def get_api_key() -> str:
    testing_mode = os.getenv("TESTING_MODE", "False").lower() == "true"
    return os.getenv("STRIPE_API_KEY_TEST") if testing_mode else os.getenv("STRIPE_API_KEY")

async def redirect_button(text: str, customer_email: str, color="#FD504D", payment_provider: str = "stripe"):
    testing_mode = os.getenv("TESTING_MODE", "False").lower() == "true"
    encoded_email = urllib.parse.quote(customer_email)
    
    if payment_provider == "stripe":
        stripe_link = os.getenv("STRIPE_LINK_TEST") if testing_mode else os.getenv("STRIPE_LINK")
        button_url = f"{stripe_link}?prefilled_email={encoded_email}"
    elif payment_provider == "bmac":
        button_url = os.getenv("BMAC_LINK")
    else:
        raise ValueError("payment_provider must be 'stripe' or 'bmac'")
    
    await cl.Message(content=f"[**{text}**]({button_url})", author="system").send()

def is_active_subscriber(email: str) -> bool:
    stripe.api_key = get_api_key()
    customers = stripe.Customer.list(email=email)
    try:
        customer = customers.data[0]
    except IndexError:
        return False
    
    subscriptions = stripe.Subscription.list(customer=customer["id"])
    cl.user_session.set("subscriptions", subscriptions)
    
    return len(subscriptions) > 0
