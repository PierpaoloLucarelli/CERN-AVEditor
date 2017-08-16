#
Webcast: AVEditor

Original respository: [https://gitlab.cern.ch/webcast/AVEditor/tree/openshift](https://gitlab.cern.ch/webcast/AVEditor/tree/openshift)

An automated video editing and encoding tool accessed though a web interface used for:

* Trimming a video
* Adding intro / outro slides
* Encoding the video to a standard format \(H.264 for video stream, AAC for audio stream, original resolution mantained\)

## Requirements and dependencies

---

* Docker + Docker Compose
* PostgreSQL DB
* Remote FFmpeg machine

## Installing and running on localhost

---

After cloning the repository: [https://gitlab.cern.ch/webcast/AVEditor.git](https://gitlab.cern.ch/webcast/AVEditor.git) run:

```
docker-compose build
```

```
docker-compose up
```

## Configuration

---

#### Flask config

`APP_PORT` , `DEBUG` , `TESTING`

#### WTF-forms

`SECRET_KEY`

#### Flask-Uploads

Even though the value of these env vars may be the same, it's still necessary to specify each one separately as these values are used to override the default destination location of the [UploadSets](https://pythonhosted.org/Flask-Uploads/)

These env vars must contain paths with trailing slash, Example: _/path/to/input/folder/_

`UPLOADED_IMAGES_DEST`, `UPLOADED_VIDEO_DEST`, `UPLOADS_DEFAULT_DEST`, `UPLOADED_VIDEO_URL`, `VIDEO_OUTPUT_DEST`

#### Database

`DB_NAME`, `DB_PASS`, `DB_PORT`, `DB_SERVICE`, `DB_USER`

#### FFmpeg

Binaries to ffmpeg and ffprobe without trailing slash, Example: _/usr/bin/ffmpeg_

`FFMPEG_BIN`, `FFPROBE_BIN`

remote machine's path to input video folder: This will be the path of the mounted EOS FS plus the input dir

`FFMPEG_FILE_FOLDER`

#### SSH

SSH\_KEY_ will contain path like_: /path/to/ssh/key/id\_rsa

`SSH_SERVER`, `SSH_USERNAME`, `SSH_KEY`

#### OAUTH

`CERN_OAUTH_CLIENT_ID`, `CERN_OAUTH_CLIENT_SECRET`

#### SMTP

`MAIL_HOSTNAME`, `MAIL_FROM`

#### File download

Hostname of the server on wihch the file to be downloaded wil reside

`HOSTNAME`

## FFmpeg commands

---

Some ffmpeg commands used by AVEditor. These commands are generate in the **app.utils.ffmpeg** Class

**Command used to get information about the video in JSON format**

```
ffprobe -v quiet -print_format json -show_format -show_entries stream=width,height,duration,codec_type <output_file_path.mp4>
```

**Command used to cut a video given sart ad stop time **

```
ffmpeg -i <path_to_video_file.mp4> -ss <start_time> -t <stop_time> -c copy <path_to_output_file.mp4>
```

start and stop time need to be in the following format: HH:MM:SS, for example:

```
ffmpeg -i <path_to_video_file.mp4> -ss 00:00:20 -t 00:02:45 -c copy <path_to_output_file.mp4>
```

**Command used to concatenate intro and outro slides to a video**

Brief explanation of

`-loop 1 -t 5 -i <slide1_path>` - Generates a video of t seconds from image i

`-i aevalsrc=0` - Generates silent audio to fill in audio stream of the image-generated video

`-i <video_path>` - Input video

**Complex filter**

For each slide we select the video stream `[<no_slide>:v]` and apply some filters like resizing and padding

Then we assign an alias to this video stream for the first slide `[v0]`, for second `[v1]` etc...

for the first slide:

`[0:v]scale=480:360:force_original_aspect_ratio=decrease,pad=480:360:(ow-iw)/2:(oh-ih)/2[v0]`

`[v0][1:a][2:v][2:a]` - Choose the order of the video streams, in this case we use the alias of the first generated video, concat the null audio src and the original video and audio stream of the input video

`concat=n=2:v=1:a=1` - Concatenate 2 video streams into 1 video stream and 1 audio stream

**Command to concatenate 1 intro slide \(5 seconds\) to one video**

```
ffmpeg -loop 1 -t 5 -i <slide1_path> -t <slide1_duration> -f lavfi
-i aevalsrc=0
-i <video_path>
-filter_complex
"[0:v]scale=480:360:force_original_aspect_ratio=decrease,pad=480:360:(ow-iw)/2:(oh-ih)/2[v0];
[v0][1:a][2:v][2:a] concat=n=2:v=1:a=1"
<path_to_output_video>
```

**Command to concatenate 1 intro and 1 outro slide \(5 seconds\) to a video**

```
ffmpeg -loop 1 -t 5 -i <intro_slide_path> -loop 1 -t 5 -i <outro_slide_path> -t 5
-f lavfi -i aevalsrc=0
-i <video_path>
-filter_complex
"[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2[v0];
[1:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2[v1];
[v1][2:a][3:v][3:a][v0][2:a] concat=n=3:v=1:a=1"
<output_video_path>
```

## Future work

---

1. Delete video from FS after download has been completed


