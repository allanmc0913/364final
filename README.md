# Introduction
Hi there, this is my SI364 Final Project Assignment.  In a nutshell, it allows students to search tweets based on a hashtag they enter in using Twitter's Search API.  It also allows users to log in and create their own personalized tweet collections and view past tweets from all users.  I've also deployed this application to Heroku -> http://si364finalproject-allanmc.herokuapp.com
 
# Code Checklist:
 
 **1.  Ensure that your SI364final.py file has all the setup (app.config values, import statements, code to run the app if that file is run, etc) necessary to run the Flask application, and the application runs correctly on http://localhost:5000 (and the other routes you set up). Your main file must be called SI364final.py, but of course you may include other files if you need.**

 **2.  A user should be able to load http://localhost:5000 and see the first page they ought to see on the application.**

 **3.  Include navigation in base.html with links (using a href tags) that lead to every other page in the application that a user should be able to click on. (e.g. in the lecture examples from the Feb 9 lecture, like this )**

 **4.  Ensure that all templates in the application inherit (using template inheritance, with extends) from base.html and include at least one additional block.**

 **5.  Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4).**

 **6.  Must have data associated with a user and at least 2 routes besides logout that can only be seen by logged-in users.**

 **7.  At least 3 model classes besides the User class.**

 **8.  At least one one:many relationship that works properly built between 2 models.**

 **9.  At least one many:many relationship that works properly built between 2 models.**

 **10.  Successfully save data to each table.**

 **11.  Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).**

 **12.  At least one query of data using an .all() method and send the results of that query to a template.**

 **13.  At least one query of data using a .filter_by(... and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table).**

 **14.  At least one helper function that is not a get_or_create function should be defined and invoked in the application.**

 **15.  At least two get_or_create functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).**

 **16.  At least one error handler for a 404 error and a corresponding template.**

 **17.  At least one error handler for any other error (pick one -- 500? 403?) and a corresponding template.**

 **18.  Include at least 4 template .html files in addition to the error handling template files.**

 **19.  At least one Jinja template for loop and at least two Jinja template conditionals should occur amongst the templates.**
 
 **20.  At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that does accord with other involved sites' Terms of Service, etc).**

 **21.  Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source to the database (in some way).**
 
 22.  At least one WTForm that sends data with a GET request to a new page.

 **23.  At least one WTForm that sends data with a POST request to the same page. (NOT counting the login or registration forms provided for you in class.)**

 24.  At least one WTForm that sends data with a POST request to a new page. (NOT counting the login or registration forms provided for you in class.)

 **25.  At least two custom validators for a field in a WTForm, NOT counting the custom validators included in the log in/auth code.**

 26.  Include at least one way to update items saved in the database in the application (like in HW5).

 **27.  Include at least one way to delete items saved in the database in the application (also like in HW5).**

 **28.  Include at least one use of redirect.**

 **29.  Include at least two uses of url_for. (HINT: Likely you'll need to use this several times, really.)**

 **30.  Have at least 5 view functions that are not included with the code we have provided. (But you may have more! Make sure you include ALL view functions in the app in the documentation and navigation as instructed above.)**
 
 # Attempted Extra Credit

 **1.  Deploy the application to the internet (Heroku) — only counts if it is up when we grade / you can show proof it is up at a URL and tell us what the URL is in the README. (Heroku deployment as we taught you is 100% free so this will not cost anything.)**
 
 # Detailed Explanation of Usage
 For this web application, anyone can search for tweets given any hashtag (hashtag string should not contain the #).  Examples to search for are "goblue", "michigan", "america", etc.  Once you enter an input to search for, the results will be shown back to you based on what Twitter's Search API finds.  By default, 5 tweets will be returned.  Users have to ability to see past searched hashtags as well as a list of all tweets that have been returned (users do not need to log in for this feature).  However, once they log in, they can navigate to create a personal collection of tweets, where they enter a name for the collection, as well as select tweets to add to that collection.  They can also delete a personal tweet collection, but that user needs to be logged in first.  
 
 # Routes -> Templates
 
1. `login` leads to `login.html` or redirects to `index.html` if login is successful
2. `logout` redirects to `index.html`
3. `register` leads to `register.html` or redirects to `login.html` after user registration
4. `index` leads to `index.html` or redirects to `searched_tweets.html` if validation for hashtag passes
5. `search_results` leads to `searched_tweets.html`
6. `search_terms` leads to `search_terms.html`
7. `all_tweets` leads to `all_tweets.html`
8. `create_collection` leads to `create_collection.html` or redirects to `collections.html` upon successful creation of a personal tweet collection.
9. `collections` leads to `collections.html`
10. `single_collection` leads to `collection.html`
11. `delete` redirects to `collections.html` after deleting a personal tweet collection

# Pip Modules
Here are the following pip modules to install that haven't been already used in a class session.

1.  `import requests_oauthlib` is need for the Twitter Search API


