# SMS-DEV-BACKEND

## Naming convention for our project

**Model:** Each model must be named in the PascalCase.

example: **StudentGuardian**

**Serializer:** Each serializer must be named in the PascalCase with the suffix Serializer at the end

example: **StudentGuardianSerializer**

**View:** Each view must be named in the PascalCase with the suffix View at the end

example: **StudentGuardianView**

**URL:** Each url must be named in all lower-case separated by "-" and must be in plural for get all and post api and in singular for put and delete. Also, must have the first letter of the app name the urls belongs to right after the domain for example "s" for the students app.

example:

plural for get all and post - [http://127.0.0.1:8000/d/classroom-types](http://127.0.0.1:8000/d/classroom-types/)/

singular for update and delete - [http://127.0.0.1:8000/d/classroom-type/](http://127.0.0.1:8000/d/classroom-types/)id
