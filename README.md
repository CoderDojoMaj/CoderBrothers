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

## Install MySQL
- **Windows**: [Installer](https://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-community-8.0.19.0.msi)
- **Mac OS X**: [Installer](https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-8.0.19-macos10.15-x86_64.dmg)
- **Linux**: Install MySQL with the package manager
    - Debian based (Ubuntu / Mint): `sudo apt-get install mysql-server`
    `mysql_secure_installation` To configure root password

## Setup the database
execute this command on the project directory  
`mysql -uroot -p` then put your root password  
`source setup.sql;` to setup everything  

### Sidenote
Changing the coderbrothers user password is highly recomended, but for just testing it isn't necessary.
To do it, the password on the mysql user has to be updated, as well as the password on the `config.json` file

# Run

First, set up the environvemnt variable in your terminal
## Loading the environment variables
### Linux / MacOS (Bash / Zsh / Fish)
```bash
export FLASK_APP=server.py
export FLASK_ENV=development
```

### Windows (CMD)

```batchfile
set FLASK_APP=server.py
set FLASK_ENV=development
```

### Windows (Powershell)

```powershell
$env:FLASK_APP = "server.py"
$env:FLASK_ENV = "development"
```

## Actually running the server
```sh
flask run -p 8080
```

Go to http://localhost:8080 to see the page

***

## Sidenote
### On MacOS & Linux, `start.sh` can be run to do everything
First give it permissions to run with
```bash
chmod +x start.sh
```
And then just run it with
```bash
./start.sh
```
### On Windows, `start.bat` can be run to do everything
(Not sure) Double click the file and it should open a command prompt with the flask developmeent server