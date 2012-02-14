#define HASHSIZ 20

struct item {
	int key;
	int value;
	short deleted;
};

// Only positive keys allowed & not deleted by default
static struct item hashtable[HASHSIZ] = { { -1, -1, 0 },
				  	  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 },
					  { -1, -1, 0 } };

int hinsert(int key, int value);
int hlookup(int key, int* value);
int hremove(int key);
void printhash(void);
