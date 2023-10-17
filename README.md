# SPARCS Email Service

A serverless Email Service with SQS and Twillio SendGrid

## Setup Local Environment

1. **Pre-requisites:**
   - Ensure Python 3.8 is installed

2. **Install pipenv:**
   ```shell
   pip install pipenv==2023.4.29 --user
   ```

3. **Install Python Dependencies:**
   ```shell
   pipenv install
   ```

4. **Activate Virtual Environment:**
   ```shell
   pipenv shell
   ```

5. **Add Environment Variables:**
    -  Add the `.env` file provided to you in the `backend` directory

## Run Locally

1. **Activate Virtual Environment:**
   ```shell
   pipenv shell
   ```

2. **Start Local Server:**
   ```shell
   uvicorn main:app --reload --log-level debug --env-file .env
   ```

## Setup AWS CLI

1. **Download and Install AWS CLI:**
   - [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

2. **Create AWS Profile:**
   ```shell
   aws configure --profile sparcs
   ```

   - **Input your AWS Access Key ID and AWS Secret Access Key provided to you.**
   - **Input `ap-southeast-1` for the default region name.**
   - **Leave blank for the default output format.**


## Setup Serverless Framework

1. **Pre-requisites:**
   - Ensure `Node 14` or later is installed

2. **Install serverless framework:**
   ```shell
   npm install -g serverless
   ```

3. **Install serverless plugins:**
   ```shell
   npm install
   ```

## Deploy to AWS
   ```shell
   serverless deploy --stage 'dev' --aws-profile 'sparcs' --verbose
   ```

## Resources

- [FastAPI](https://fastapi.tiangolo.com/)
- [Serverless Framework Documentation](https://www.serverless.com/framework/docs)
- [Clean Coder Blog](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
