# SPARCS Email Service

A serverless Email Service built with FastAPI, AWS SQS, and Twilio SendGrid. This service handles the queuing and sending of event-related emails for SPARCS UP Mindanao events.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Clean Architecture](#clean-architecture)
- [Naming Conventions](#naming-conventions)
- [Setup Local Environment](#setup-local-environment)
- [Run Locally](#run-locally)
- [Extra Commands](#extra-commands)
- [Setup AWS CLI](#setup-aws-cli)
- [Setup Serverless Framework](#setup-serverless-framework)
- [Deploy to AWS](#deploy-to-aws)
- [Resources](#resources)

---

## Project Structure

```
SPARCS-Email-Service/
├── constants/                  # Shared constant values used across the application
│   └── common_constants.py
├── model/                      # Data models and schemas
│   ├── email/                  # Email-specific models
│   │   └── email.py
│   ├── registrations/          # Registration-specific models
│   │   └── registration.py
│   └── entities.py             # Shared base entities
├── repository/                 # Data access layer; abstracts all read/write operations
│   ├── email_tracker_repository.py
│   ├── registrations_repository.py
│   └── repository_utils.py
├── resources/                  # AWS resource configurations for Serverless Framework
│   ├── send_email.yml
│   └── sqs.yml
├── scripts/                    # Developer utility scripts for local testing and setup
│   ├── generate-env.py         # Generates the .env file
│   └── send_email_test.py      # Sends a test email for local verification
├── template/                   # HTML email templates for different event types
│   ├── durianPyEmailTemplate.html
│   ├── emailTemplate.html
│   ├── nonDurianPyEmailTemplate.html
│   ├── nonSparcsEmailTemplate.html
│   └── get_template.py         # Helper to retrieve the correct template
├── usecase/                    # Core business logic; orchestrates models, repositories, and services
│   └── email_usecase.py
├── utils/                      # General-purpose helpers and logging utilities
│   ├── logger.py
│   └── utils.py
├── handler.py                  # AWS Lambda entry point
├── main.py                     # FastAPI app entry point for local development
├── serverless.yml              # Serverless Framework configuration
├── ruff.toml                   # Linter configuration (Ruff)
├── Pipfile                     # Python dependency definitions
└── package.json                # Node.js dependency definitions for Serverless plugins
```

---

## Clean Architecture

This project follows **Clean Architecture** principles to keep the codebase modular, testable, and maintainable. Each layer has a single responsibility and dependencies only flow inward — outer layers depend on inner ones, never the reverse.

```
┌─────────────────────────────────┐
│         handler / main          │  ← Entry points (Lambda, FastAPI)
├─────────────────────────────────┤
│            usecase/             │  ← Business logic
├─────────────────────────────────┤
│     repository/  │  template/   │  ← Data access & external services
├─────────────────────────────────┤
│             model/              │  ← Entities & data schemas
└─────────────────────────────────┘
```

| Layer | Folder | Responsibility |
|---|---|---|
| **Entities** | `model/` | Defines the core data structures (email, registration). No dependencies on other layers. |
| **Use Cases** | `usecase/` | Contains the application's business rules. Orchestrates data flow between repositories and models. |
| **Interface Adapters** | `repository/`, `template/` | Translates data between the use case layer and external systems (DynamoDB, SendGrid, HTML templates). |
| **Frameworks & Drivers** | `handler.py`, `main.py`, `resources/` | Entry points and infrastructure config. Connects AWS Lambda/FastAPI to the rest of the application. |

> For more on Clean Architecture, see [The Clean Coder Blog](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).

---

## Naming Conventions

### Python
- **Files & modules:** `snake_case` (e.g., `email_usecase.py`, `repository_utils.py`)
- **Classes:** `PascalCase` (e.g., `EmailUseCase`, `RegistrationRepository`)
- **Functions & variables:** `snake_case` (e.g., `send_email()`, `registration_id`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_COUNT`)

### Folders
- All folder names are lowercase and descriptive of their Clean Architecture layer (e.g., `usecase/`, `repository/`, `model/`)

### AWS Resources
- Resource config files in `resources/` are named after the AWS service they configure (e.g., `sqs.yml`, `send_email.yml`)

### HTML Templates
- Template files use `camelCase` suffixed with `EmailTemplate.html` (e.g., `durianPyEmailTemplate.html`, `nonSparcsEmailTemplate.html`)

---

## Setup Local Environment

1. **Pre-requisites:**
   - Ensure Python 3.8 is installed

2. **Install pipenv:**
   ```shell
   pip install pipenv==2023.4.29 --user
   ```

3. **Install Python dependencies:**
   ```shell
   pipenv install
   ```

4. **Activate virtual environment:**
   ```shell
   pipenv shell
   ```

5. **Add environment variables:**
   - Add the `.env` file provided to you in the root directory
   - To generate the `.env` file from a template, run:
     ```shell
     python scripts/generate-env.py
     ```

---

## Run Locally

> Use this when developing or testing changes before deploying to AWS. The `--reload` flag automatically restarts the server on code changes, so it should only be used in development.

1. **Activate virtual environment:**
   ```shell
   pipenv shell
   ```

2. **Start local server:**
   ```shell
   uvicorn main:app --reload --log-level debug --env-file .env
   ```

   The API will be available at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

---

## Extra Commands

### Send a Test Email
Use this to verify that your SendGrid credentials and email templates are working correctly before deploying.
```shell
python scripts/send_email_test.py
```

### Lint the Codebase
This project uses [Ruff](https://docs.astral.sh/ruff/) for fast Python linting. Run this before committing to catch style and syntax issues.
```shell
ruff check .
```

### Auto-fix Lint Issues
```shell
ruff check . --fix
```

### Check Ruff Configuration
The linter rules are defined in `ruff.toml`. View or edit this file to adjust linting rules:
```shell
cat ruff.toml
```

---

## Setup AWS CLI

> Required before deploying. Only needs to be done once per machine.

1. **Download and install AWS CLI:**
   - [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

2. **Create AWS profile:**
   ```shell
   aws configure --profile sparcs
   ```
   - Input your **AWS Access Key ID** and **AWS Secret Access Key** provided to you
   - Input `ap-southeast-1` for the default region name
   - Leave blank for the default output format

---

## Setup Serverless Framework

> Required before deploying. The Serverless Framework packages and deploys the app to AWS Lambda.

1. **Pre-requisites:**
   - Ensure Node 14 or later is installed

2. **Install Serverless Framework globally:**
   ```shell
   npm install -g serverless
   ```

3. **Install Serverless plugins:**
   ```shell
   npm install
   ```

---

## Deploy to AWS

> Use this when you are ready to ship changes to the `dev` environment on AWS. Ensure your AWS profile is configured and your `.env` variables are up to date before deploying.

```shell
serverless deploy --stage 'dev' --aws-profile 'sparcs' --verbose
```

The `--verbose` flag prints detailed deployment logs, which is useful for debugging failed deployments.

---

## Resources

- [FastAPI](https://fastapi.tiangolo.com/)
- [Serverless Framework Documentation](https://www.serverless.com/framework/docs)
- [Ruff Linter](https://docs.astral.sh/ruff/)
- [Clean Architecture — The Clean Coder Blog](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)