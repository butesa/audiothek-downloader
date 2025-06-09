This script can download mp3s and covers from ARD audiothek.
This project is a [Fork](https://github.com/Leetcore/audiothek-downloader).

# Installation
```bash
git clone "https://github.com/Schluggi/audiothek-downloader.git"
cd audiothek-downloader
python3 -m venv venv
source venv/bin/activate
pip3 install -r requierements.in
```

# Usage

``` bash
python3 audiothek.py \
--url 'https://www.ardaudiothek.de/sendung/grimms-maerchen-und-verbrechen/13308785/' \
--directory ./output \
--group-episodes \ 
--square-images
```

## Arguments

| Argument           | Short | Type   | Default  | Required | Description                                                         |
|--------------------|-------|--------|----------|----------|---------------------------------------------------------------------|
| `--url`            | `-u`  | `str`  | -        | Yes      | Insert Audiothek URL (e.g. https://www.ardaudiothek.de/sendung/...) |
| `--directory`      | `-f`  | `str`  | `output` | No       | Directory to save all MP3s                                          |
| `--square-images`  | `-s`  | `bool` | `False`  | No       | Download images in 1:1 aspect ratio instead of widescreen           |
| `--group-episodes` | `-g`  | `bool` | `False`  | No       | Group episodes into their own subdirectories                        |
