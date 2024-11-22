# Cargo Insurance Application

This application provides an API for calculating cargo insurance costs based on tariffs and allows managing tariffs.
Action logs are saved to the database and sent to Kafka.

## Features

- **Insurance Cost Calculation**: Calculate insurance costs for different cargo types based on active tariffs.
- **Tariff Management**: Create, read, update, and delete tariffs.
- **Bulk Tariff Loading from JSON**: Load multiple tariffs from a JSON structure.
- **Action Logging**: Creation, update, deletions of tariffs, and insurance calculations are first sent to Kafka
  asynchronously and then logged into the database logs.

## Requirements

- **Python 3.10 or higher**
- **Docker and Docker Compose** (for easy deployment)

## Installation and Running

### 1. Clone the Repository

```bash
git clone https://github.com/YuryHaurylenka/insurance_service_test_task
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with the following content(example):

```env
POSTGRES_USER=insurance_user
POSTGRES_PASSWORD=insurance_password
POSTGRES_DB=insurance_db
POSTGRES_HOST=postgres  # The hostname must remain 'postgres' as it is the service name in Docker Compose.
POSTGRES_PORT=5432       # The port must remain 5432 unless you explicitly change it in Docker Compose.
```

### 3. Run the Application with Docker Compose

The application and its dependencies (PostgreSQL and Kafka) can be run using Docker Compose. Use the
provided `docker-compose.yml` file.

#### Start the Services

```bash
docker-compose up -d
```

This command will start the following services:

- **app**: The FastAPI application.
- **postgres**: PostgreSQL database.
- **kafka**: Kafka broker.
- **zookeeper**: Zookeeper service required by Kafka.

### 4. Access the API

API will be available at: [http://localhost:8000](http://localhost:8000)

## Examples of Using the API

### Manage Tariffs

- **Get Tariff List:**

  ```http
  GET /api/v1/tariffs/
  ```

- **Create a New Tariff:**

  ```http
  POST /api/v1/tariffs/
  Content-Type: application/json

  {
    "cargo_type": "Wood",
    "rate": 0.02,
    "valid_from": "2024-12-01",
    "valid_to": "2024-12-31"
  }
  ```

- **Update a Tariff:**

  ```http
  PUT /api/v1/tariffs/{tariff_id}
  Content-Type: application/json

  {
    "rate": 0.025
  }
  ```

- **Delete a Tariff:**

  ```http
  DELETE /api/v1/tariffs/{tariff_id}
  ```

### Calculate Insurance Cost

**Request:**

```http
POST /api/v1/insurance/
Content-Type: application/json

{
  "cargo_type": "Glass",
  "declared_value": 10000.0
}
```

**Response:**

```json
{
  "id": 1,
  "cargo_type": "Glass",
  "declared_value": 10000.0,
  "insurance_cost": 400.0,
  "timestamp": "2024-11-22T12:34:56.789Z",
  "user_id": null,
  "tariff": {
	"id": 5,
	"cargo_type": "Glass",
	"rate": 0.04,
	"valid_from": "2024-11-01",
	"valid_to": "2024-11-30"
  }
}

```

## Dependencies

Key libraries and frameworks used in the project:

- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for database interactions.
- **Alembic**: Tool for managing database migrations.
- **Pydantic**: For data validation and schemas.
- **AIOKafka**: For asynchronous action logging.
