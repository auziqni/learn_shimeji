# Test/Run Pattern Documentation

## 📋 Overview

Dokumentasi ini menjelaskan pola penamaan dan organisasi file untuk project ini menggunakan suffix `_test.py` dan `_run.py` di folder `test/`.

## 🎯 Pola Penamaan

### File Test (`_test.py`)
- **Lokasi**: `test/` folder
- **Suffix**: `_test.py`
- **Fokus**: Pengetesan komprehensif semua aspek file
- **Cakupan**: Edge cases, fallback conditions, error handling, validation

### File Run (`_run.py`)
- **Lokasi**: `test/` folder  
- **Suffix**: `_run.py`
- **Fokus**: Menjalankan fungsi utama file dengan sederhana
- **Cakupan**: Minimal setup, user-friendly output, error handling

## 📁 Struktur File

```
test/
├── xml2json_test.py      # Test komprehensif untuk xml2json.py
├── xml2json_run.py       # Runner sederhana untuk xml2json.py
├── animation_test.py      # Test komprehensif untuk animation.py
├── animation_run.py       # Runner sederhana untuk animation.py
└── ...                   # File test/run lainnya
```

## 🔧 Cara Pembuatan File

### 1. File Test (`_test.py`)

**Tujuan**: Test komprehensif yang mencakup semua aspek file

**Struktur yang Harus Diikuti**:

