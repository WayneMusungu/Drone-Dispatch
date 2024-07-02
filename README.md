# Drone Management Service via REST API

This Django project implements a REST API service for managing a fleet of drones and their interactions with medications. The service allows clients to communicate with drones through various endpoints provided by the dispatch controller.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Server](#running-the-server)
  - [Database](#database)
- [Endpoints](#endpoints)
- [Testing](#testing)
- [Docker Instructions](#docker-instructions)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This project manages a fleet of **10 drones** designed to deliver small loads, specifically medications. Each drone is equipped with specific attributes such as serial number, model, weight limit, battery capacity, and state. Medications are characterized by name, weight, code, and an image of the medication case.

The API provides functionalities to register drones, load medications onto drones, check loaded medications, monitor available drones for loading medications, and check drone battery levels.

## Features

- **Drone Registration**: Register new drones with their specifications.
- **Medication Loading**: Load medications onto drones while enforcing weight limits and battery conditions.
- **Medication Check**: Retrieve a list of medications loaded on a specific drone.
- **Available Drones**: Retrieve a list of drones available for loading medications.
- **Battery Level Check**: Check the current battery level of a specific drone.
- **Periodic Battery Audits**: Automatically monitor and log battery levels at regular intervals.

## Setup Instructions

### Prerequisites

Ensure you have the following installed on your system:
- Docker
- Docker Compose
- Python (for local development and management)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/WayneMusungu/Drone-Dispatch.git
   cd Drone-Dispatch
   ```

2. Stopping Existing Redis Service (if running):
   ```bash
   sudo service redis-server stop
   ```

### Running the Server

Start the Django development server using Docker:
   ```bash
   docker-compose up --build
   ```

This command will:
- Apply database migrations
- Load initial data
- Start the Django development server

The server should now be running locally at `http://127.0.0.1:8000/`.

### Database

The project uses different databases for different environments:
- **Local development**: SQLite3 (default Django configuration)
- **Docker setup**: PostgreSQL

## Endpoints

The following endpoints are available:

- **Register a Drone**:
  - `POST http://127.0.0.1:8000/drone/register/`
  
    Payload Example:
    ```json
    {
      "serial_number": "DRN001",
      "model": "LIGHTWEIGHT",  // Choices: LIGHTWEIGHT, MIDDLEWEIGHT, CRUISERWEIGHT, HEAVYWEIGHT
      "weight_limit": 500,
      "battery_capacity": 100
    }
    ```

- **Load Medications onto a Drone**:
  - `POST http://127.0.0.1:8000/drone/<int:id>/load/`
  
    To load medications onto a drone, use Postman with the following steps:
    
    1. Set the request type to `POST`.
    2. Set the URL to `http://127.0.0.1:8000/drone/1/load/`. (where `1` is the ID of the drone)
    3. Go to the `Body` tab, select `form-data`.
    4. Add the following fields:
       - `name`: Name of the medication.
       - `weight`: Weight of the medication in grams.
       - `code`: Code representing the medication.
       - `image`: Upload a file (medication image).
       
       Example:
       - `name`: Medication A
       - `weight`: 50
       - `code`: MEDA001
       - `image`: Select a file to upload (medication image).

- **Check Loaded Medications for a Drone**:
  - `GET http://127.0.0.1:8000/drone/<int:id>/medications/`
  
    Example:
    - `GET http://127.0.0.1:8000/drone/1/medications/` (where `1` is the ID of the drone)

- **Check Available Drones for Loading**:
  - `GET http://127.0.0.1:8000/drone/available-drones/`

- **Check Drone Battery Level**:
  - `GET http://127.0.0.1:8000/drone/<int:id>/battery/`
  
    Example:
    - `GET http://127.0.0.1:8000/drone/1/battery/` (where `1` is the ID of the drone)

- **Drone Battery Audit Log**:
  - `GET http://127.0.0.1:8000/drone-audit/`

## Testing

Run unit tests to verify functionality within the Docker container:
   ```bash
   docker-compose run web python manage.py test
   ```

## Docker Instructions

### Checking Logs

- **Check periodic task logs**:
  ```bash
  docker-compose logs celery_beat
  ```

- **Check worker logs**:
  ```bash
  docker-compose logs celery_worker
  ```