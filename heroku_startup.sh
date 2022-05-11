# Start the services in the background
python3 -m uvicorn weatherapi:app --port=8080 &
python3 bot.py &

cat << EOF > /opt/Caddyfile
http://:${PORT} {
    route / {
    	reverse_proxy localhost:8080
    }

    route /bot/* {
    	reverse_proxy localhost:8081
    }
}
EOF

/opt/caddy run -config /opt/Caddyfile
