# Default target for model microservices
.PHONY: model-microservice-all
model-microservice-all: model-microservice-build model-microservice-run

# Build the Docker image
.PHONY: model-microservice-build
model-microservice-build:
	cd model-microservice && docker build -t model-microservice .

# Run the Docker container
.PHONY: model-microservice-run
model-microservice-run:
	docker run -p 5000:5000 model-microservice

# Stop the Docker container
.PHONY: model-microservice-stop
model-microservice-stop:
	docker stop model-microservice
	docker rm model-microservice

# Remove the Docker image
.PHONY: model-microservice-clean
model-microservice-clean: model-microservice-stop
	docker rmi model-microservice

















# Default target for database operations
.PHONY: database-up-create
database-up-create:
	cd database && docker-compose up -d
	until docker exec postgres-container pg_isready -U myuser; do \
		echo "Waiting for PostgreSQL to be ready..."; \
		sleep 2; \
	done
	docker exec -i postgres-container psql -U myuser -d mydatabase < ./backend/delete.sql
	docker exec -i postgres-container psql -U myuser -d mydatabase < ./backend/schema.sql


# Start the database container
.PHONY: database-up
database-up:
	cd database && docker-compose up -d

# Create the database schema
.PHONY: database-create
database-create:
	docker exec -i postgres-container psql -U myuser -d mydatabase < ./backend/schema.sql

# Stop the database container
.PHONY: database-down
database-down:
	docker stop postgres-container
	docker rm postgres-container
















# Default target for backend operations
.PHONY: backend-all
backend-all: backend-build backend-run

# Build the Docker image
.PHONY: backend-build
backend-build:
	cd backend && docker build -t backend .

# Run the Docker container
.PHONY: backend-run
backend-run:
	docker run -p 8000:8000 backend

# Stop the Docker container
.PHONY: backend-stop
backend-stop:
	docker stop backend
	docker rm backend

# Remove the Docker image
.PHONY: backend-clean
backend-clean: backend-stop
	docker rmi backend









# Default target for frontend
.PHONY: frontend-all
frontend-all: frontend-build frontend-run

# Build the Docker image
.PHONY: frontend-build
frontend-build:
	cd frontend && docker build -t frontend .

# Run the Docker container
.PHONY: frontend-run
frontend-run:
	docker run -p 3000:3000 frontend

# Stop the Docker container
.PHONY: frontend-stop
frontend-stop:
	docker stop frontend
	docker rm frontend

# Remove the Docker image
.PHONY: frontend-clean
frontend-clean: frontend-stop
	docker rmi frontend
