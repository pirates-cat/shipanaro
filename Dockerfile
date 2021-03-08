FROM python:3.8
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set work directory
WORKDIR /code

# OS-level dependencies (required for LDAP)
RUN apt-get update && apt-get install -y build-essential python3-dev libldap2-dev libsasl2-dev gettext

# Install dependencies
COPY Pipfile Pipfile.lock /code/
RUN pip install pipenv && pipenv install --system
# Copy project
COPY . /code/

CMD [ "./entrypoint.sh" ]
