# Welcome to Krzysztof Wróbel's solution

## Endpoint description

Four Endpoint Actions are presented according to task description:
 - **POST** */api/table* - Generate dynamic Django model based on user provided
fields types and titles. The field type can be a string,
number, or Boolean. HINT: you can use Python type
function to generate models on the fly and the schema editor to
make schema changes just like the migrations


 - **PUT** */api/table/:id* - This end point allows the user to update the structure of dynamically generated model.


 - **POST** */api/table/:id/row* - Allows the user to add rows to the dynamically generated model while respecting the model schema


 - **GET** */api/table/:id/rows* - Get all the rows in the dynamically generated model

## Start using

I've attached ***envs*** and ***docker-compose.yml*** (uses Postgres DB) file so it's easy to test it.

Usage:

`source envs`

`docker-compose up --build -d`

First apply migrations: `python manage.py migrate`

Then server can be run by: `python manage.py runserver`

Tests can be run by `python manage.py test`

Backward typing can be implemented to this solution e.g. change text to number when in text there is float number - this wasn't specified in task, so I only stick with serializer validation
