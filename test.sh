#!/bin/bash

BASE_URL="http://localhost:8000"

echo "🧪 Testing endpoints..."
echo ""

echo "1. GET /"
curl -s $BASE_URL/
echo -e "\n"

echo "2. GET /otel-payment/{order_id}"
curl -s $BASE_URL/otel-payment/test-order-123
echo -e "\n"

echo "3. GET /error (may randomly fail)"
curl -s $BASE_URL/error
echo -e "\n"

echo "✅ Done!"
