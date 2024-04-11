# yk-aws-application

This is a Django project created for demonstrating the implementation of shadow analysis.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and deployment purposes.

### Prerequisites

What things you need to install the software and how to install them:

- Python (version 3.8)

### Installing

A step by step series of examples that tell you how to get a development env running:

1. Download the repository as ZIP
2. Move to the application directory.
3. Install ipykernel by the following command:
               ```
               <pip install ipykernel>
               ```
      			OR
             ```
      			<conda install -c anaconda ipykernel>
               ```
5. Create conda virtual environment
               ```
               <conda create -n awsapplication python=3.8.5>
               ```
6. Activate the conda virtual environment
              ```
              <conda activate awsapplication>
              ```
7. Install Jupyter Notebook
              ```
               <pip install notebook>
               ```
8. Update Kernel into Jupyter Notebook             
               ```
               <python -m ipykernel install --user --name awsapplication --display-name awsapplication>
               ```
9. Install the dependencies 

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

10. Apply the migrations
   python manage.py makemigrations
   python manage.py migrate

11. Start the development server
   python manage.py runserver

12. Visit `http://localhost:8000` in your browser to view the project.





