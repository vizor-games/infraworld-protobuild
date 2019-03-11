Vizor Infraworld Protobuild
===========================

Protobuild is an utility helping you to keep your protobuf and gRPC-related code wrappers in a consistent
state for all programming languages you're using across your projects. Write a YML configuration file
once, and then re-run this utility each time your `*.proto` file(s) changes, and your language wrappers will
always be in mint condition :tropical_drink:

Usage
=====

You're required to have a **python>=3.6** installed ([See how to install Python for Windows](https://www.howtogeek.com/197947/how-to-install-python-on-windows/)) to be able to run the program.

Since protobuild has some dependent packages, you can install them by simply running this in the protobuild root directory:
>`pip install -r requirements.txt` (of course, you can use [virtual environment](https://virtualenv.pypa.io/en/stable/) as well)

Then you can run the program with:
>`python main.py   #sometimes there should be 'python3' instead of 'python'`

You can provide your options using a configuration YML file and then override them using command line options.


* `proto_root` **(string)** - Folder being searched for *.proto files. Path can be either absolute, or relative to the working directory.
* `gen_root` **(string)** - Folder, where generated files will be put. Path can be either absolute, or relative to the working directory.
* `programs_root` **(string)** Path to the protoc and grpc plugins, being used for code generation. Since these binaries are platform-dependent,
the provided path does not include the 'platform' folder suffix, which is: 'Mac' for Mac OS, 'Linux' for any compatible linux distributive,
'Win64' for x64 windows distributive. You may build these programs using build scripts from the Infraworld Runtime as well as use installed programs.
Path can be either absolute, or relative to the working directory.
* `languages` **(array)** - Languages to generate wrappers for. Supported by protoc: [cpp, csharp, js, objc, php, python, ruby],
 you may add additional plugins for extra languages.
* `extensions` **(array)** - Possible extensions of proto files.
* `protoc_options` **(array)** - Possible add optional flags for protoc. 
* `protoc_options_go` **(array)** - Possible add optional flags for protoc for Go. 

*Note that boolean options might be overriden with environment variables*

* `force` **(boolean)** - Regenerate all (yes) or just changes (no).
* `transport` **(boolean)** - Generate GRPC transport code for proto-buffers (yes), or just proto-buffers (no).
* `verbose` **(boolean)** - Do verbose output of anything (yes) or be silent (no).
* `porcelain` **(boolean)** - Show error messages gently (yes) or as full stack traces (no).

Debugging
=========

Since Protobuild is an open source software, you may want to debug it or add some extra functionality.
You can import it to any Python IDE, a PyCharm for example.

Contribution
============

Please feel free to report known bugs, propose new features and improve tests using Github's pull request system.
Thank you very much for contributing into free software.