# Étape 1 : Builder
FROM ubuntu:22.04 AS builder

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

# Étape 2 : Image finale basée sur scratch
FROM scratch

# Copier Python et les bibliothèques nécessaires depuis l'étape de construction
COPY --from=builder /usr/bin/python3 /usr/bin/python3
COPY --from=builder /usr/lib /usr/lib
COPY --from=builder /lib /lib
COPY --from=builder /usr/local/lib/python3.10 /usr/local/lib/python3.10

# Copier l'application Flask
COPY --from=builder /app /app

# Définir le répertoire de travail
WORKDIR /app

# Définir le point d'entrée de l'application
ENTRYPOINT ["/usr/bin/python3"]
CMD ["app.py"]

