from rpython.rlib.streamio import open_file_as_stream
from rpython.rlib.rsre.rsre_re import match as re_match

def preprocess_file(file_path):
    source_file = open_file_as_stream(file_path)
    data = source_file.readall()
    source_file.close()
    return preprocess(data)

def preprocess(source):
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
            file_path = match.group(0)
            processed.extend(preprocess_file(file_path).split("\n"))
        else:
            processed.append(line)

    return "\n".join(processed)
