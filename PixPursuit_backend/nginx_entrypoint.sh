#!/bin/sh

# Check if NEXTAUTH_URL contains "localhost"
if echo "$NEXTAUTH_URL" | grep -q "localhost"; then
    echo "Using nginx.local.conf"
    cp /etc/nginx/conf.d/nginx.local.conf /etc/nginx/conf.d/default.conf
else
    echo "Using nginx.conf"
    cp /etc/nginx/conf.d/nginx.conf /etc/nginx/conf.d/default.conf
fi

nginx -g 'daemon off;'

