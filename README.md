# s3-md5

Get fast md5 hashes for an s3 file.

## installation

-   python 3.10

## how to use

You can use the tool as a command line argument. You can download the latest release from [here](https://github.com/sakibstark11/s3-md5-python/releases). You can also build the wheel file yourself by running the following command.

```sh
pip install ".[release]"
```

```sh
python setup.py bdist_wheel sdist
```

Which will generate a wheel file in the `dist` folder. Install it like any other wheel file.

```sh
pip install dist/s3_md5-1.0.0-py3-none-any.whl
```

And you should have the tool available to yourself from the terminal.

From the command line, run

```sh
s3-md5 <bucket_name> <file_name>
```

Or you can directly invoke the script by going into the `s3_md5` folder and running

```sh
python main.py <bucket_name> <file_name>
```

There are two _optional_ arguments that you may want to provide

-   `-w` or workers sets the number of python threads to use for downloading purposes, by default its set to the following equation `number of cpu cores * 2 - 1`
-   `-c` or chunk size in **bytes** sets the individual download size on each get request sent to s3, by default its set to `1000000`

## caveats

-   File size can not be smaller than the default chunk size of `1000000`, if yes, then the chunk size must be manually provided or it will raise an assertion error.
