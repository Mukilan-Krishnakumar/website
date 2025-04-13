#!/bin/sh

# Create self-signed certificate for initial startup if needed
if [ ! -f "/etc/letsencrypt/live/mukilank.com/fullchain.pem" ]; then
    echo "No SSL certificate found. Creating temporary self-signed certificate..."
    mkdir -p /etc/letsencrypt/live/mukilank.com
    
    # Generate a self-signed certificate
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
        -keyout /etc/letsencrypt/live/mukilank.com/privkey.pem \
        -out /etc/letsencrypt/live/mukilank.com/fullchain.pem \
        -subj '/CN=mukilank.com'
    
    # Create chain.pem (not strictly necessary but prevents warnings)
    cp /etc/letsencrypt/live/mukilank.com/fullchain.pem /etc/letsencrypt/live/mukilank.com/chain.pem
    
    echo "Temporary self-signed certificate created."
fi

# Start Nginx in the foreground and reload it periodically to pick up new certificates
echo "Starting Nginx..."
while :; do 
    sleep 6h & wait ${!}
    echo "Reloading Nginx configuration..."
    nginx -s reload
done & nginx -g "daemon off;"