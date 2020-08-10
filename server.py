import os
import sys

from flask import Flask, render_template,request, send_file
from unidecode import unidecode


app = Flask(__name__)
global_db = None


RELATIVE_DATA_FOLDER = 'data'
DATA_FILES = ['ordered_songs.csv']
SCHEMA = [
    'number', 'name', 'author', 'makam', 'form', 'usul', 'composer'
    ]


# Cache the directory, so we do not list a 20k+ folder multiple times.
dirdata = None
def listdatadir():
    global dirdata
    if dirdata:
        return dirdata
    else:
        dirdata = os.listdir(RELATIVE_DATA_FOLDER)
        return dirdata


# All strings shall be lowercase and all english characters
def standardize(str_obj):
    return unidecode(str_obj).lower()


# A simple class to hold all song information.
class Song(object):
    def __init__(self, data):
        self.number = data[0]
        self.row = {
            SCHEMA[i]: data[i] for i in  range(len(SCHEMA))}

    def __str__(self):
        return str(self.row)

    def __repr__(self):
        return str(self.row)

    def tablerow(self):
        return self.row.values()

    def compare(self, search_str):
        for _, v in self.row.items():
            if search_str in v:
                return True

        return False

    def getFileList(self):
        files = listdatadir()
        tmp1 = self.number + '.'
        tmp2 = self.number + '_'
        return [x for x in files if x.startswith(tmp1) or x.startswith(tmp2)]


# The class to hold the database.
class SongDatabase(object):
    def __init__(self, files=DATA_FILES):
        self.data = []
        for f in files:
            with open(f, encoding='utf-8') as csvfile:
                lines = csvfile.readlines()
            for row in lines:
                self.data.append(Song(standardize(row).split(',')))

    def find(self, search_str):
        std_search_str = standardize(search_str)
        return [x for x in self.data if x.compare(std_search_str)]

# Main page.
@app.route('/', methods=['GET', 'POST'])
def search_page():
    kwargs = {}
    if request.method == 'POST':
        results = global_db.find(request.form['search_str'])
        kwargs['number_of_results'] = len(results)
        kwargs['table'] = [r.tablerow() for r in results]
        kwargs['images'] = [r.getFileList() for r in results]

    return render_template('index.html', **kwargs)

# Get the songs.
@app.route('/song/<image>')
def song_page(image):
    return send_file(
        os.path.join(RELATIVE_DATA_FOLDER, image),
        mimetype='image/tiff')


if __name__ == "__main__":
    # Warm up the house!
    global_db = SongDatabase()
    listdatadir()

    # Serve all the things.
    # app.run()
    app.run(port=5000, host='0.0.0.0')
