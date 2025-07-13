#!/bin/bash

# Get current working directory (cwd)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/../.."

# Activate virtual environment if needed
# source venv/bin/activate

LOG_FILE="/tmp/customer_cleanup_log.txt"
NOW=$(date +"%Y-%m-%d %H:%M:%S")

# Run Django shell command
COUNT=$(python manage.py shell << END
from crm.models import Customer, Order
from datetime import timedelta
from django.utils import timezone
a_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.exclude(order__order_date__gte=a_year_ago)
deleted_count = inactive_customers.count()
inactive_customers.delete()
print(deleted_count)
END
)

if [ "$COUNT" -gt 0 ]; then
    echo "$NOW - Deleted $COUNT inactive customers" >> "$LOG_FILE"
else
    echo "$NOW - No inactive customers found" >> "$LOG_FILE"
fi