# CaptionBlocker [![CaptionBlocker](https://github.com/Serden-YilmazKose/CaptionBlocker/blob/main/src/icons/icons8-c-48.png)](https://github.com/Serden-YilmazKose/CaptionBlocker)
**Block or blur unnecessary captions and subtitles.**

# Purpose
Hard-coded captions and subtitles, when not needed, can decrease the viewing experience. This extension seeks to mitigate that problem by placing a black rectangle over the captions.

# Tools
The location and dimensions of the caption blocker are submitted by users, or detected automatically using server-side magic.

The following are the languages and tools used in the development of the project:
* JavaScript: Used to write the source code of the extension.
* Python: Used to build a server, using Flask, that handles GET and POST requests.
* MariaDB: Used to host the database of videos, insertions are made from the Python Flask server.

# Installation
Since this project hasn't been deployed, you will have to run everything locally, including the server. The following are some steps to get that working.
* Clone the repository by running:
```shell
git clone https://github.com/Serden-YilmazKose/CaptionBlocker.git
cd CaptionBlocker
```
* Install all Python dependencies:
```shell
pip install -r requirements.txt
```
* Run the server: Navigate to where you cloned the project repository, and run:
```shell
python3 server.py
```
* Log into your MariaDB server, the user and password must be root and pass, respectively:
```shell
mariadb -u root -p
Enter password: root
```
* Once logged into your MariaDB server, create a database labeled `caption_capper` (this will be changed later):
```shell
CREATE DATABASE caption_capper;
```
Finally, submit the following query:
```SQL
CREATE TABLE VIDEOS (
    website VARCHAR(50),
    video_id VARCHAR(50),
    x_cord INT,
    y_cord INT,
    length INT,
    height INT,
    x_res INT,
    y_res INT
);
```

The next steps will depend on what browser you are using. Currently, the extension only works on Firefox.
## Firefox
* Visit the [Firefox debugging page](about:debugging#/runtime/this-firefox): about:debugging#/runtime/this-firefox.
* Click on `Load Temporary Add-on`
* Navigate to the directory you cloned the project repository.
* Finally, open `manifest.json`, which is located in `src/`.
* Great! The extension should now be running.

# Note
As may be evident from the quality and structure of the code, not one line of this project was written by a generative artificial intelligence. Prior to this, I had nearly zero experience using JavaScript.

Icons downloaded from [icons8](https://icons8.com/icon/Hph7fH3f5brw/c-cute).
