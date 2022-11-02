**`Documentation`** |
------------------- |
This library was developed by Telops to help customer post-process the data acquired with 
Telops's infrared cameras.
More details and documentation about the library's functions are provided in the folder documentation. 


## Install

To install the library:

```
$ pip install TelopsToolbox-0.0.1-py2.py3-none-any.whl
```

#### Try your first program
```shell
$ python
```

```python
>>> from TelopsToolbox.hcc.readIRCam import read_ircam
>>> data, header, _,_= read_ircam('D:/Demo Data/Lighter.hcc', frames=list(range(0, 50)))
>>> frame = data[0]
```

For more examples, see the TelopsToolbox_examples.py file.