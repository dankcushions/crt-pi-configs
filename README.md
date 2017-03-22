Creates cfg files for optimum crt-pi shader appearence. Works only for lr-fbalpha (FBA 0.2.97.39) and lr-mame2003 (MAME 0.78)

Params are:
* core (currently, mame2003 or fbalpha)
* screen width (eg 1920)
* screen height (eg 1080)

Example usage:
Clone into a directory, and then navigate to that directory in your command prompt, and then:
```python crt-pi-configs.py mame2003 1920 1080```

It will generate the cfgs and zip files containing the same in the root.

Requires Python 3.5.2 or higher (or at least, it doens't work properly on 2.7)