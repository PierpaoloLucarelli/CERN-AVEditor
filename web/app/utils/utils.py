import ntpath
import os


def str2bool(v):
    """
    Converts a string to boolean

    :param v: Value to convert to boolean
    :return: The boolean result
    """
    return v.lower() in ("yes", "true", "t", "1")


def path_conversion(job_id, path):
    """
    Appends filename to path on ffmpeg machine
    This allows the ffmpeg machine to access the saved file
    :return: path of file on host machine
    """
    host_path = os.environ['FFMPEG_FILE_FOLDER']

    ntpath.basename("a/b/c")
    filename = path_leaf(path)
    return host_path + job_id + "/" +filename


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
