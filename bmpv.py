import os
import re
import requests
from urllib.parse import urlparse, unquote


class Video:

    def __init__(self, url, title, video_url, audio_url, cid, resolution):
        self.url = url
        self.title = title
        self.video_url = video_url
        self.audio_url = audio_url
        self.cid = cid
        self.resolution = resolution

    def download_subtitle(self, work_dir):
        exit_code = os.system('BBDown "{}" --sub-only --work-dir "{}"'.format(
            self.url, work_dir))
        if exit_code != 0:
            raise Exception(
                'BBDown: process exited with non-zero code: {}'.format(
                    exit_code))

    def prepare_subtitle(self):
        work_dir = '/tmp'
        quoted_title = self.title.replace('/', '.')

        sub_dir = os.path.join(work_dir, quoted_title, '')
        if os.path.exists(sub_dir):
            os.system('rm -rf {}'.format(sub_dir))

        self.download_subtitle(work_dir)

        sub_dir = os.path.join(work_dir, quoted_title, '')
        if os.path.exists(sub_dir):
            for subtitle_filename in os.listdir(sub_dir):
                if subtitle_filename.endswith('zh-CN.srt'):
                    return os.path.join(sub_dir, subtitle_filename)

        return None

    def download_danmaku_xml(self, path):
        danmaku_url = 'https://comment.bilibili.com/{}.xml'
        response = requests.get(danmaku_url.format(self.cid))
        response.encoding = 'utf-8'
        open(path, 'w').write(response.text)

    def generate_danmaku_ass(self, input_path, output_path):
        exit_code = os.system(
            'danmaku2ass --font MiSans -a 0.6 -fs 36 -dm 10 -ds 10 --size {} -o "{}" "{}"'
            # .format(self.resolution, output_path, input_path))
            .format('1920x1080', output_path, input_path))
        if exit_code != 0:
            raise Exception(
                'danmaku2ass: process exited with non-zero code: {}'.format(
                    exit_code))

    def prepare_danmaku(self):
        quoted_title = self.title.replace('/', '.')
        xml_path = '/tmp/{}.xml'.format(quoted_title)
        ass_path = '/tmp/{}.ass'.format(quoted_title)

        self.download_danmaku_xml(xml_path)
        self.generate_danmaku_ass(xml_path, ass_path)

        os.remove(xml_path)
        return ass_path

    def play(self):
        self.danmaku_path = self.prepare_danmaku()
        self.subtitle_path = self.prepare_subtitle()

        if self.subtitle_path != None:
            play_command = "mpv '{}' --audio-file='{}' --sub-file='{}' --sub-file='{}' --secondary-sid=auto --sub-border-size=1 --no-ytdl --referrer='https://www.bilibili.com'"
            os.system(
                play_command.format(self.video_url, self.audio_url,
                                    self.danmaku_path, self.subtitle_path))
        else:
            play_command = "mpv '{}' --audio-file='{}' --sub-file='{}' --sub-border-size=1 --no-ytdl --referrer='https://www.bilibili.com'"
            os.system(
                play_command.format(self.video_url, self.audio_url,
                                    self.danmaku_path))
        os.remove(self.danmaku_path)


def get_url():
    return os.sys.argv[1]


def parse_params(url):
    assignments = [
        raw_assignment.split('=')
        for raw_assignment in urlparse(url).query.split('&')
    ]
    return {
        assignment[0]: unquote(assignment[1])
        for assignment in assignments
    }


def get_title(bbdown_output):
    pattern = r'(?m)视频标题: (.*)'
    return re.search(pattern, bbdown_output).group(1)


def get_video_url(bbdown_output):
    pattern = r'(?m)\d+\.( \[.+?\]){6}$\s+(.*?)$'
    return re.search(pattern, bbdown_output).group(2)


def get_audio_url(bbdown_output):
    pattern = r'(?m)\d+\. \[M4A\]( \[.+?\])+$\s+(.*?)$'
    return re.search(pattern, bbdown_output).group(2)


def get_resolution(bbdown_output):
    pattern = r'(?m)\d+\.( \[(.+?)\]){2}( \[.+?\]){4}$\s+(.*?)$'
    return re.search(pattern, bbdown_output).group(2)


def get_bbdown_output(url):
    return os.popen("BBDown '{}' --encoding-priority 'av1,hevc,avc' -info".format(url)).read()


def resolve(params):
    url = params['url']
    output = get_bbdown_output(url)
    return Video(url, get_title(output), get_video_url(output),
                 get_audio_url(output), params['cid'], get_resolution(output))


# bmpv:///?url=www.bilibili.com/video/av1&cid=12345
def main():
    print(os.sys.argv)
    try:
        resolve(parse_params(get_url())).play()
    except Exception as err:
        print(err.__repr__())
        input()


if __name__ == "__main__":
    main()
