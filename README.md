# xcode_complete_me
Scripts to extract compilation flags to be used in YouCompleteMe from Xcode build logs 

## Usage

In `/path/to/the/directory/your.xcodeproj/or/your.xcworkspace/locates/.ycm_extra_conf.py`:

```python
import xflagman

flagman = xflagman.XFlagman()
def FlagsForFile( filename, **kwargs ):
    flags = flagman.clangFlagsForFile(filename)
    return { 'flags': flags, 'do_cache': True }

```
