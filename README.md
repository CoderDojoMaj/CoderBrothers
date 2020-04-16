# CoderBrothers

# Install
## Install Python3 for your OS:  
- **Windows**: [64 bit installer](https://www.python.org/ftp/python/3.8.2/python-3.8.2-amd64.exe) ([32 bit installer](https://www.python.org/ftp/python/3.8.2/python-3.8.2.exe))
- **Mac OS X**: [Installer](https://www.python.org/ftp/python/3.8.2/python-3.8.2-macosx10.9.pkg)
- **Linux**: Install python3.8 with the package manager
    - Debian based (Ubuntu / Mint): `sudo apt-get install python3.8`

## Install libraries for the project
```sh
python3.8 -m pip install -r requirements.txt
```

# Run

First, set up the environvemnt variable in your terminal
## Loading the environment variables
### Linux / MacOS (Bash / Zsh / Fish)
```bash
export FLASK_APP=server.py
```

### Windows (CMD)

```batchfile
set FLASK_APP=server.py
```

### Windows (Powershell)

```powershell
$env:FLASK_APP = "server.py"
```

## Actually running the server
```sh
flask run -p 8080
```

Go to http://localhost:8080 to see the page
