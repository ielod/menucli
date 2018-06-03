Menu CLI
============

This python package provides a CLI for getting the daily menu from
restaurants' Facebook pages.

This CLI can only be used for restaurants, that
* have facebook pages
* post their menu on daily bases in written text!!!
* do not post other things...

To make this CLI work you need to be able to use the facebook graph API.
That means, you have to have an app ID and api token for that app id.


Installation
------------

To install use e.g. easy_install:

> sudo easy_install menucli-X.Y-py2.7.egg

This will install the CLI.


Config File
-----------

To be able to fetch data from Facebook Graph API a config file has to be
created under the user's home: ~/.config/menucli/menucli.cfg
Which should contain a Facebook App ID and App token.

Example config file content:

`[MenuCLI]`  
`app_id = 298522234894849`  
`app_token = lkajdlkajlkjfowapolyLKHJSOD`  


Restaurant YAML File
--------------------

The restaurant information should be listed in the file: 
~/.config/menucli/restaurants.json

It should contain entries with name, description, and tag, where:
* name: the short name of the restaurant without spaces
  this will be used in the CLI
* description: the full name of the restaurant (and location)
* tag: the facebook unique name (or ID) of the restaurant, which is the name in
  the facebook url

Example yaml file:

    ---
    restaurants:
      - name: 'eurest'
        description: 'Eurest Science Park Restaurant'
        tag: 'EurestSciencePark'
      - name: 'ibm'
        description: 'Ara-Parti Restaurant - Infopark Building A'
        tag: '234719740030074'


Usage of CLI
------------

To list configured restaurants:

> menucli list
> menucli list --detailed

To query the daily menu:

> menucli show <restaurant name>

e.g.:

> menucli show eurest
> menucli show --oneline ibm
 

Run tests for source code
-------------------------

Simply run:

> tox

This will run pylint, flake8 and unittests (with pytest)

