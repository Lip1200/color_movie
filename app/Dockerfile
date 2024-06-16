FROM ubuntu:22.04

# Installer les dépendances nécessaires
RUN apt-get update && \
    apt-get install -y \
    mysql-client \
    python3-pip \
    python3-dev \
    libmariadb-dev \
    build-essential \
    liblapack-dev \
    libfreetype6-dev \
    libpng-dev \
    gfortran \
    libopenblas-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Mettre à jour pip et installer numpy
RUN pip3 install --upgrade pip setuptools
RUN pip3 install numpy


# Créer et définir le répertoire de travail
RUN mkdir /app
WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt /app/requirements.txt

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l'application
COPY . /app

ENV SQLALCHEMY_DATABASE_URI=$SQLALCHEMY_DATABASE_URI
ENV CHROMADB_URI=$CHROMADB_URI
ENV JWT_SECRET_KEY=$JWT_SECRET_KEY
ENV CHROMADB_STORAGE_DIR=$CHROMADB_STORAGE_DIR
ENV HOST=$HOST
ENV AUTHORIZED_ORIGIN=$AUTHORIZED_ORIGIN

EXPOSE 5001

# Définir le point d'entrée de l'application
ENTRYPOINT ["python3"]
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"]
