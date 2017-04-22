import sys
import logging

from hashlib import md5

import aiohttp

from .constants import DISCORD_MSG_CHAR_LIMIT

LOG = logging.getLogger(__name__)


def load_file(filename, skip_commented_lines=True, comment_char='#'):
    """ TODO """
    try:
        with open(filename, encoding='utf8') as file_:
            results = []
            for line in file_:
                line = line.strip()

                if line and not (skip_commented_lines and
                                 line.startswith(comment_char)):
                    results.append(line)

            return results

    except IOError as error:
        LOG.error("Error loading %s - %s", filename, error)
        return []


def write_file(filename, contents):
    """ TODO """
    with open(filename, 'w', encoding='utf8') as file_:
        for item in contents:
            file_.write(str(item))
            file_.write('\n')

def format_time_ffmpeg(seconds):
    """ TODO """
    total_msec = seconds * 1000
    total_seconds = seconds
    total_minutes = seconds / 60
    total_hours = seconds / 3600
    msec = int(total_msec % 1000)
    sec = int(total_seconds % 60 - (msec / 3600000))
    mins = int(total_minutes % 60 - (sec / 3600) - (msec / 3600000))
    hours = int(total_hours - (mins / 60) - (sec / 3600) - (msec / 3600000))

    return "{:02d}:{:02d}:{:02d}".format(hours, mins, sec)

def paginate(content, *, length=DISCORD_MSG_CHAR_LIMIT, reserve=0):
    """
    Split up a large string or
     list of strings into chunks for sending to discord.
    """
    if isinstance(content, str):
        contentlist = content.split('\n')
    elif isinstance(content, list):
        contentlist = content
    else:
        raise ValueError("Content must be str or list, not %s" % type(content))

    chunks = []
    currentchunk = ''

    for line in contentlist:
        if len(currentchunk) + len(line) < length - reserve:
            currentchunk += line + '\n'
        else:
            chunks.append(currentchunk)
            currentchunk = ''

    if currentchunk:
        chunks.append(currentchunk)

    return chunks


async def get_header(session, url, headerfield=None, *, timeout=5):
    """ TODO """
    with aiohttp.Timeout(timeout):
        async with session.head(url) as response:
            if headerfield:
                return response.headers.get(headerfield)
            else:
                return response.headers


def md5sum(filename, limit=0):
    """ TODO """
    fhash = md5()
    with open(filename, "rb") as file_:
        for chunk in iter(lambda: file_.read(8192), b""):
            fhash.update(chunk)
    return fhash.hexdigest()[-limit:]


def fixg(x, dp=2):
    """ TODO """
    return ('{:.%sf}' % dp).format(x).rstrip('0').rstrip('.')


def ftimedelta(timedelta):
    """ TODO """
    part1, part2 = str(timedelta).rsplit(':', 1)
    return ':'.join([part1, str(int(float(part2)))])


def safe_print(content, *, end='\n', flush=True):
    """ TODO """
    sys.stdout.buffer.write((content + end).encode('utf-8', 'replace'))
    if flush:
        sys.stdout.flush()


def avg(i):
    """ TODO """
    return sum(i) / len(i)


def objdiff(obj1, obj2, *, access_attr=None, depth=0):
    """ TODO """
    changes = {}

    if access_attr is None:
        def attrdir(x):
            """ TODO """
            return x

    elif access_attr == 'auto':
        if hasattr(obj1, '__slots__') and hasattr(obj2, '__slots__'):
            def attrdir(x):
                """ TODO """
                return getattr(x, '__slots__')

        elif hasattr(obj1, '__dict__') and hasattr(obj2, '__dict__'):
            def attrdir(x):
                """ TODO """
                return getattr(x, '__dict__')

        else:
            # LOG.everything("{}{} or {} has no slots \
            # or dict".format('-' * (depth+1), repr(obj1), repr(obj2)))
            attrdir = dir

    elif isinstance(access_attr, str):
        def attrdir(x):
            """ TODO """
            return list(getattr(x, access_attr))

    else:
        attrdir = dir

    # LOG.everything("Diffing {o1} and {o2} with {attr}" \
    # .format(o1=obj1, o2=obj2, attr=access_attr))

    for item in set(attrdir(obj1) + attrdir(obj2)):
        try:
            iobj1 = getattr(obj1, item, AttributeError("No such attr " + item))
            iobj2 = getattr(obj2, item, AttributeError("No such attr " + item))

            # LOG.everything("Checking {o1}.{attr} and {o2}.{attr}" \
            # .format(attr=item, o1=repr(obj1), o2=repr(obj2)))

            if depth:
                # LOG.everything("Inspecting level {}".format(depth))
                idiff = objdiff(
                    iobj1, iobj2, access_attr='auto', depth=depth - 1)
                if idiff:
                    changes[item] = idiff

            elif iobj1 is not iobj2:
                changes[item] = (iobj1, iobj2)
                # LOG.everything("{1}.{0} ({3}) is not {2}.{0} ({4}) " \
                # .format(item, repr(obj1), repr(obj2), iobj1, iobj2))

            else:
                pass
                # LOG.everything("{obj1}.{item} is {obj2}.{item} ({val1} \
                # and {val2})".format(obj1=obj1, obj2=obj2, item=item, \
                # val1=iobj1, val2=iobj2))

        except Exception as error:
            # LOG.everything("Error checking {o1}/{o2}.{item}" \
            # .format(o1=obj1, o2=obj2, item=item), exc_info=error)
            continue

    return changes


def color_supported():
    """ TODO """
    return hasattr(sys.stderr, "isatty") and sys.stderr.isatty()
