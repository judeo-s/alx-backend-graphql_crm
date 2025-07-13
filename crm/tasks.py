from celery import shared_task
import requests
import datetime

@shared_task
def generate_crm_report():
    query = """
    query {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """

    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": query}
        )
        data = response.json()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} - Report: "

        if "errors" in data:
            log_line += f"Error: {data['errors']}\n"
        else:
            report_data = data['data']
            log_line += f"{report_data['totalCustomers']} customers, "
            log_line += f"{report_data['totalOrders']} orders, "
            log_line += f"{report_data['totalRevenue']} revenue\n "

        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(log_line)

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"Error at {datetime.datetime.now()}: {str(e)}\n")
