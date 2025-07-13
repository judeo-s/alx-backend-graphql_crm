import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

log_path = "/tmp/order_reminders_log.txt"

transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

query = gql(
    """
    query {
        allOrders(orderDate_Gte: "%s") {
            edges {
                node {
                    id
                    customer {
                        email
                    }
                }
            }
        }
    }
    """ % (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
)

result = client.execute(query)

with open(log_path, "a") as f:
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for edge in result["allOrders"]["edges"]:
        order = edge["node"]
        f.write(f"{now} - Order ID: {order['id']}, Customer Email: {order['customer']['email']}\n")

print("Order reminders processed!")