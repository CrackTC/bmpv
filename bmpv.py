#!/usr/bin/env python3
import os
import sys
import re
import json
import requests
from urllib.parse import urlparse, unquote


class Configuration:

    def __init__(self, font: str, font_size: int, danmaku_opacity: float,
                 marquee_duration: int, still_duration: int,
                 size: str) -> None:
        self.font = font
        self.font_size = font_size
        self.danmaku_opacity = danmaku_opacity
        self.marquee_duration = marquee_duration
        self.still_duration = still_duration
        self.size = size


def parse_configuration(path) -> Configuration:
    # read json formatted configuration from path
    configuration = json.load(open(path, 'r', encoding='utf-8'))
    return Configuration(configuration['font'], configuration['font_size'],
                         configuration['danmaku_opacity'],
                         configuration['marquee_duration'],
                         configuration['still_duration'],
                         configuration['size'])


class Video:

    def __init__(self, url: str, title: str, video_info: tuple[str, str],
                 audio_url: str, cid: str, resolution: str) -> None:
        self.url = url
        self.title = title
        self.video_url = video_info[1]
        self.is_dolby_vision = video_info[0].find('杜比视界') != -1
        self.audio_url = audio_url
        self.cid = cid
        self.resolution = resolution

    def download_subtitle(self, work_dir) -> None:
        exit_code = os.system('BBDown "{}" --sub-only --work-dir "{}"'.format(
            self.url.replace('"', '\\"'), work_dir.replace('"', '\\"')))
        if exit_code != 0:
            raise Exception(
                'BBDown: process exited with non-zero code: {}'.format(
                    exit_code))

    def prepare_subtitle(self) -> (str | None):
        work_dir = '/tmp'
        quoted_title = self.title.replace('/', '.')

        sub_dir = os.path.join(work_dir, quoted_title, '')
        if os.path.exists(sub_dir):
            os.system('rm -rf "{}"'.format(sub_dir.replace('"', '\\"')))

        self.download_subtitle(work_dir)

        sub_dir = os.path.join(work_dir, quoted_title, '')
        if os.path.exists(sub_dir):
            for subtitle_filename in os.listdir(sub_dir):
                if subtitle_filename.endswith('zh-CN.srt'):
                    return os.path.join(sub_dir, subtitle_filename)

        return None

    def download_danmaku_xml(self, path) -> None:
        danmaku_url = 'https://comment.bilibili.com/{}.xml'
        response = requests.get(danmaku_url.format(self.cid))
        response.encoding = 'utf-8'
        open(path, 'w').write(response.text)

    def generate_danmaku_ass(self, input_path, output_path) -> None:
        exit_code = os.system(
            'danmaku2ass --font "{}" -a {} -fs {} -dm {} -ds {} --size {} -o "{}" "{}"'
            # .format(self.resolution, output_path, input_path))
            .format(self.configuration.font.replace('"', '\\"'),
                    self.configuration.danmaku_opacity,
                    self.configuration.font_size,
                    self.configuration.marquee_duration,
                    self.configuration.still_duration,
                    self.configuration.size,
                    output_path.replace('"', '\\"'),
                    input_path.replace('"', '\\"')))
        if exit_code != 0:
            raise Exception(
                'danmaku2ass: process exited with non-zero code: {}'.format(
                    exit_code))

    def prepare_danmaku(self) -> str:
        quoted_title = self.title.replace('/', '.')
        xml_path = '/tmp/{}.xml'.format(quoted_title)
        ass_path = '/tmp/{}.ass'.format(quoted_title)

        self.download_danmaku_xml(xml_path)
        self.generate_danmaku_ass(xml_path, ass_path)

        os.remove(xml_path)
        return ass_path

    def play(self, configuration: Configuration) -> None:
        self.configuration = configuration
        self.danmaku_path = self.prepare_danmaku()
        self.subtitle_path = self.prepare_subtitle()

        play_command = "mpv '{}' --audio-file='{}' --sub-file='{}' --sub-border-size=1 --no-ytdl --referrer='https://www.bilibili.com'".format(
            self.video_url, self.audio_url,
            self.danmaku_path.replace('\'', "\\'"))

        if self.is_dolby_vision:
            play_command += ' --vo=gpu-next'

        if self.subtitle_path != None:
            play_command += " --sub-file='{}' --secondary-sid=auto"
            os.system(play_command.format(self.subtitle_path))
        else:
            os.system(play_command)
        os.remove(self.danmaku_path)


def get_url() -> str:
    return sys.argv[1]


def parse_params(url) -> dict[str, str]:
    assignments = [
        raw_assignment.split('=')
        for raw_assignment in urlparse(url).query.split('&')
    ]
    return {
        assignment[0]: unquote(assignment[1])
        for assignment in assignments
    }


def get_title(bbdown_output) -> str:
    pattern = r'(?m)视频标题: (.*)'
    result = re.search(pattern, bbdown_output)
    if result:
        return result.group(1)
    raise Exception('BBDown: no title found')


def get_video_info(bbdown_output) -> tuple:
    pattern = r'(?m)\d+\.( \[.+?\])( \[.+?\]){5}$\s+(.*?)$'
    match = re.search(pattern, bbdown_output)
    if match:
        return (match.group(1), match.group(3))
    raise Exception('BBDown: failed to get video info')


def get_audio_url(bbdown_output) -> str:
    pattern = r'(?m)\d+\. \[M4A\]( \[.+?\])+$\s+(.*?)$'
    result = re.search(pattern, bbdown_output)
    if result:
        return result.group(2)
    raise Exception('BBDown: no audio found')


def get_resolution(bbdown_output) -> str:
    pattern = r'(?m)\d+\.( \[(.+?)\]){2}( \[.+?\]){4}$\s+(.*?)$'
    result = re.search(pattern, bbdown_output)
    if result:
        return result.group(2)
    raise Exception('BBDown: no resolution found')


def get_bbdown_output(url) -> str:
    return os.popen(
        "BBDown '{}' --encoding-priority 'hevc,av1,avc' -info".format(
            url)).read()


def resolve(params: dict[str, str]) -> Video:
    url: str = params['url']
    output = get_bbdown_output(url)
    return Video(url, get_title(output), get_video_info(output),
                 get_audio_url(output), params['cid'], get_resolution(output))


def load_configuration() -> Configuration:
    # search common configuration path
    paths: list[str] = []

    # $XDG_CONFIG_HOME
    if 'XDG_CONFIG_HOME' in os.environ:
        paths.append(
            os.path.join(os.environ['XDG_CONFIG_HOME'], 'bmpv', 'config.json'))

    # $HOME/.config
    paths.append(
        os.path.join(os.environ['HOME'], '.config', 'bmpv', 'config.json'))

    # /etc
    paths.append(os.path.join('/etc', 'bmpv', 'config.json'))

    for path in paths:
        if os.path.exists(path):
            return parse_configuration(path)

    return Configuration(font='serif',
                         font_size=36,
                         danmaku_opacity=0.6,
                         marquee_duration=10,
                         still_duration=10,
                         size='2560x1440')


# bmpv:///?url=www.bilibili.com/video/av1&cid=12345
def main() -> None:
    print(sys.argv)
    try:
        resolve(parse_params(get_url())).play(load_configuration())
    except Exception as err:
        print(err.__repr__(), file=sys.stderr)


if __name__ == "__main__":
    main()
