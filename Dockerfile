FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requisitos.txt

EXPOSE 8080

CMD ["streamlit", "run", "pc1.py", "--server.address=0.0.0.0"]
