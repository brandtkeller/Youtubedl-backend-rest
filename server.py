from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions
import youtube_dl
from database import create_table, get_all_rows, get_row_by_id, create_row, update_row, delete_row
from video import Video

app = FlaskAPI(__name__)


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
            vid_dir = "/"
        
        # Create the Video row & object
        rowId = create_row(vid_url, "", "Pending", "Placed in Queue", vid_dir)
        newVid = Video(rowId, vid_url, "", "Pending", "Placed in Queue", vid_dir)

        # Pass this video object to the Queue

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


if __name__ == "__main__":

    app.run(debug=True)