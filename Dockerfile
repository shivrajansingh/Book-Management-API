FROM python:3.9-slim

ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=mydb

RUN apt-get update && apt-get install -y postgresql postgresql-contrib

RUN service postgresql start && \
    su - postgres -c "createuser -s $POSTGRES_USER" && \
    su - postgres -c "createdb -O $POSTGRES_USER $POSTGRES_DB" && \
    su - postgres -c "psql -c \"ALTER USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';\"" && \
    service postgresql stop

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["sh", "-c", "service postgresql start && flask run --host=0.0.0.0"]
