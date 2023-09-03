### How to run the desktop application
```
$ pip install -r requirements.txt
$ python lazy_typewriter.py
```

### How to pack an executable

[Source](https://flet.dev/docs/guides/python/packaging-desktop-app/#using-ci-for-multi-platform-packaging)

```
$ flet pack .\lazy_typewriter.py --icon .\assets\favicon.png
```