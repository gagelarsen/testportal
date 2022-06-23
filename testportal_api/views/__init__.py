from .bug_verification_views import BugVerificationDetail, BugVerificationList
from .product_views import ProductDetail, ProductList
from .suite_views import duplicate_suite, SuiteDetail, SuiteList  # NOQA: F401
from .tag_views import TagDetail, TagList  # NOQA: F401
from .test_case_views import delete_test_case, upload_multiple_test_cases, TestCaseDetail  # NOQA: F401
from .test_category_views import TestCategoryDetail, TestCategoryList  # NOQA: F401
from .test_plan_views import TestPlanDetail, TestPlanList  # NOQA: F401
from .test_result_views import delete_test_results_for_date_and_suite, upload_test_results, TestResultDetail, TestResultList, \
    copy_result_to_latest  # NOQA: F401
from .test_subcategory_views import TestSubcategoryDetail, TestSubcategoryList  # NOQA: F401
