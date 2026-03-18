# syntax=docker/dockerfile:1.7

FROM maven:3.9.11-eclipse-temurin-21 AS build
WORKDIR /app

# Copy only pom first to leverage Docker layer caching for dependencies
COPY pom.xml ./
RUN mvn -B -ntp dependency:go-offline

# Copy source and build
COPY src ./src
RUN mvn -B -ntp clean package -DskipTests

FROM eclipse-temurin:21-jre
WORKDIR /app

# Keep runtime image minimal and predictable
COPY --from=build /app/target/*.jar /app/app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
