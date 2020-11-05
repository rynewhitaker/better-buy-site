# better-buy-site

This is a project created by Ryne, Collin, Noah, Ryan, and Jafett for Systems Analysis and Design.

## How to run

Install [Python 3.7](https://www.python.org/downloads/release/python-379/) and [Node.js](https://nodejs.org/en/download/)

Install some python applications:

        pip install --user pipenv autopep8

Clone this repo:

        git clone https://github.com/rynewhitaker/better-buy-site.git

Navigate to the project's folder and install missing dependencies:

        cd better-buy-site
        pipenv install
        npm install

Start the virtual environment shell:

        pipenv shell

Run the local server:

        python manage.py runserver

Navigate to http://localhost:8000/ in your browser

## How to use (CMD Prompt)

Open Site:

        cd better-buy-site
        pipenv shell  (ctrl-c or exit() to exit)
        python manage.py runserver
                
Upload Changes:

        git add .
        git commit -m "message" (add message)
        git push
                
Change Branch:

        git checkout branch (branch is name of branch)
                
