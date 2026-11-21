REM launch a local server for hosting the gamedata overlay html
cd HTML_Server
python3 -m http.server 8080 --bind 0.0.0.0
