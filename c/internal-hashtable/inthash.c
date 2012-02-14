#include<stdio.h>
#include <mcheck.h>
#include "inthash.h"

/* Internal hashtable
 *
 * This is an example implementation of a so called 'closed hash'. The elements
 * are placed within the hashtable itself, rather than referenced through linked
 * lists.
 */

static void printhash(void)
{
	int i;

	for(i = 0; i < HASHSIZ; i++){
		printf("Elem %d\n", i);
		printf("\tKey %d\n", hashtable[i].key);
		printf("\tVal %d\n", hashtable[i].value);
		printf("\tDel %d\n", hashtable[i].deleted);
	}
}

static int hash(int key)
{
	int position = key % HASHSIZ;

	if ( 0 <= position < HASHSIZ)
		return position;
	else
		return -1;
}

static int rehash(int position)
{
	return ++position;
}

static int search_item_with_key(int key)
{
	int position = -1;
	int slots = 0;

	if((position = hash(key)) >= 0){
		if ((hashtable[position].key == key) && (!hashtable[position].deleted)) {
			return position;
		} else {
			for(slots = 0; slots < HASHSIZ; slots++){
				position = rehash(position);
				if ((hashtable[position].key == key) && (!hashtable[position].deleted)) {
					return position;
				}
			}
		}
	}

	return -1;
}

static int search_for_empty_slot(int key)
{
	int position = -1;
	int slots = 0;

	if((position = hash(key)) >= 0){
		if((hashtable[position].key == -1) || (hashtable[position].deleted))
			return position; 
		else {
			for(slots = 0; slots < HASHSIZ; slots++){
				position = rehash(position);
				printf("mhfm position: %d\n", position);
				if((hashtable[position].key == -1) || (hashtable[position].deleted))
					return position;
			}
		}
	}

	return -1;
}

int hinsert(int key, int value)
{
	int position = -1;
	int val      = -1;

	/* item is already there */
	if((position = search_item_with_key(key)) != -1){
		hashtable[position].value = value;
		return 0;
	} else {
		printf("need to find free spot\n");
		if((position = search_for_empty_slot(key)) != -1){
			printf("found it: %d\n", position);
			hashtable[position].key = key;
			hashtable[position].value = value;
			hashtable[position].deleted = 0;
			return 0;
		} else {
			printf("could not find empty slot\n");
			return -1;
		}
	}

	return -1;
}

int hremove(int key)
{
	int position = -1;

	if((position = search_item_with_key(key)) != -1){
		hashtable[position].deleted = 1;
		return 0;
	}
	return -1;
}

int hlookup(int key, int* value)
{
	int position = -1;
	if((position = search_item_with_key(key)) != -1){
		*value = hashtable[position].value;
		return 0;
	}

	return -1;
}

//   mtrace();
