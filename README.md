# Django Rest Framework and Stripe Integration

This Django project integrates with the Stripe API to handle payment-related functionalities using Django Rest Framework.

## Getting Started

### Prerequisites

- Python 3.10
- Docker (optional, for running the project with Docker)
- Rename `.env.example` to `.env` and configure your environment variables.
- Install project dependencies using the provided `requirements.txt` file.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/varlamzhordania/lazariuskriss.git
   ```
2. Change into the project directory:

   ```bash
   cd lazariuskriss
   ```
   
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
   
4. Rename .env.example to .env and configure your environment variables.

### Usage
#### Running with Docker Compose

Ensure Docker is installed on your system.

1. Build and run the project using Docker Compose:

   ```bash
   docker-compose up --build
   ```
    Access the Django Rest Framework API at http://127.0.0.1:8000/.

#### Running without Docker

1. Run the development server:

   ```bash
   python manage.py runserver
   ```
    Access the Django Rest Framework API at http://127.0.0.1:8000/.

