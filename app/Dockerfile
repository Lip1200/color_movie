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
RUN pip3 install -r requirements.txt

# Copier le reste de l'application
COPY . /app

ARG SQLALCHEMY_DATABASE_URI=mysql+pymysql://movienotes:filipe@db/MovieDb
ENV SQLALCHEMY_DATABASE_URI=$SQLALCHEMY_DATABASE_URI
ARG CHROMADB_URI=localhost:8000
ENV CHROMADB_URI=$CHROMADB_URI
ARG JWT_SECRET_KEY="b'\xc6\x91)\xc3\x00\xeb\x06c:\xdc\xe0\xd6-\x1a7I<\x13aM\xe24l\xe8'"
ENV JWT_SECRET_KEY=$JWT_SECRET_KEY
ARG CHROMADB_STORAGE_DIR=/vec_data
ENV CHROMADB_STORAGE_DIR=$CHROMADB_STORAGE_DIR

# Définir le point d'entrée de l'application
ENTRYPOINT ["python3"]
CMD ["app.py"]
