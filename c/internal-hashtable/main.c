#include <stdio.h>
#include <string.h>
#include <CUnit/Basic.h>
#include "inthash.h"

int init_suite1(void)
{
	return 0;
}

int clean_suite1(void)
{
	return 0;
}

void testhinsert(void)
{
	CU_ASSERT(0 == hinsert(1,1));
	CU_ASSERT(0 == hinsert(21,2));
	CU_ASSERT(0 == hinsert(31,3));
	CU_ASSERT(0 == hinsert(41,4));
}

void testhlookup(void)
{
	int value = -1;
	CU_ASSERT(0 == hlookup(1, &value));
	CU_ASSERT(value == 1);

	CU_ASSERT(0 == hlookup(21, &value));
	CU_ASSERT(value == 2);

	CU_ASSERT(0 == hlookup(31, &value));
	CU_ASSERT(value == 3);

	CU_ASSERT(0 == hlookup(41, &value));
	CU_ASSERT(value == 4);
}

void testhremove(void)
{
	CU_ASSERT(0 == hremove(1));
	CU_ASSERT(0 == hremove(21));
	CU_ASSERT(0 == hremove(31));
	CU_ASSERT(0 == hremove(41));
}

void testhinsertremove(void)
{
	CU_ASSERT(0 == hinsert(1,5));
	CU_ASSERT(0 == hremove(1));
}

void testmanyhinserts(void)
{
	int i = 0;
	for (i = 0; i < (HASHSIZ); i++) {
		CU_ASSERT(0 == hinsert(i,10));
	}
	printhash();

	CU_ASSERT(-1 == hinsert(HASHSIZ,10));
}

int main(int argc, char **argv)
{
	CU_pSuite pSuite = NULL;

	/* initialize the CUnit test registry */
	if (CUE_SUCCESS != CU_initialize_registry())
		return CU_get_error();

	/* add a suite to the registry */
	pSuite = CU_add_suite("Suite_1", init_suite1, clean_suite1);
	if (NULL == pSuite) {
		CU_cleanup_registry();
		return CU_get_error();
	}

	/* add the tests to the suite */
	if ((NULL == CU_add_test(pSuite, "test of hinsert()", testhinsert)) ||
			(NULL == CU_add_test(pSuite, "test of hlookup()", testhlookup)) ||
			(NULL == CU_add_test(pSuite, "test of hremove()", testhremove)) ||
			(NULL == CU_add_test(pSuite, "test of hinsert() after hremove()", testhinsertremove)) ||
			(NULL == CU_add_test(pSuite, "test of too many hinsert()", testmanyhinserts)))
	{
		CU_cleanup_registry();
		return CU_get_error();
	}

	/* Run all tests using the CUnit Basic interface */
	CU_basic_set_mode(CU_BRM_VERBOSE);
	CU_basic_run_tests();
	CU_cleanup_registry();

	return CU_get_error();
}
