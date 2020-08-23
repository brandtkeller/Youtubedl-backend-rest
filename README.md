# YoutubeDL RESTFul Backend
This service is a pet project to be paired with a database (required) and a frontend web interface (Optional).
While this has been accomplished before, I enjoy new challenges that solve problems or make life a little easier. 

The thought here is having a minimal webstack (Backend + DB + Frontend) that would be deployed to either a static node or kuberenetes cluster.
You could then visit the web interface, submit youtube URL's to the form which would place them in the backend server Queue to be downloaded to the node (via a container bind mount)

## How I will be utilizing the Stack
I enjoy the world of self-hosting. As such I currently run a Plex server for my home media needs. I plan to bind mount the media directory from this container to a sub-directory of the Plex server media so that I can have a collection of local media to watch without internet as a necessity. 

## Docker
Main Docker Container:
* Written in python for embedding youtube-dl
* FLASK API endpoints

Requires a DB container pairing - PostgresDB

Saves Video's to a specific (or specified?) directory
* This could then be mounted to a Plex sub-library folder

## TODO
* Write CRUD logic for each endpoint w/ DB integration
	* Write for JSONAPI specification
* Add queue of some type for thread communication
* Add thread for Queue Processing
	* If there is an item or items in the Queue, grab first item in the Queue
	* Change Status to "Processing" and call youtube-dl on the url provided
* Add restart - startup procedures
	* Initial database connection - Create table if not exist by default
	* Queue thread should get all DB rows with "pending" and "processing" status and fill the Queue then begin processing
* Add logic for media directory structure
	* Maybe variable of the Video model
	* Default location or sub-directory
		* Check if sub-directory exists, if not create it

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


## Installation
```
pip3 install flask Flask-API youtube-dl psycopg2
```

## REST Example
```
curl -X POST localhost:5000/Videos -H 'Content-type:application/json' -d '{"type":"video", "attributes":{"url":"youtube.com/thisnewvid", "directory":"/"}}'
```