# yk-aws-application

This is a Django project created for demonstrating the implementation of shadow analysis.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and deployment purposes.

### Prerequisites

What things you need to install the software and how to install them:

- Python (version 3.8)

### Installing

A step by step series of examples that tell you how to get a development env running:

1. Clone this repository:

   git clone https://github.com/Aarthi1508/yk-aws-application.git

2. Install the dependencies 

   pip install webapp/requirements.txt
   
   The `requirements.txt` file should contain the following packages:
   
   django==3.2
   
   numpy==1.21.2
   
   pvlib==0.8.0
   
   mapbox==0.18.0
   
   matplotlib==3.4.3
   
   pymongo[srv]==4.0.1
   
   rasterio
   
   plotly==5.3.1
   
   python-dotenv==0.19.2
   
   django-cors-headers==3.8.0
   
   pandas==1.3.3
   
   scipy==1.7.3

3. Apply the migrations
   python manage.py makemigrations
   python manage.py migrate

4. Start the development server
   python manage.py runserver

5. Visit `http://localhost:8000` in your browser to view the project.





