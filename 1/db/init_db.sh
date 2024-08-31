docker rm -f mp_db &> /dev/null
docker build -t mp_db .
docker run --name mp_db -e POSTGRES_PASSWORD=pass -p 2345:5432 -d mp_db

echo
echo "URL: postgresql://postgres:pass@localhost:2345/postgres"
