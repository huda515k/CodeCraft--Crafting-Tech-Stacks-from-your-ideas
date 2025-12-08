# CodeCraft Test Suite

Comprehensive test suite covering all 108 test cases from the testing documentation.

## Test Categories

1. **API Endpoint Testing** (TC001-TC005) - 5 tests
2. **Frontend Generation Module** (TC006-TC027, TC093-TC108) - 37 tests
3. **Backend Generation Module** (TC028-TC050) - 23 tests
4. **ERD Processing Module** (TC051-TC065) - 15 tests
5. **Integration Testing** (TC066-TC078) - 13 tests
6. **Error Handling and Edge Cases** (TC079-TC092) - 14 tests

**Total: 108 test cases**

## Prerequisites

1. **Server Running**: The FastAPI server must be running on `localhost:8000`
   ```bash
   python3 main.py
   # or
   uvicorn main:app --host 127.0.0.1 --port 8000
   ```

2. **API Key**: Set `GEMINI_API_KEY` environment variable
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   # or create .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

3. **Dependencies**: Install test dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Running Tests

### Run All Tests
```bash
# From project root
python3 tests/run_tests.py

# Or using pytest directly
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# API Endpoints
pytest tests/test_api_endpoints.py -v

# Frontend Generation
pytest tests/test_frontend_generation.py -v

# Backend Generation
pytest tests/test_backend_generation.py -v

# ERD Processing
pytest tests/test_erd_processing.py -v

# Integration Tests
pytest tests/test_integration.py -v

# Error Handling
pytest tests/test_error_handling.py -v
```

### Run Specific Test Case
```bash
# Run TC001
pytest tests/test_api_endpoints.py::TestHealthCheckEndpoint::test_tc001_health_check_returns_200 -v
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_api_endpoints.py    # TC001-TC005
├── test_frontend_generation.py  # TC006-TC027, TC093-TC108
├── test_backend_generation.py  # TC028-TC050
├── test_erd_processing.py   # TC051-TC065
├── test_integration.py      # TC066-TC078
├── test_error_handling.py   # TC079-TC092
├── run_tests.py            # Test runner script
└── README.md               # This file
```

## Test Fixtures

The test suite includes several fixtures in `conftest.py`:

- `base_url`: Base URL for API testing
- `temp_dir`: Temporary directory for test files
- `sample_png_image`: Sample UI image for testing
- `sample_erd_image`: Sample ERD image for testing
- `invalid_image_file`: Invalid file for error testing
- `corrupted_image_file`: Corrupted image for error testing
- `large_image_file`: Large image for performance testing
- `sample_backend_zip`: Sample backend ZIP for testing
- `check_server_running`: Check if server is running
- `check_api_key`: Check if API key is set
- `skip_if_no_api_key`: Skip test if API key not set
- `skip_if_server_down`: Skip test if server not running

## Test Execution Notes

1. **Skipped Tests**: Some tests may be skipped if:
   - Server is not running (tests will skip automatically)
   - API key is not set (tests requiring AI will skip)
   - Endpoints are not implemented (marked with `pytest.skip`)

2. **Timeout**: Tests have a default timeout of 300 seconds (5 minutes) for AI operations

3. **Test Data**: Tests automatically generate sample images and files as needed

4. **Cleanup**: Temporary files are automatically cleaned up after tests

## Expected Results

All 108 test cases should pass when:
- Server is running correctly
- API key is configured
- All endpoints are implemented
- Network connectivity is available

## Troubleshooting

### Server Not Running
```
Error: Cannot connect to server
Solution: Start the server with `python3 main.py`
```

### API Key Missing
```
Warning: GEMINI_API_KEY not set
Solution: Set the environment variable or create .env file
```

### Tests Timing Out
```
Error: Request timeout
Solution: Increase timeout in conftest.py or check network/API status
```

### Import Errors
```
Error: Module not found
Solution: Install dependencies with `pip install -r requirements.txt`
```

## Test Coverage

The test suite covers:
- ✅ API endpoint responses and structures
- ✅ UI image analysis and component extraction
- ✅ React code generation with TypeScript and CSS modules
- ✅ Prompt analysis and role extraction
- ✅ Backend generation with Node.js/Express
- ✅ ERD parsing and schema conversion
- ✅ Multi-screen app generation
- ✅ Error handling and edge cases
- ✅ Integration workflows

## Contributing

When adding new features:
1. Add corresponding test cases
2. Follow the naming convention: `test_tcXXX_description`
3. Use appropriate fixtures from `conftest.py`
4. Ensure tests are independent and can run in any order
5. Update this README if adding new test categories

