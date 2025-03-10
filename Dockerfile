FROM openjdk:11-jre-slim

# Set environment variables
ENV HOP_VERSION=2.12.0
ENV HOP_HOME=/opt/hop

# Install dependencies and download Apache Hop
RUN apt-get update && apt-get install -y wget unzip \
    && wget https://downloads.apache.org/hop/${HOP_VERSION}/apache-hop-client-${HOP_VERSION}.zip \
    && unzip apache-hop-client-${HOP_VERSION}.zip -d /opt/ \
    && mv /opt/apache-hop-client-${HOP_VERSION} /opt/hop \
    && rm apache-hop-client-${HOP_VERSION}.zip

# Copy Hop workflows and pipelines into the container
COPY hop-workflows /opt/hop/hop-workflows

# Set working directory
WORKDIR /opt/hop

# Expose port
EXPOSE 8080

# Start Hop Server
CMD ["sh", "./hop-server.sh"]
