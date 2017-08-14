import os

import paramiko
from flask import json

from app.extensions import setup_custom_logger


class FfmpegTaskRunner:
    ffprobe_bin = os.environ['FFPROBE_BIN']
    ffmpeg_bin = os.environ['FFMPEG_BIN']
    # Command returns JSON data about the video
    ffprobe_command = "-v quiet -print_format json -show_format -show_entries stream=width,height,duration,codec_type"
    # Command cuts a video give start and stop time
    ffmpeg_cut = "-i {} -ss {} -t {} -c copy {}/vid_cut.mp4"

    logger = setup_custom_logger('root')
    upload_folder = os.environ['FFMPEG_FILE_FOLDER']

    def ffprobe(self, job_id, filename):
        """
        Will generate the ffprobe command to get the details of a video
        :param job_id: The id of the job (video)
        :param filename: The name of the file that the ffprobe command will run on
        :return: The ffprobe command to get details of one video
        """
        path_to_file = self.upload_folder + "in/" + job_id + "/" + filename
        return self.ffprobe_bin + " " + self.ffprobe_command + " " + path_to_file

    def ffmpeg_cut_video(self, job_id, filename, start_time, stop_time):
        """
        Will generate the ffmpeg command to cut a video given start and stop time
        :param job_id: The id of the job (video)
        :param filename: The name of the file that the ffmpeg command will run on
        :param start_time: The time at which the video will start (left cut)
        :param stop_time: The time at which the video will stop (right cut)
        :return: The ffmpeg command to cut the provided video
        """
        return self.ffmpeg_bin + " " + self.ffmpeg_cut.format(
            os.environ['FFMPEG_FILE_FOLDER'] + "in/" + job_id + "/" + filename,
            start_time,
            stop_time,
            os.environ['FFMPEG_FILE_FOLDER'] + "in/" + job_id
        )

    def concat_images_to_video(self, slides, video, job_id):
        """
        will generate the ffmpeg command to add intro and outro slides to a video. Command syntax:

        ffmpeg -loop 1 -t <slide1_duration> -i <slide1_file> -loop 1 -t <slide2_duration> -i <slide2_file>  -t 5 -f
        lavfi -i aevalsrc=0 -i <video_file.mp4>
        -filter_complex "[0:v]scale=<video_width>:<video_height>:force_original_aspect_ratio=decrease,pad=<video_width>:<video_height>:(ow-iw)/2:(oh-ih)/2[v0];
        [1:v]scale=<video_width>:<video_height>:force_original_aspect_ratio=decrease,pad=<video_width>:<video_height>:(ow-iw)/2:(oh-ih)/2[v1];
        [v0][2:a][3:v][3:a][v1][2:a] concat=n=3:v=1:a=1" <path_to_output.mp4>

        see documentation for mor details

        :param slides: file names of the slides to append to a video
        :param video: The target video for the slides
        :param job_id: The id of the video
        :return: The ffmpeg String command
        """
        no_slides = str(len(slides))
        null_audio_src = '-t 5 -f lavfi -i aevalsrc=0'
        filter_complex_start = '-filter_complex "'
        filter_complex_end = 'concat=n=' + str(len(slides) + 1) + ':v=1:a=1"'
        input_video = '-i ' + self.upload_folder + "in/" + job_id + '/' + video.file
        input_images = ''
        input_images_rules = ''
        intro_pads = ''
        outro_pads = ''
        video_pad = '[' + str(len(slides) + 1) + ':v][' + str(len(slides) + 1) + ':a]'
        output_video = self.upload_folder + 'out/' + job_id + '/output.mp4'

        for i, slide in enumerate(slides):
            input_images += '-loop 1 -t 5 -i ' + self.upload_folder + "in/" + job_id + "/img/" + slide.img_upload + " "
            input_images_rules += '[' + str(i) + ':v]scale=' + str(video.width) + ':' + str(video.height) + \
                                  ':force_original_aspect_ratio=decrease,pad=' + str(video.width) + ':' + str(
                                   video.height) + ':(ow-iw)/2:(oh-ih)/2[v' + str(i) + '];'
            if slide.slide_type == 'intro':
                intro_pads += '[v' + str(i) + '][' + no_slides + ':a]'
            else:
                outro_pads += '[v' + str(i) + '][' + no_slides + ':a]'

        command = self.ffmpeg_bin + " " + input_images + " " + null_audio_src + " " + input_video + " " + \
                  filter_complex_start + input_images_rules + intro_pads + video_pad + outro_pads + " " + filter_complex_end + " " + \
                  output_video

        return command

    def ffmpeg_run(self, cmd):
        """
        WIll run a specified command over SSH
        :param cmd: The command to be executed on the remote machine
        :return: A JSON object containing the stdout of the executed command, and the success flag
        """
        ssh = self.init_ssh_client()
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        self.logger.debug("Executed cmd: %s \n", cmd)
        # if ssh return success code: 0
        if ssh_stdout.channel.recv_exit_status() == 0:
            output = ""
            # ssh command returns an array containing the JSON output,
            # parse JSON
            for line in ssh_stdout.readlines():
                output += line.rstrip()
            ssh.close()
            if self.is_json(output):
                output = json.loads(output)
                output['success'] = True
                return output
            return {"success": True}
        self.logger.error('FFmpeg error\n')
        ssh.close()
        return {"success": False}

    def is_json(self, myjson):
        try:
            json.loads(myjson)
        except ValueError:
            return False
        return True

    def init_ssh_client(self):
        """
        Initializes and ssh connection to a remote machine
        :return: the ssh client
        """
        ssh = paramiko.SSHClient()
        # automatically adds host to known hosts list
        k = paramiko.RSAKey.from_private_key_file(os.environ['SSH_KEY'])
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.logger.debug("CONNECTING at {}@{}".format(os.environ['SSH_USERNAME'], os.environ['SSH_SERVER']))
        ssh.connect(os.environ['SSH_SERVER'], username=os.environ['SSH_USERNAME'], pkey=k)
        self.logger.debug('Connected to the SSH client')
        return ssh
