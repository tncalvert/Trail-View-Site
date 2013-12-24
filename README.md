##TrailView

The TrailView website is a project completed by an IQP group from Worcester Polytechnic Institute during June - August 2013.

It was created for the National Park Service at Acadia National Park.

This is a rewrite, written in Python/Django. The original version was written in ASP.NET MVC 4 (C#). It can be found in an SVN Google Code repository [here](http://code.google.com/p/wpitrailview/).

##Setup

The project can be run with any install of Django 1.4 (possibly others, but it hasn't been checked). To do so, you'll need a PostgreSQL database (which must be set up in the settings files). The User and Password for the database are defined in a file .pg_pwd that sits in the same directory as settings.py and includes only
the username and the password on two lines.

To setup the database, run the functions in Setup/setup.py with the files provided inside the same folder. It should be fairly self explanatory.

After that, it can be run like any Django program.

However, the photos required for the project are not included in the repository, and are not available outside of WPI IQP groups and the NPS. As a result, you can see all the info we collected, but you cannot actually see the images (which is obviously disappointing, but there isn't much that can be done. There are a lot of images, and they really aren't mine to give out).
