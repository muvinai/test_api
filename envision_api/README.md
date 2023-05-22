<a href="https://github.com/muvinai/envision_api/actions/workflows/test.yml" target="_blank">
  <img src="https://github.com/muvinai/envision_api/actions/workflows/test.yml/badge.svg" alt="Test">
</a>


# Table of Contents

* [Setup](#setup)
* [Environment Variables](#environment-variables)
* [Tests](#tests)
* [Docs](#docs)

# Setup

First, create a new python environment.

```
$ python3 -m venv venv
$ source ./venv/bin/activate
```

Now install all the requirements.

```
$ pip install -r requirements.txt
```

Finally, run the app.

```
$ uvicorn main:app --reload
```

If during development you add any dependency, remember to run:

```
pip freeze > requirements.txt
```

## Setup with Docker

Build an image:

```bash
docker build -t envision-api
```

Run a docker container:

```bash
docker run -p 8000:8000 envision-api
```

Or use the scripts `build.sh` and `run.sh`.

# Environment Variables

Create the `.env` file in the root folder of the project.\
It must contain the following environment variables.

Development environment:

```
CURRENT_ENVIRONMENT=development
```

Production environment:

```
CURRENT_ENVIRONMENT=production
MONGODB_USER={mongo username}
MONGODB_PASSWD={mongo password}
API_KEY={api key}
AWS_ACCESS_KEY_ID={aws access key id}
AWS_SECRET_ACCESS_KEY={aws secret access key}
REGION_NAME={region name}
THINKIFIC_API_KEY={thinkific api key}
THINKIFIC_SUBDOMAIN={thinkific subdomain}
CMS_API_KEY={cms api key}
CMS_SITE_ID={cms site id}
```

# Tests

For tests and coverage run the following.

```
coverage run -m pytest
coverage report
```

# Docs

To read the interactive docs go to:\
http://127.0.0.1:8000/docs
