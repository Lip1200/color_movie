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
    && apt-get clean

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

# Définir le point d'entrée de l'application
ENTRYPOINT ["python3"]
CMD ["app.py"]
