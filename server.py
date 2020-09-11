from flask import request, url_for, jsonify, make_response
from flask_api import FlaskAPI, status, exceptions
import youtube_dl
from database import create_table, get_all_rows, get_row_by_id, create_row, update_row, delete_row
from video import Video
from queue import Queue 
from threading import Thread
import sys

app = FlaskAPI(__name__)

# Custom response method for adding headers and data formatting
def mod_response(data, status_code):
    res = make_response(jsonify(data), status_code)
    return res

@app.route("/health", methods=['GET'])
def service_health():
    rows = get_all_rows()
    if len(rows) != None:
        return mod_response({'data':'Service is healthy'}, 200)
    else:
        return mod_response({'error':'Service is unhealthy'}, 500)

@app.route("/videos", methods=['GET', 'POST', 'OPTIONS'])
def videos_list():
    if request.method == 'POST':
        # We are only expecting the URL and Directory
        data = request.json
        vid_url = data["data"]["attributes"]["url"]
        vid_dir = data["data"]["attributes"]["directory"]
        if vid_url == None:
            return mod_response({'error':'URL not specified'}, 400)
        if vid_dir == None:
            vid_dir = ""
        
        # Create the Video row & object
        rowId = create_row(vid_url, "", "Pending", "Placed in Queue", vid_dir)
        newVid = Video(rowId, vid_url, "", "Pending", "Placed in Queue", vid_dir)

        # Pass this video object to the Queue
        q.put(newVid)

        return mod_response({'data':newVid.toJson()}, 201)

    else:
        data = {
            'data': [Video(row[0], row[1], row[2], row[3], row[4], row[5]).toJson() for row in get_all_rows()]
        }
        
        return mod_response(data, 200)


@app.route("/videos/<int:key>", methods=['GET', 'DELETE'])
def videos_detail(key):

    if request.method == 'DELETE':
        delete_row(key)
        return mod_response({'data':{}}, 204) 

    # request.method == 'GET'
    row = get_row_by_id(key)
    if row == None:
        raise exceptions.NotFound()
    newVid = Video(row[0], row[1], row[2], row[3], row[4], row[5])
        
    return mod_response({'data':newVid.toJson()}, 200)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST, DELETE')
    return response

# --------- Video Processor Logic ----------
# Global Variables
processing = False
video_processing = None

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
        global video_processing
        video_processing.status = 'Error'
        video_processing.status_message = msg
        video_processing.save()

def processor(in_q):
    startup(in_q)

    while True:
        vid = in_q.get()
        print("New thread started")
        t2 = Thread(target = download, args =(vid, ), daemon=True) 
        t2.start()
        t2.join()
        print("Thread joined")

def startup(q):
    rows = get_all_rows()
    for row in rows:
        if row[3] == 'Pending' or row[3] == 'Processing':
            q.put(Video(row[0], row[1], row[2], row[3], row[4], row[5]))

def my_hook(d):
    if d['status'] == 'finished':
        global video_processing
        print('Video ' + video_processing.title + ' has finished downloading.')
        video_processing.status = 'Downloaded'
        video_processing.status_message = 'Download Compeleted'
        video_processing.save()

def download(video):
    global video_processing
    ydl_opts = {
    'noplaylist' : True,
    'outtmpl': video.dir + '%(title)s.%(ext)s',
    'progress_hooks': [my_hook],
    'logger': MyLogger(),
    'writethumbnail': True,
    'postprocessors': [{
        'key': 'FFmpegMetadata'
    }]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video.url, download=False)
        video_title = info_dict.get('title', None)
        video.title = video_title
        video.status = "Processing"
        video.status_message = "Beginning Download"
        video.save()
        video_processing = video
        ydl.download([video.url])


if __name__ == "__main__":
    try:
        if len(sys.argv) < 5:
            print('Incorrect runtime arguments passed')
            print('Usage:')
            print('  python3 server.py <db host> <db name> <db user> <db password>')
            sys.exit(1)

        create_table()
        q = Queue() 
        t1 = Thread(target = processor, args =(q, ), daemon=True) 
        t1.start()
        app.run(debug=True, host='0.0.0.0')
        
    except KeyboardInterrupt:
        t1.join()
        print("Attempting to exit gracefully")
        sys.exit(0)
    
