#include<stdio.h>
#include <mcheck.h>
#include "inthash.h"

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

int hinsert(void)
{
   return 0;
}

int hremove(void)
{
   return 0;
}

int hlookup(void)
{
   return 0;
}


//   mtrace();
