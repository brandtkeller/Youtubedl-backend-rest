from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
import youtube_dl
from database import create_table, get_all_rows, get_row_by_id, create_row, update_row, delete_row
from video import Video
from queue import Queue 
from threading import Thread
import sys

app = FlaskAPI(__name__)
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
        global processing
        video_processing.status = 'error'
        video_processing.status_message = msg
        video_processing.save()

        processing = False


@app.route("/Videos", methods=['GET', 'POST'])
def videos_list():
    if request.method == 'POST':
        # We are only expecting the URL and Directory
        data = request.json
        print()
        vid_url = data["attributes"]["url"]
        vid_dir = data["attributes"]["directory"]
        if vid_url == None:
            return "Error", status.HTTP_400_BAD_REQUEST
        if vid_dir == None:
            vid_dir = ""
        
        # Create the Video row & object
        rowId = create_row(vid_url, "", "Pending", "Placed in Queue", vid_dir)
        newVid = Video(rowId, vid_url, "", "Pending", "Placed in Queue", vid_dir)

        # Pass this video object to the Queue
        q.put(newVid)

        return {'data':newVid.toJson()},status.HTTP_201_CREATED

    # request.method == 'GET'
    else:
        return {
            'data': [Video(row[0], row[1], row[2], row[3], row[4], row[5]).toJson() for row in get_all_rows()]
        }


@app.route("/Videos/<int:key>", methods=['GET', 'DELETE'])
def videos_detail(key):

    if request.method == 'DELETE':
        delete_row(key)
        return {'data':{}}, status.HTTP_204_NO_CONTENT

    # request.method == 'GET'
    row = get_row_by_id(key)
    if row == None:
        print("There was no row returned for this ID")
        raise exceptions.NotFound()
    newVid = Video(row[0], row[1], row[2], row[3], row[4], row[5])
        
    return {'data':newVid.toJson()}

def processor(in_q):
    global processing
    while True:
        print("Processing = " + str(processing))
        if processing == False:
            vid = in_q.get()
            download(vid)
        else:
            continue

def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')
        global video_processing
        global processing

        print('video_processing id = ' + str(video_processing.id))
        video_processing.status = 'downloaded'
        video_processing.status_message = 'Download Compeleted'
        video_processing.save()

        processing = False

def download(video):
    global video_processing
    global processing
    processing = True
    ydl_opts = {
    'noplaylist' : True,
    'outtmpl': '/data/' + video.dir + '%(title)s.%(ext)s',
    'progress_hooks': [my_hook],
    'logger': MyLogger()
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video.url, download=False)
        video_title = info_dict.get('title', None)
        video.title = video_title
        video.status = "processing"
        video.status_message = "Beginning Download"
        print('Video db ID = ' + str(video.id))
        video.save()
        video_processing = video
        ydl.download([video.url])


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print('Incorrect runtime arguments passed')
        print('Usage:')
        print('  python3 server.py <db host> <db name> <db user> <db password>')
        sys.exit(1)

    create_table()
    q = Queue() 
    t1 = Thread(target = processor, args =(q, ), daemon=True) 
    t1.start()
    app.run(debug=True)
    t1.join()
