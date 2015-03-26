#include "cycy/stdio.h"

int puts(const char * string) {
    int i = 0;
    while (string[i] != NULL) {
        putchar(string[i++]);
    }
    putc('\n');
    return i + 1;
}
