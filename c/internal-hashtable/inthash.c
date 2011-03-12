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
		return position;
	else
		return -1;
}

static int hrehash(int position, int key)
{
	return position++;
}

int hinsert(int key, int value)
{
	int retval = 0;
	int val    = 0;

	/* item is already there */
	if ((retval = hlookup(key, &val)) == 1)
		return -1;

	/* position is free, use it */
	if (((hitem = hhash(key)) != NULL) && (hitem->deleted == 1)) {
		hitem->val     = value;
		hitem->deleted = 0;
		return 0;
	}

	/* seek a free position */
	while (rehash())
	{
	}

	return -1;
}

int hremove(int key)
{
	return 0;
}

int hlookup(int key, int *value)
{
	int position = -1;

	if (value == NULL)
		return -1;
	else
		if ((position = hash(key)) == -1)
			return -1;

	if (hashtable[position].key == key){
		if (hashtable[position].deleted)
			return -1;
		else {
			*value = hashtable[position].value;
			return 0;
		}
	}
	else
		while ((position = rehash(key)) != -1) {
			if (hashtable[position].key == key) {
				if (hashtable[position].deleted)
					return -1;
				else {
					*value = hashtable[position].value;
					return 0;
				}
			}
		}

	return -1;
}

//   mtrace();
