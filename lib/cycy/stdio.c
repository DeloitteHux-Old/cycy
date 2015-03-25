#include "cycy/stdio.h"

int puts(const char * string) {
    int i = 0;
    while (string[i] != NULL) {
        putc(string[i++]);
    }
    putc('\n');
    return i + 1;
}
