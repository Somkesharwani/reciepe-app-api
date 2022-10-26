# reciepe-app-api

Soon document will be update but for now you can user below command to build and view the app.
Note : Docker installation required

open Command promt inside reciepe-app-api folder after checckkin the code.

RUN below command:
Docker-compose build
Docker-compose up

Now, you can see the URL in the logs if it successfully run.
access the URL like.
https//:localhost:8000/api/docs

To run the testing framework from CLI run below command.
docker-compose run --rm app sh -c "python manage.py test"
