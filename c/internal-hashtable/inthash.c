#include<stdio.h>
#include <mcheck.h>
#include "inthash.h"

/* Internal hashtable
 *
 * This is an example implementation of a so called 'closed hash'. The elements
 * are placed within the hashtable itself, rather than referenced through linked
 * lists.
 */

static struct item hashtable[HASHSIZ];
static int hhash(int key)
{
   int position = key % HASHSIZ;

   if ( 0 <= position <= HASHSIZ)
      return &hashtable[key % HASHSIZ];
   else
      return NULL;
}

static int hrehash(int position, int key)
{
   return position++;
}

int hinsert(int key, int value)
{
   struct item *hitem = NULL;

   /* item is already there */
   if ((hitem = hlookup(key)) != NULL)
      return -1;

   /* position is free, use it */
   if (((hitem = hhash(key)) != NULL) && (hitem->deleted == 1)) {
      hitem->val     = value;
      hitem->deleted = 0;
      return 0;
   }

   /* seek a free position */
   while (rehash()
   
   return -1;
}

int hremove(int key)
{
   return 0;
}

struct item *hlookup(int key)
{
   return NULL;
}

//   mtrace();
