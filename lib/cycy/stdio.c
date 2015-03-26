#include "cycy/stdio.h"

int puts(const char * string) {
    int i = 0;
    while (string[i] != 0) {
        putchar(string[i]);
        i = i + 1;
    }
    putchar('\n');
    return i + 1;
}
