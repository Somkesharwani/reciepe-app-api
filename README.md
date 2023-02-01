# reciepe-app-api

To Run this application please follow the bellow points

1. download the code in you local machine
2. For this you required the docker installed, after downloading the code from the project directory open command promopt and run bellow code in cmd :
   Docker-compose build
3. Afte successfully execution of the above command run the below command to strat the project.
   Docker-compose up
4. Now you app is up and running. Now, upon the localhost/8000/admin in your web browser you can see the django admin
5. If you want to access the api open the URL below:
   localhost:8000/api/docs
6. Now, you can see the Swagger interface and from here you need to do below steps:
	a) Create user from the user post api
	b) generate the token for the user
	c) save the token for the user in Authorize tab
	d) Now, you can create recipe using the reciepe api7. 
	

7. To run the testing framework from CLI run below command.
     
	  docker-compose run --rm app sh -c "python manage.py test"

8. To stop the running docker container run bellow command.
      
	  docker-compose down
