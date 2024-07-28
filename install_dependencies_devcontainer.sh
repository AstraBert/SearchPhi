apt update
apt install -y docker.io
docker run -d -p 8501:8501 astrabert/searchphi:latest
