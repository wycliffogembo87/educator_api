**Educator API**

***Technologies used***

1. Python3
2. Starlette/Fastapi (https://fastapi.tiangolo.com/)
3. Postgresql
4. PonyORM (https://docs.ponyorm.org/toc.html)
5. Dbmate

***How to setup and run the project in on your local machine***

1. Install and setup dbmate (for data migrations).

        URL: https://github.com/amacneil/dbmate

1. Create a python3 virtual environment and activate it.

        https://docs.python.org/3/tutorial/venv.html

2. Clone the project repo.
    
        git clone git@github.com:wycliffogembo87/educator_api.git
    
3. Install python packages.

        cd <PROJECT ROOR DIRECTORY>
        pip install -r requirements.txt

4. Setup your postgresql database.

        creatdb <Databae Name>
        cp sample_dot_env .env

5. Also configure other parameters in the .env file

        - SMS API Parameters
        - Secret key

6. Run migrations.

        dbmate up

7. Populate your database with test accounts and other necesary data.

        python seed.py

8. Start the service

            uvicorn main:app  --reload


***Interactive swagger/openapi spec/doc***

        http://127.0.0.1:8000/docs


***API authentication and authorization***

        - The api uses http basic auth for authentication.
        - It uses a simple role based whitelist for authorization.
        - When you populate your database with test data, the following account will be inserted which you can use to test with.


        Authentication (Accounts)

                1. Username: tutor, Password: tutor123
                2. Username: learner, Password: learner123
                3. Username: staff, Password: staff123
                4. Username: admin, Password: admin123
        

        Authorization

                upload_file allows [Role.tutor] only
                create_exam allows [Role.tutor] only
                add_participant allows [Role.tutor] only
                create_question allows [Role.tutor] only 
                create_submission [Role.learner] only
                mark_submission [Role.tutor] only
                get_exam_performance [Role.tutor] only
                notify_user [Role.tutor, Role.staff, Role.admin] only
                request_form_mentorship [Role.learner] only


**To be done**
- [ ] Add timer endpoint
- [ ] Add PATCH, UPDATE, and GET
- [ ] Write test case