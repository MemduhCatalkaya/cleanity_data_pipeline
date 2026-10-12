
import requests


BASE_URL = "http://127.0.0.1:8000"
API_TIMEOUT = 30


def get_products():
    response = requests.get(
        f"{BASE_URL}/products",
        timeout=API_TIMEOUT
    )

    response.raise_for_status()

    return response.json()


def get_customers(after_id):
    response = requests.get(
        f"{BASE_URL}/customers",
        params={"after_id": after_id},
        timeout=API_TIMEOUT
    )

    response.raise_for_status()

    return response.json()


def get_orders(after_id):
    response = requests.get(
        f"{BASE_URL}/orders",
        params={"after_id": after_id},
        timeout=API_TIMEOUT
    )

    response.raise_for_status()

    return response.json()
