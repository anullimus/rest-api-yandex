# start by pulling the python image
FROM python:3.10

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# set working directory
WORKDIR .

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . .

# configure the container to run in an executed manner
ENTRYPOINT ["python"]

CMD ["uvicorn", "app.main:app", "--port", "8080"]