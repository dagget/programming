#include<stdlib.h>
#include<string.h>
#include<stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/select.h>
#include <sys/time.h>
#include <sys/types.h>

#include <mcheck.h>

int main(int argc, char **argv) {

   mtrace();

   return 0;
}
