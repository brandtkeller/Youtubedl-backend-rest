# Video Cache Backend
This service is a pet project to be paired with a database (required) and a frontend web interface (Optional).
While this has been accomplished before, I enjoy new challenges that solve problems or make life a little easier. 

The thought here is having a minimal webstack (Backend + DB + Frontend) that would be deployed to either a static node or kuberenetes cluster.
You could then visit the web interface, submit youtube URL's to the form which would place them in the backend server Queue to be downloaded to the node (via a container bind mount)

## How I will be utilizing the Stack
I enjoy the world of self-hosting. As such I currently run a Plex server for my home media needs. I plan to bind mount the media directory from this container to a sub-directory of the Plex server media so that I can have a collection of local media to watch without internet as a necessity. 

## Getting Started

These instructions will get the backend REST API server running for development purposes

### Prerequisites

Necessary items to compile and run the server

```
python3-dev
python3-pip
ffmpeg
libpq-dev
```

### Installing

A step by step series of examples that tell you how to get a development env running

Dependencies
```
pip3 install flask Flask-API youtube-dl psycopg2
```

Database parameters
```
nano database.ini 
```

Run

```
python3 server.py <db host> <db name> <db user> <db password>
```

The server will now be running on port 5000

## Manual testing

Testing the server via command line

### REST test examples
```
curl -X POST localhost:5000/videos -H 'Content-type:application/json' -d '{"type":"video", "attributes":{"url":"https://youtu.be/7GFmAdRW_98", "directory":""}}'

Test for my K8s deployment
curl -X POST 192.168.0.122:31200/videos -H 'Content-type:application/json' -d '{"type":"video", "attributes":{"url":"https://youtu.be/7GFmAdRW_98", "directory":""}}'
```

## Deployment

Add additional notes about how to deploy this on a live system

## TODO
  
* Add error checking to runtime database parameters
* Add path to file output
* Add restart - startup procedures
	* Queue thread should get all DB rows with "pending" and "processing" status and fill the Queue then begin processing
* Add logic for when a video fails to process
	* PATCH /Videos/{ID} - Could change status to "refresh" and re-place in the queue - Need 
* Add logic for media directory structure
	* Maybe variable of the Video model
	* Default location or sub-directory
		* Check if sub-directory exists, if not create it
* Add GET/PATCH /config for future saved table preferences
## Suedo Logic
A user would have an interface to which upon opening would query all videos
* Display table with all current videos and statuses

There would be a form/panel available to submit a URL for download
Upon submitting, a POST /Video would be sent to the backend for processsing
* This would create a DB row in the videos table with a "Pending" status
* There would be a queue of videos that run in-series
* The video would be added to the queue to download when readu

Backend would return the new object with a "Pending" status

The backend would be processing the Queue and downloading in the order received (FIFO)
Each Queue item would have the related primary key for the DB row

Download Loop:
* Pull next item from Queue
* Change DB row Status to "Processing"
* Begin the download and conversion
* After completion Change the DB row Status
	* If error - "Error", Change StatusMessage to related error message"
	* If Completed - "Downloaded"

## API Endpoint CRUD

GET /Videos - Get all videos 
	* Get all videos from DB and return a list
	
Get /Videos/{id} - Get a specific Video by id
	* Queries for a specific video 'id'
	* This will be used for querying updates per video
	
POST /VIDEO - Add a new video to the Queue
	* Adds video to the Queue
	* Returns with a 200 w/ video object that has a "pending" status

DELETE /VIDEO/{id} - Remove video from the DB
	* If the video has a physical copy, maybe remove as well?
	* if status = "Error", just remove the DB row

## Video Model
* ID - primary key - Serial
* vid_url - Submitted during POST /VIDEO - String
* title - Retrieved in some manner? - String
* status - "Pending", "Processing", "Downloaded", "Error" - String
* status_message - "In-Queue", "Insert Error Message"
* vid_dir - "/","/work" - String

## Websocket
Websocket could be added to add realtime updates to videos in the queue

## Plex Integration
The main concept of the mounting structure is to mount this containers /data directory to a subdirectory of Plex's /media directory.
The library should be created as a Movie library with personal media. This downloader should add metadata to the video's.