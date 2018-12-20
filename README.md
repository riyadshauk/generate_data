# Generate Data
## A simple, ad hoc script (Python 2 & 3) to generate random CLOB data in (a specified table of) an Oracle SQL database.

If you'd like to use a more mature and feature-rich application, do check out the free and open-source data-generating software called [Swing Bench](http://www.dominicgiles.com/swingbench.html), and also [Data Generator](http://www.dominicgiles.com/datagenerator.html), both written in Java by [Dominic Giles](http://www.dominicgiles.com/index.html). Swing Bench actually works pretty well for generating and comitting lots of data, and it seems to be pretty fast, from what I've seen.

This script is very simple (easy to understand, not feature-rich) and one-off (spent 2-3 days writing and manually testing it with a database running on an Oracle VM instance in OCI), and written in Python 3, in comparison.

Table of contents
=================

<!--ts-->
   * [Setup](#setup)
      * [Environment & Dependency Info](#info-on-setting-up-the-environment-one-dependency--as-needed)
      * [Installing Python3.6 with pip3.6](#installing-python36-with-pip36)
      * [Files to Modify](#files-to-modify)
        * [What does this do?](#what-does-this-do)
   * [Run the Script](#run-the-script)
      * [How to Execute the Script](#how-to-execute-the-script)
      * [Example Script Execution using tmux](#example-script-execution-using-tmux)
<!--te-->

## Setup

### Info on setting up the environment (one dependency), as needed:

This Python script relies on the cx_Oracle module. For installation instructions, see: https://oracle.github.io/odpi/doc/installation.html#odpi-c-installation .


For a general overview of cx_Oracle: https://cx-oracle.readthedocs.io/en/latest/ .

Also, make sure pip is installed (see below for more info).

### Installing Python3.6 with pip3.6

Do note: If you'd rather just use Python 2, I've also supplied a Python 2-compatible version of this script.

Here's an easy way to get python3.6, including pip3.6 (for Python 3, cx_Oracle 7.0 is only supported for version 3.5-3.7), for Oracle 6 / Centos 6 / RHEL.

As described here, https://www.rosehosting.com/blog/how-to-install-python-3-6-4-on-centos-7/, we will install pip3.6 for Oracle Linux 6.9 as follows (replacing centos7 with centos6, since that's what we have on Oracle Linux 6.9):

```
$ sudo yum install -y https://centos6.iuscommunity.org/ius-release.rpm
$ sudo yum update
$ sudo yum install -y python36u python36u-libs python36u-devel python36u-pip
$ sudo pip3.6 install --upgrade pip
```

If you desire to stick with Python 2, instead, you still need pip to be installed: https://www.godaddy.com/help/how-to-install-python-pip-on-centos-12367 .

### Files to Modify

Before running the script, make any required edits to the end of the file by commenting / uncommenting the line(s) in `generate_data.py`, as desired:

```
executeQueryBatch('test_clobs', int(pow(2, 22)), 10)        # 4 MiB total
# executeQueryBatch('test_clobs', int(pow(2, 33)), 6)       # 8 GiB total
# executeQueryBatch('test_clobs', int(pow(2, 36)), 6)       # 64 GiB total
# executeQueryBatch('test_clobs', int(pow(2, 37)), 6)       # 128 GiB total
# executeQueryBatch('test_clobs', int(pow(2, 38)), 6)       # 256 GiB total
```

Also, you will need to provide the credentials needed to connect to your possibly remote Oracle database.

```
$ cp credentials_template.py credentials.py
```

Correctly modify `credentials.py`, as that is what allows Python to connect to your database.

Tip: Running this script on the same machine as the DB is on may yield better performance.

#### What does this do?
This creates a table named 'test_clobs' if it doesn't yet exist, then inserts the specified number of bytes as a sequence of randomly generated characters into that table in the database.

## Run the Script

### How to Execute the Script

To execute the script, simply run the following:

(After correctly modifying `credentials_template.py` and renaming it to `credentials.py`, as described above)

```
$ sudo pip3 install --user -r requirements.txt
$ sh run_generate_data.sh   # this will create a log file per invocation, in `./logs`
```

Do note: If you'd like to run the script with Python 2 instead, you can do so by uncommenting the corresponding line in `run_generate_data.sh`, and commenting out the Python 3 invocation. Then, very similarly, run the script as follows:

```
$ sudo pip install --user -r requirements.txt # assuming pip points to your pip2 installation
$ sh run_generate_data.sh  # after uncommenting/commenting the relevant two lines
```

### Example Script Execution using tmux

It's recommended to run this using tmux sessions, if running remotely, so that the process stays alive even after you log out or terminate your network connection. For example:

```
$ # preferably, run this in a tmux session, since it takes a lot of time
$ sudo yum install -y tmux
$ tmux new -s generateDBData
$ sh run_generate_data.sh
$ # type "ctrl+b" then "d" to detach the tmux (do it)
$ tmux new -s logOfGenerateScript
$ # assumming the script is unchanged and creates a .txt file using a date timestamp as the filename, the following
$ # should open a live-updating stream of logs in this tmux session
$ echo "logs/\"$(ls -ltr logs | head -n 2 | grep txt | awk '{print $9" "$10" "$11" "$12" "$13" "$14}')\"" | xargs tail -f
$ # "ctrl+b" then "d" to detach this tmux session (do it; it'll continue in the background)
$ # have fun doing other stuff... 
$ # attach back to a tmux:
$ tmux a -t log # it assumes the rest of the session name, like tab-complete
```