```python
#!/usr/bin/env python3
"""
test/[filename]_test.py - Comprehensive Test Suite for [Module Name]

Tests all aspects of the [module] including:
- Normal operations
- Edge cases  
- Fallback conditions
- Error handling
- Validation scenarios
- Performance considerations
"""

import unittest
import tempfile
import shutil
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from [module_path] import [ClassNames]


class Test[ClassName]Comprehensive(unittest.TestCase):
    """Comprehensive test suite for [ClassName]"""
    
    def setUp(self):
        """Set up test environment"""
        # Setup code here
        
    def tearDown(self):
        """Clean up test environment"""
        # Cleanup code here
    
    # ===== BASIC FUNCTIONALITY TESTS =====
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        # Basic tests
        
    # ===== EDGE CASES TESTS =====
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Edge case tests
        
    # ===== FALLBACK CONDITIONS TESTS =====
    
    def test_fallback_conditions(self):
        """Test fallback conditions"""
        # Fallback tests
        
    # ===== ERROR HANDLING TESTS =====
    
    def test_error_handling(self):
        """Test error handling"""
        # Error handling tests
        
    # ===== VALIDATION TESTS =====
    
    def test_validation_scenarios(self):
        """Test validation scenarios"""
        # Validation tests
        
    # ===== PERFORMANCE TESTS =====
    
    def test_performance_considerations(self):
        """Test performance considerations"""
        # Performance tests
        
    # ===== DATA STRUCTURE TESTS =====
    
    def test_data_structures(self):
        """Test data structures"""
        # Data structure tests
        
    # ===== INTEGRATION TESTS =====
    
    def test_integration_scenarios(self):
        """Test integration scenarios"""
        # Integration tests


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

**Kategori Test yang Wajib**:

1. **Basic Functionality Tests**
   - Test fungsi utama
   - Test parameter initialization
   - Test basic operations

2. **Edge Cases Tests**
   - Test input yang tidak valid
   - Test boundary conditions
   - Test unexpected data

3. **Fallback Conditions Tests**
   - Test ketika primary method gagal
   - Test alternative paths
   - Test default values

4. **Error Handling Tests**
   - Test exception handling
   - Test graceful degradation
   - Test error reporting

5. **Validation Tests**
   - Test input validation
   - Test output validation
   - Test data integrity

6. **Performance Tests**
   - Test dengan data besar
   - Test memory usage
   - Test processing speed

7. **Data Structure Tests**
   - Test semua data classes
   - Test property access
   - Test data conversion

8. **Integration Tests**
   - Test dengan file lain
   - Test end-to-end scenarios
   - Test real-world usage

### 2. File Run (`_run.py`)

**Tujuan**: Runner sederhana untuk menjalankan fungsi utama

**Struktur yang Harus Diikuti**:

```python
#!/usr/bin/env python3
"""
test/[filename]_run.py - Simple Runner for [Module Name]

Simple script to run [module] with minimal setup.
[Brief description of what it does]
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from [module_path] import [ClassName]


def main():
    """Main function to run [module]"""
    try:
        # Initialize with minimal setup
        instance = [ClassName](
            # Minimal parameters
        )
        
        # Run main functionality
        result = instance.main_function()
        
        # Simple output
        print(f"✅ [Success message]")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

**Karakteristik File Run**:

1. **Minimal Setup**
   - Import hanya yang diperlukan
   - Parameter minimal
   - Setup sederhana

2. **User-Friendly Output**
   - Output yang mudah dibaca
   - Emoji untuk status
   - Informasi yang relevan

3. **Error Handling**
   - Try-catch untuk semua operasi
   - Error message yang jelas
   - Exit code yang sesuai

4. **Flexibility**
   - Support parameter command line
   - Default behavior yang masuk akal
   - Help text jika diperlukan

## 📝 Contoh Implementasi

### Contoh File Test: `xml2json_test.py`

```python
# Test komprehensif dengan 8 kategori test
# - Basic functionality (converter initialization, basic conversion)
# - Edge cases (empty XML, missing attributes, invalid values)
# - Fallback conditions (namespace fallback, missing names)
# - Error handling (missing files, invalid XML, invalid references)
# - Validation (behavior categorization, action types, animation conditions)
# - Performance (large XML handling)
# - Data structures (FrameData, AnimationBlock, ActionData, BehaviorData)
# - Integration (JSON output, multiple sprite packs)
```

### Contoh File Run: `xml2json_run.py`

```python
# Runner sederhana dengan dual mode
# - Default: Convert semua sprite packs
# - Parameter: Convert sprite pack tertentu
# - Error handling: Validasi sprite existence
# - Output: Status dengan emoji dan detail
```

## 🎯 Best Practices

### Untuk File Test:

1. **Comprehensive Coverage**
   - Test semua public methods
   - Test semua edge cases
   - Test semua error conditions

2. **Organized Structure**
   - Group test berdasarkan kategori
   - Clear test names
   - Proper setup/teardown

3. **Realistic Data**
   - Use realistic test data
   - Test with actual file formats
   - Simulate real-world scenarios

4. **Performance Awareness**
   - Test with large datasets
   - Monitor memory usage
   - Test processing speed

### Untuk File Run:

1. **Minimal Dependencies**
   - Import hanya yang diperlukan
   - Avoid complex setup
   - Keep it simple

2. **User Experience**
   - Clear output messages
   - Helpful error messages
   - Intuitive usage

3. **Robust Error Handling**
   - Catch all exceptions
   - Provide meaningful errors
   - Graceful degradation

4. **Flexible Usage**
   - Support command line args
   - Provide defaults
   - Include help text

## 🔄 Workflow Pengembangan

### 1. Membuat File Baru

```bash
# 1. Buat file utama di src/
touch src/new_module.py

# 2. Buat file test
touch test/new_module_test.py

# 3. Buat file run  
touch test/new_module_run.py

# 4. Implementasi file utama
# 5. Implementasi test komprehensif
# 6. Implementasi run sederhana
```

### 2. Update File Existing

```bash
# 1. Update file utama
# 2. Update test untuk cover semua perubahan
# 3. Update run jika ada perubahan interface
# 4. Test semua file
python test/new_module_test.py
python test/new_module_run.py
```

## ⚠️ Troubleshooting

### Common Issues:

1. **Import Errors**
   ```python
   # Pastikan path setup benar
   sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
   ```

2. **Test Failures**
   ```python
   # Pastikan setup/teardown benar
   # Pastikan test data realistic
   # Pastikan assertions tepat
   ```

3. **Run Errors**
   ```python
   # Pastikan error handling lengkap
   # Pastikan output user-friendly
   # Pastikan exit codes benar
   ```

## 📊 Quality Checklist

### File Test Checklist:
- [ ] 8 kategori test terpenuhi
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] Performance considered
- [ ] Data structures tested
- [ ] Integration scenarios covered
- [ ] Realistic test data used
- [ ] Clear test organization

### File Run Checklist:
- [ ] Minimal setup
- [ ] User-friendly output
- [ ] Robust error handling
- [ ] Flexible usage
- [ ] Clear documentation
- [ ] Proper exit codes
- [ ] Help text included
- [ ] Real-world usage tested

## 🚀 Quick Reference

### Command Examples:

```bash
# Run tests
python test/xml2json_test.py

# Run simple execution
python test/xml2json_run.py

# Run with parameters
python test/xml2json_run.py HiveKnight
```

### File Naming Convention:

```
[original_filename]_test.py  # Comprehensive tests
[original_filename]_run.py   # Simple runner
```

### Import Pattern:

```python
# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import from src
from utils.xml2json import XML2JSONConverter
```

Dengan mengikuti pola ini, setiap teknisi akan memiliki panduan yang jelas untuk membuat file test dan run yang konsisten dan berkualitas tinggi. 