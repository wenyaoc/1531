# Extra Features

## FrontEnd





## Database

We use `postgresql` remote database and deploy on `AWS RDS`.

Using `psycopg2` to connect the database in the code.





## Deployment

We split the `backend` and `frontend` and deploy on `Heroku` respectively.

#### Backend

*   Using `gunicorn` to be our web app

*   Here is my team's `Procfile`

    ```
    web gunicorn --pythonpath src src.server:APP
    ```

*   Here is the link for this app: [https://flockr-grape13-backend.herokuapp.com/]

    **This link cannot be directly be used, it is only the backend, I put this link in our frontend and rebuild a new react frontend application**

    

#### Frontend

*   In frontend, edit `src/utils/constants.js`

    ```javascript
    require("dotenv").config();
    
    export const drawerWidth = 240;
    const port = window.BACKEND_PORT;
    const local = window.LOCAL_ENV || false;
    console.log(local)
    export const url = port === 0 || !local ? "https://flockr-grape13-backend.herokuapp.com" : "http://localhost:" + port;
    
    export const PERMISSION_IDS = {
      OWNER: 1,
      MEMBER: 2
    };
    export const PAGINATION_SIZE = 50;
    export const SLICE_SIZE = 10;
    ```

    



*   deploy on Heroku, here is the link :[https://flockr-grape13.herokuapp.com/]



*   My group also change some UI feature make different  with example.



**This is the app link, click it and register to chat with us**

**https://flockr-grape13.herokuapp.com/**



