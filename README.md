# Image API

Application for uploading images. 
Based on Account Tier, user has the ability to generate thumbnails in custom sizes, links to uploaded images in full-size and signed, timestamped url to the binary version of images.

**Live version available at:**

http://18.195.219.19/

**Installation instructions:**

Prerequisites for installation using docker-compose:
- Docker
- Git
---

- Open terminal and navigate to desired directory and type:

	`git clone https://github.com/adam-teszner/image_api.git .`
	`docker-compose up`

Executing commands may stop for a while at: 
> - LOG:  database system is ready to accept connections

But that's just the database performing a healthcheck. Just wait a few seconds...
After a while,  you should see a message from Django, that the server is running:
> - Starting development server at http://0.0.0.0:8000/
> - Quit the server with CONTROL-C.

And that's it. You should now be able to fully use this application.
Just open your browser and go to http://localhost:8000
You should be asked for username/password. Preinstalled users/tiers are:

- *basic/basic123*
- *premium/premium123*
- *enterprise/enterprise123*

If you wish to login to admin panel type: http://localhost:8000/admin

- *admin/admin123*

---

There is an **.env** file inside the project directory with default settings, passwords etc.
Please change those settings when in production, as well as change django settings:
`production = True`
