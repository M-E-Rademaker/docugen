"""
Manual test script for DocGenerator.

This script demonstrates how to use the DocGenerator class
and tests its functionality with sample code.

Run with: python test_generator_manual.py

Note: Requires ANTHROPIC_API_KEY environment variable to be set.
"""

from pathlib import Path
from docugen.core.doc_generator import DocGenerator, APIKeyMissingError, DocGeneratorError


def test_api_key_handling():
    """Test that API key error handling works correctly."""
    print("\n" + "="*60)
    print("TEST 1: API Key Handling")
    print("="*60)

    try:
        # This should raise APIKeyMissingError if no key is set
        generator = DocGenerator()
        print("✓ API key found and client initialized successfully")
        print(f"  Using model: {generator.model}")
    except APIKeyMissingError as e:
        print(f"✗ API key missing (expected if ANTHROPIC_API_KEY not set)")
        print(f"  Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    return True


def test_python_generation():
    """Test Python documentation generation."""
    print("\n" + "="*60)
    print("TEST 2: Python Documentation Generation")
    print("="*60)

    sample_python_code = """
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count if count > 0 else 0
"""

    try:
        generator = DocGenerator()
        file_path = Path("sample.py")

        print(f"\nGenerating documentation for Python code...")
        print(f"Code:\n{sample_python_code}")

        docs = generator.generate(file_path, sample_python_code)

        print(f"\nGenerated Documentation:")
        print("-" * 60)
        print(docs)
        print("-" * 60)
        print("\n✓ Python documentation generated successfully")

        return True

    except APIKeyMissingError as e:
        print(f"✗ Cannot test without API key: {e}")
        return False
    except DocGeneratorError as e:
        print(f"✗ Documentation generation failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sql_generation():
    """Test SQL documentation generation."""
    print("\n" + "="*60)
    print("TEST 3: SQL Documentation Generation")
    print("="*60)

    sample_sql_code = """
CREATE OR REPLACE FUNCTION get_user_orders(user_id INTEGER)
RETURNS TABLE(order_id INTEGER, order_date DATE, total DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT id, created_at, total_amount
    FROM orders
    WHERE customer_id = user_id
    ORDER BY created_at DESC;
END;
$$ LANGUAGE plpgsql;
"""

    try:
        generator = DocGenerator()
        file_path = Path("sample.sql")

        print(f"\nGenerating documentation for SQL code...")
        print(f"Code:\n{sample_sql_code}")

        docs = generator.generate(file_path, sample_sql_code)

        print(f"\nGenerated Documentation:")
        print("-" * 60)
        print(docs)
        print("-" * 60)
        print("\n✓ SQL documentation generated successfully")

        return True

    except APIKeyMissingError as e:
        print(f"✗ Cannot test without API key: {e}")
        return False
    except DocGeneratorError as e:
        print(f"✗ Documentation generation failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_r_generation():
    """Test R documentation generation."""
    print("\n" + "="*60)
    print("TEST 4: R Documentation Generation")
    print("="*60)

    sample_r_code = """
calculate_mean <- function(x, na.rm = TRUE) {
    if (!is.numeric(x)) {
        stop("Input must be numeric")
    }
    sum(x, na.rm = na.rm) / length(x[!is.na(x)])
}
"""

    try:
        generator = DocGenerator()
        file_path = Path("sample.r")

        print(f"\nGenerating documentation for R code...")
        print(f"Code:\n{sample_r_code}")

        docs = generator.generate(file_path, sample_r_code)

        print(f"\nGenerated Documentation:")
        print("-" * 60)
        print(docs)
        print("-" * 60)
        print("\n✓ R documentation generated successfully")

        return True

    except APIKeyMissingError as e:
        print(f"✗ Cannot test without API key: {e}")
        return False
    except DocGeneratorError as e:
        print(f"✗ Documentation generation failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_update_documentation():
    """Test updating existing documentation."""
    print("\n" + "="*60)
    print("TEST 5: Update Existing Documentation")
    print("="*60)

    existing_doc = {
        'content': '"""Simple function."""',
        'type': 'docstring'
    }

    sample_code = """
def add_numbers(a, b):
    return a + b
"""

    try:
        generator = DocGenerator()
        file_path = Path("sample.py")

        print(f"\nUpdating existing documentation...")
        print(f"Existing doc: {existing_doc['content']}")
        print(f"Code:\n{sample_code}")

        docs = generator.update(file_path, existing_doc, sample_code)

        print(f"\nUpdated Documentation:")
        print("-" * 60)
        print(docs)
        print("-" * 60)
        print("\n✓ Documentation updated successfully")

        return True

    except APIKeyMissingError as e:
        print(f"✗ Cannot test without API key: {e}")
        return False
    except DocGeneratorError as e:
        print(f"✗ Documentation update failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("DocGenerator Manual Test Suite")
    print("="*60)
    print("\nThis script tests the DocGenerator implementation.")
    print("Make sure ANTHROPIC_API_KEY is set in your environment.")

    results = []

    # Test 1: API Key handling (always runs)
    results.append(("API Key Handling", test_api_key_handling()))

    # Only run remaining tests if API key is available
    if results[0][1]:
        results.append(("Python Generation", test_python_generation()))
        results.append(("SQL Generation", test_sql_generation()))
        results.append(("R Generation", test_r_generation()))
        results.append(("Update Documentation", test_update_documentation()))
    else:
        print("\n⚠ Skipping remaining tests (no API key)")

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {total - passed} test(s) failed")


if __name__ == "__main__":
    main()