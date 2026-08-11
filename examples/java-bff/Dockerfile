FROM maven:3.9.16-eclipse-temurin-21 AS build
WORKDIR /app
COPY . /app
RUN mvn -f java/pom.xml install -DskipTests && mvn -f examples/java-bff/pom.xml package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app
ARG OTEL_JAVA_AGENT_VERSION=2.24.0
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/* \
    && curl --fail --location --output /app/opentelemetry-javaagent.jar "https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v${OTEL_JAVA_AGENT_VERSION}/opentelemetry-javaagent.jar"
COPY --from=build /app/examples/java-bff/target/java-bff-0.0.0-SNAPSHOT.jar app.jar
CMD ["java", "-javaagent:/app/opentelemetry-javaagent.jar", "-jar", "app.jar"]
