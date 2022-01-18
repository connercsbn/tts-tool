from distutils.log import error
from flask import Flask, session, request, render_template, send_file, redirect, url_for
import requests, json
import zipfile
from tts import get_clip
import io
from pprint import pprint

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
load_dotenv()

@app.route("/pronunciation/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        list = request.form['list']
        audio_files = []
        for line in [line for line in list.splitlines() if line]:
            audio_files.append(line)
        print(audio_files)
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as z:
            for af in audio_files:
                z.writestr('pronunciation_clips/' + af + '.mp3', get_clip(af))
        zip_buf.seek(0)
        if zip_buf.getbuffer().nbytes > 22:
            return send_file(
                zip_buf,
                mimetype='application/zip',
                as_attachment=True,
                attachment_filename='pronunciation_clips.zip'
            )
        else:
            session['text0'] = 'error'
            session['text1'] = 'you did not submit anything'
            return redirect(url_for('.error'))
    return render_template('index.html')

@app.route('/pronunciation/error', methods=['GET'])
def error():
    username = os.getenv('imgflip_username')
    password = os.environ.get('imgflip_password')
    text0 = session['text0']
    text1 = session['text1']
    res = requests.post('https://api.imgflip.com/caption_image', params={
        'template_id': '365775729/weinbach',
        'username': username,
        'password': password,
        'text0': text0,
        'text1': text1
    })
    imageurl = res.json()['data']['url']
    return render_template('error.html', e=text0, link=imageurl)
