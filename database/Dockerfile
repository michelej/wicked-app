FROM mongo:7.0

# Copiar el script de inicialización
COPY init-mongo.js /docker-entrypoint-initdb.d/init-mongo.js

# Establecer variables de entorno por defecto
ENV MONGO_INITDB_DATABASE=wicked_db

EXPOSE 27017
