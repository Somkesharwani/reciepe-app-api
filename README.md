# reciepe-app-api

Soon document will be update but for now you can user below command to build and view the app.
</br><b>Note : Docker installation required</b>

open Command promt inside reciepe-app-api folder after checckkin the code.</br>
RUN below command:
<table>
  <tr>
 <td> Docker-compose build</td>
  </tr>
  <tr>
     <td> Docker-compose up</td>
  </tr>
</table>
Now, you can see the URL in the logs if it successfully run.
access the URL like.
</br><b>https//:localhost:8000/api/docs</b></br>

</br>To run the testing framework from CLI run below command.</br>
<b>docker-compose run --rm app sh -c "python manage.py test"</b>

To stop the running docker container run bellow command.</br>
<b> docker-compose down </b>

