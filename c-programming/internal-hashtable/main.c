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

/* Internal hashtable
 *
 * This is an example implementation of a so called 'closed hash'. The elements
 * are placed within the hashtable itself, rather than referenced through linked
 * lists.
 */

#define HASHSIZ 20

struct item {
   int val;
};

static struct item hashtable[HASHSIZ];

int insert()
{
   return 0;
}

int delete()
{
   return 0;
}

int lookup()
{
   return 0;
}


//   mtrace();
