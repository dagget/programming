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
}

void testhlookup(void)
{
	int value = -1;
	CU_ASSERT(0 == hlookup(1, &value));
	CU_ASSERT(value == 1);
}

void testhremove(void)
{
	CU_ASSERT(0 == hremove(1));
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
			(NULL == CU_add_test(pSuite, "test of hremove()", testhremove)))
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
