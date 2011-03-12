#define HASHSIZ 20

struct item {
	int key;
	int value;
	short deleted;
};

static struct item hashtable[HASHSIZ];

int hinsert(int key, int value);
int hlookup(int key, int *value);
int hremove(int key);
