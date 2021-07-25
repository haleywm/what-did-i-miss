FROM python:3.9-buster

WORKDIR /app

# Pass each line in dependencies.txt as an argument to apt-get install, to attempt to install each package
# xargs required as apt-get and apt don't offer file reading functionality
COPY dependencies.txt dependencies.txt
RUN apt-get update && xargs -a dependencies.txt -r apt-get install -y

# Install each required python package in requirements.txt
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy all local files needed for the program to run to the directory
COPY cogs/ fonts/ services/ colormaps.txt default_config.yml main.py stopwords.txt .

# Create a symbolic link to where config should be mounted
RUN ln -s -r config/config.yml config.yml
RUN ln -s -r config/server_variables.db server_variables.db

CMD [ "python", "main.py" ]