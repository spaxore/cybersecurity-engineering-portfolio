# Image Metadata and Privacy Toolkit

A local-first Python GUI and command-line toolkit for inspecting image metadata, extracting embedded GPS coordinates, opening location maps, and creating clean copies without image metadata.

> Analyze locally. Understand what an image reveals. Remove sensitive metadata before sharing.

## Overview

Digital images can contain metadata such as camera model, capture time, and GPS coordinates. This project provides a simple workflow for inspecting that information and creating a privacy-safe copy of an image without the embedded metadata.

The project is designed for local analysis. Images are not uploaded to an external service by the application.

## Features

The graphical interface allows you to browse for a JPG, JPEG, or TIFF image, view its camera and capture information, detect embedded GPS coordinates, open the location in an interactive HTML map, and save a clean copy with metadata removed.

The command-line interface provides the same core extraction and map workflow for terminal-based use. The source code separates EXIF extraction, GPS parsing, map rendering, and metadata scrubbing into independent modules.

## Project structure

```
05-image-metadata-extractor/
├── gui.py
├── cli.py
├── requirements.txt
├── src/
│   ├── extractor.py
│   ├── gps_parser.py
│   ├── map_renderer.py
│   └── scrubber.py
└── tests/
    └── test_gps_parser.py
```

## Installation

Clone or download the portfolio repository, then enter the project directory:

```
cd 05-image-metadata-extractor
python -m pip install -r requirements.txt
```

## Run the GUI

```
python gui.py
```

Use **Browse for photo** to select an original image. If GPS metadata is available, the interface enables **Open map**. Use **Save clean copy** to create a new image without the original metadata.

## Run the CLI

```
python cli.py path\to\image.jpg
```

For a file path containing spaces, use quotes:

```
python cli.py "C:\Users\ikbal\Pictures\travel-photo.jpg"
```

The generated map is saved as `location_map.html` in the current project directory and opened in the default browser.

## Metadata scrubbing

The scrubber creates a new image from the source pixels instead of simply re-saving the original file. This is intended to prevent EXIF metadata such as GPS coordinates, camera model, and capture time from being copied into the clean output.

The visible pixels are not anonymized. Metadata scrubbing does not remove faces, signs, landmarks, documents, or other information visible inside the image itself.

## Testing

Run the GPS parser tests with:

```
python -m pytest
```

## Limitations

The current release focuses on JPG, JPEG, and TIFF images. Metadata may already have been removed from images downloaded from social media, messaging platforms, or search-engine previews. A missing GPS result does not prove that the original camera file never contained location data.

The map requires an internet connection when the browser loads map tiles. The image analysis itself remains local.

## Responsible use

Use this software only with images you own or are authorized to inspect. Treat GPS coordinates and other metadata as potentially sensitive personal information. Do not publish or share extracted locations without appropriate permission.

## License

Add a license before public distribution. An MIT license is a practical default for a small educational software project, but choose the license that matches your intended use and contributions.