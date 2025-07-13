import datetime
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    now = datetime.datetime.now()
    timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")
    status = "OK"

    # queries the GraphQL hello field to verify the endpoint is responsive
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"}
        )
        if response.status_code != 200:
            status = "GraphQL DOWN"
    except Exception:
        status = "GraphQL ERROR"

    message = f"{timestamp} CRM is alive\n"

    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message)

def update_low_stock():
    query = """
    mutation {
        updateLowStockProducts {
            success
            updatedProducts {
                name
                stock
            }
        }
    }
    """

    try:
        print("Sending mutation:\n", query)
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        print("Response status:", response.status_code)
        print("Response text:", response.text)

        data = response.json()
        log_path = "/tmp/low_stock_updates_log.txt"
        with open(log_path, "a") as f:
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
            f.write(f"\n[{timestamp}] Low Stock Update:\n")
            if "errors" in data:
                f.write(f"Error: {data['errors']}\n")
            else:
                products = data["data"]["updateLowStockProducts"]["updatedProducts"]
                for p in products:
                    f.write(f" - {p['name']}: new stock = {p['stock']}\n")
    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"\n Error at {datetime.datetime.now()}: {str(e)}\n")
    
