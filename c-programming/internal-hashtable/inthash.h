#define HASHSIZ 20

struct item {
   int val;
   short deleted;
};

int hinsert(int key, int value);
struct item *hlookup(int key);
int hremove(int key);
