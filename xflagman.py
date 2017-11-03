import os, plistlib, glob, gzip

class XCActivityLog:

    def __init__(self, path):
        self.path = path

    def clangFlagsForFile(self, path):
        opened = gzip.open(self.path, 'rt', newline='\r')
        for line in opened.readlines():
            if path in line and "/XcodeDefault.xctoolchain" in line:
                for rline in line.split("\r"):
                    if path in rline and "/XcodeDefault.xctoolchain" in rline:
                        if rline.endswith(".o"):
                            yield rline.strip()
        opened.close()

class WorkingDir:

    def __init__(self):
        self.path = os.getcwd()

    def workspace(self):
        for f in  os.listdir(self.path):
            if f.endswith('.xcodeproj') or f.endswith('.xcworkspace'):
                return os.path.join(self.path, f)
        raise RuntimeError('Cannot find any .xcodeproj or .xcworkspace file in the current working directory. \n{}'.format(cwd))

class DerivedDir:

    def __init__(self, path):
        self.path = path

    def directoryForWorkspace(path, workspace):
        info = plistlib.readPlist(os.path.join(path, 'info.plist'))
        workspacePath = info['WorkspacePath']
        if workspace == workspacePath:
            return DerivedDir(path)
        else:
            raise RuntimeError('Cannot initialize derived dir of {} with {}'.format(workspacePath, workspace))

    def latestLogFile(self):
        logsDir = os.path.join(self.path, 'Logs/Build')
        pattern = os.path.join(logsDir, '*.xcactivitylog')
        logs = glob.glob(pattern)
        latest = max(logs, key=os.path.getctime)
        log = XCActivityLog(latest)
        return log

class XFlagman:

    def __init__(self):
        self.workspacePath = WorkingDir().workspace()

    def clangFlagsForFile(self, path):

        # Use the flags for .m for its .h
        if path.endswith('.h'):
            path = path[:-2] + '.m'

        # Find in .xcactivitylog file
        log = self.derivedDir().latestLogFile()
        strings = log.clangFlagsForFile(path)

        # ['flags string',]
        try: 
            flags = next(strings)
        except StopIteration: 
            raise RuntimeError('Cannot find any flag for file at path: \n{}'.format(path))
        flags = flags.split()

        # [path/to/clang, ..., -c, path/to/.m, -o, path/to/.o,]
        if not len(flags) >= 5:
            raise RuntimeError('Cannot find enough flags for file at path: \n{}'.format(path))
        flags = flags[1:-4]

        return flags

    def derivedDir(self):
        derivedDataDir = os.path.expanduser('~/Library/Developer/Xcode/DerivedData')
        workspaceName = os.path.basename(self.workspacePath).split('.')[0]
        for f in os.listdir(derivedDataDir):
            if f.startswith(workspaceName):
                dirPath = os.path.join(derivedDataDir, f)
                try:
                    return DerivedDir.directoryForWorkspace(dirPath, self.workspacePath)
                except RuntimeError:
                    continue
        raise RuntimeError('Cannot find derived direcotry for workspace file. {}'.format(self.workspacePath))

def main():
    import optparse
    p = optparse.OptionParser()
    p.add_option('--file', '-f', help="File for which parameters are searching for")

    options, arguments = p.parse_args()
    if not options.file:
        p.error("searching file path is required")

    # Check that file starts from backslash
    if not options.file.startswith("/"):
        p.error("Provide full path to the file")

    flags = XFlagman().clangFlagsForFile(options.file)

    from pprint import pprint
    pprint(flags)

if __name__ == '__main__':
    main()
