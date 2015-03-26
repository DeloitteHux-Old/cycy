import os

from rpython.rlib.streamio import open_file_as_stream
from rpython.rlib.rsre.rsre_re import match as re_match

def find_file(file_path, environment=None):
    if os.path.exists(file_path):
        return file_path
    if environment:
        for include_path in environment.include_paths:
            path = os.path.join(include_path, file_path)
            if os.path.exists(path):
                return path

    raise OSError("No such file or directory: '%s'" % file_path)

def preprocess_file(file_path, environment=None):
    file_path = find_file(file_path, environment)
    source_file = open_file_as_stream(file_path)
    data = source_file.readall()
    source_file.close()
    return preprocess(data)

def preprocess(source, environment=None):
    """
    Run the preprocessor on a stream of source. Eventually this should take
    a stream of pptokens and emit a stream of tokens. For now, we only support
    #include statements and we support them by replacing the #include
    by the contents of the file. We also don't make any distinction between
    #include "..." and #include <...>.
    """
    processed = []
    for line in source.split("\n"):
        match = re_match("\s*#include\s+[\"<](.*)[\">]\s*", line)
        if match is not None:
            file_path = match.group(1)
            processed.extend(
                preprocess_file(file_path, environment).split("\n")
            )
        else:
            processed.append(line)

    return "\n".join(processed)
