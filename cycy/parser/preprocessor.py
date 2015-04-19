from rpython.rlib.rsre.rsre_re import match as re_match

from cycy.exceptions import CyCyError


class PreprocessorError(CyCyError):
    pass


class IncludeNotFound(PreprocessorError):
    def __init__(self, path, searched):
        self.path = path
        self.searched = searched

    def __str__(self):
        return "Could not locate '%s'.\nSearched in: %s" % (
            self.path, self.searched,
        )


def preprocess_file(file_path, environment):
    source_file = environment.include(file_path)
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
