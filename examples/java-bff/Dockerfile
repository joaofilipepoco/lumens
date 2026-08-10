FROM maven:3.9.16-eclipse-temurin-21 AS build
WORKDIR /app
COPY . /app
RUN mvn -f java/pom.xml install -DskipTests && mvn -f examples/java-bff/pom.xml package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/examples/java-bff/target/java-bff-0.0.0-SNAPSHOT.jar app.jar
CMD ["java", "-jar", "app.jar"]
