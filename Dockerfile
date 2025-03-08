FROM openjdk:11-jre-slim

ENV HOP_VERSION=2.7.0
ENV HOP_HOME=/opt/hop

RUN apt-get update && apt-get install -y wget unzip \
    && wget https://downloads.apache.org/hop/${HOP_VERSION}/apache-hop-client-${HOP_VERSION}.zip \
    && unzip apache-hop-client-${HOP_VERSION}.zip -d /opt/ \
    && mv /opt/apache-hop-client-${HOP_VERSION} /opt/hop \
    && rm apache-hop-client-${HOP_VERSION}.zip

WORKDIR /opt/hop

EXPOSE 8080

CMD ["sh", "./hop-server.sh"]
