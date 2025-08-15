# skeleton fastapi project

## Development Info

### Required envvars
**API_KEY** - serves as a generic pre-shared key. not perfect, but will generally eliminate random calls

### Running Dev Server

1. Generate certs
```sh
mkdir secrets && cd secrets
mkcert localhost 127.0.0.1 ::1
mkcert -install
```
2. Generate keys
```sh
python scripts/generate_secrets.py
```
3. Set config - using dotenv
```sh
touch .env.local
echo "APP_NAME=Development API" >> .env.local
4. Run with uvicorn
```sh
cd src
uvicorn --reload --port 8443 --ssl-keyfile ../secrets/localhost+2-key.pem --ssl-certfile ../secrets/localhost+2.pem app:app
```
