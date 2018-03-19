# Use an official Python runtime as a parent image
FROM python:3

LABEL   maintainer  =   "e043120@dac.unicamp.br"
LABEL   Description =   "Docker image for the PrivaaaS"
LABEL   Vendor      =   "UNICAMP & UC"
LABEL   Version     =   "1.0"

# Install Java
ENV JAVA_HOME       /usr/lib/jvm/java-8-oracle

## Install Oracle's JDK
RUN echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | debconf-set-selections
RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" > /etc/apt/sources.list.d/webupd8team-java-trusty.list
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886
RUN apt-get update && \
  apt-get install -y --no-install-recommends oracle-java8-installer && \
  apt-get clean all

COPY /PrivaaaS/requirements.txt ./
COPY /PrivaaaS/run.py ./
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /PrivaaaS
ADD . /PrivaaaS

# Set the working directory to /PrivaaaS
ENV HOME /PrivaaaS
WORKDIR /PrivaaaS

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run run.py when the container launches -- Externally Visible Server
CMD ["python", "run.py", "runserver", "--host=0.0.0.0"]
