FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml requirements.txt README.md ./
COPY backend ./backend
COPY assets ./assets
COPY css ./css
COPY js ./js
COPY *.html ./
RUN pip install --no-cache-dir -e .[api]
EXPOSE 8088
CMD ["python", "-m", "pulsecse", "api", "--host", "0.0.0.0", "--port", "8088"]
