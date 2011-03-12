#include<stdio.h>
#include <mcheck.h>
#include "inthash.h"

/* Internal hashtable
 *
 * This is an example implementation of a so called 'closed hash'. The elements
 * are placed within the hashtable itself, rather than referenced through linked
 * lists.
 */

static int hash(int key)
{
	int position = key % HASHSIZ;

	if ( 0 <= position <= HASHSIZ)
		return position;
	else
		return -1;
}

static int rehash(int position, int key)
{
	return position++;
}

int hinsert(int key, int value)
{
	int position = 0;
	int val      = 0;

	/* item is already there */
	if (hlookup(key, &val) == 0)
		if (val == value)
			return 0;
		else
			return -1;

	/* seek free position and use it */
	if ((position = hash(key)) != -1) {
		if (hashtable[position].deleted == 1){
			hashtable[position].deleted = 0;
			hashtable[position].value = value;
			return 0;
		}
		else {
			while ((position = rehash(position, key)) != -1) {
				if (hashtable[position].deleted == 1){
					hashtable[position].deleted = 0;
					hashtable[position].value = value;
					return 0;
				}
			}
		}

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

	if ((position = hash(key)) != -1) {
		if (hashtable[position].key == key){
			if (hashtable[position].deleted)
				return -1;
			else {
				*value = hashtable[position].value;
				return 0;
			}
		}
		else
			while ((position = rehash(position, key)) != -1) {
				if (hashtable[position].key == key) {
					if (hashtable[position].deleted)
						return -1;
					else {
						*value = hashtable[position].value;
						return 0;
					}
				}
			}
	}

	return -1;
}

//   mtrace();
