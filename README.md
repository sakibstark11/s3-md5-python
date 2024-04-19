# s3-md5

Get fast md5 hashes for an s3 file. This works by utilizing a process to fetch chunks into by doing them in threads while having another process consuming the shared dictionary. Given MD5 hashes need to be processed sequentially, it keeps looking for the expected chunk to ensure the order is right.

## Requirements

-   python 3.10

## Usage

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

Or you can directly invoke the script by running

```sh
python s3_md5/main.py <bucket_name> <file_name>
```

### Arguments

There are two _optional_ arguments that you may want to provide

-   `-c` or chunk size in **bytes** sets the individual download size on each get request sent to s3, by default it will use [speedtest-cli](https://pypi.org/project/speedtest-cli/) to determine the network speed.
-   `-b` or block size to determine the number of maximum concurrent requests sent to s3 to protect against rate limiting. By default it is set to **10**. Please change this as this is related to your aws account s3 api rate limits.

### Example

for a file size of `1048576000` bytes
on a 250 mpbs bandwidth
on a macbook m1 8 core cpu
a chunk size of `4000000` works the best as it completes it within ~100 seconds
