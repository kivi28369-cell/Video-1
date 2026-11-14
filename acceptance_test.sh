#!/bin/sh
cd "$(dirname "$0")/.."
if grep -rniE "admob|adsense|subscribe|upgrade|premium|paywall|stripe|razorpay" backend web capacitor.config.json; then echo "FAIL"; exit 1; else echo "PASS: no ads/payment terms"; fi
