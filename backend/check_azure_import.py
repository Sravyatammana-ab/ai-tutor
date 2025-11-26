#!/usr/bin/env python3
"""
Diagnostic script to check if Azure packages are installed correctly
"""
import sys
import os

print("=" * 60)
print("Azure Package Diagnostic Tool")
print("=" * 60)
print(f"\nPython executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"\nPython path locations:")
for i, path in enumerate(sys.path[:5], 1):
    print(f"  {i}. {path}")

print("\n" + "-" * 60)
print("Checking for Azure packages...")
print("-" * 60)

try:
    import azure
    print(f"✓ azure package found at: {azure.__file__}")
except ImportError as e:
    print(f"✗ azure package not found: {e}")

try:
    from azure.ai import documentintelligence
    print(f"✓ azure.ai.documentintelligence found at: {documentintelligence.__file__}")
except ImportError as e:
    print(f"✗ azure.ai.documentintelligence not found: {e}")
    print(f"  Install: {sys.executable} -m pip install azure-ai-documentintelligence")

try:
    from azure.core.credentials import AzureKeyCredential
    print(f"✓ azure.core.credentials found")
except ImportError as e:
    print(f"✗ azure.core.credentials not found: {e}")
    print(f"  Install: {sys.executable} -m pip install azure-core")

try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    print(f"✓ DocumentIntelligenceClient can be imported")
except ImportError as e:
    print(f"✗ DocumentIntelligenceClient import failed: {e}")

print("\n" + "-" * 60)
print("Recommendation:")
print("-" * 60)

print(f"\nTo install packages in the CURRENT Python environment, run:")
print(f"  {sys.executable} -m pip install azure-ai-documentintelligence azure-core")
print(f"\nOr if using a virtual environment:")
print(f"  1. Activate your venv first (e.g., venv\\Scripts\\activate)")
print(f"  2. Then run: pip install azure-ai-documentintelligence azure-core")

print("\n" + "=" * 60)

