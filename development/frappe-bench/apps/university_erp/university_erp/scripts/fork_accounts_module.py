"""
Fork ERPNext Accounts Module into University Finance.

This script copies all doctype directories, report directories, and core
utility files from erpnext/accounts into university_erp/university_finance.
It then updates all doctype JSON module fields and rewrites all Python
imports to point to the new module path.

Usage:
    cd /workspace/development/frappe-bench/apps/university_erp
    python -m university_erp.scripts.fork_accounts_module
"""

import glob
import json
import os
import re
import shutil

# Paths relative to the university_erp app root
# (script is run from frappe-bench/apps/university_erp/)
ERPNEXT_ACCOUNTS = os.path.join("..", "erpnext", "erpnext", "accounts")
UNI_FINANCE = os.path.join("university_erp", "university_finance")


def copy_doctype_dirs():
	"""Copy all doctype directories from erpnext/accounts to university_finance.

	Excludes test_*.py files and __pycache__ directories.
	Skips directories that already exist in the destination (preserves existing doctypes).
	"""
	src = os.path.join(ERPNEXT_ACCOUNTS, "doctype")
	dst = os.path.join(UNI_FINANCE, "doctype")

	if not os.path.isdir(src):
		raise FileNotFoundError(f"Source doctype directory not found: {src}")

	os.makedirs(dst, exist_ok=True)

	copied = 0
	skipped = 0
	for entry in sorted(os.listdir(src)):
		src_dir = os.path.join(src, entry)
		dst_dir = os.path.join(dst, entry)

		if not os.path.isdir(src_dir):
			continue

		if os.path.exists(dst_dir):
			skipped += 1
			continue

		# Copy the directory, then clean up test files and __pycache__
		shutil.copytree(src_dir, dst_dir)
		_clean_directory(dst_dir)
		copied += 1

	print(f"Doctypes: copied {copied}, skipped {skipped} (already exist)")
	return copied


def copy_report_dirs():
	"""Copy all report directories from erpnext/accounts to university_finance.

	Also copies root-level report utility files:
	- financial_statements.py
	- financial_statements.html
	- non_billed_report.py
	- utils.py

	Skips directories that already exist. Excludes test_*.py and __pycache__.
	"""
	src = os.path.join(ERPNEXT_ACCOUNTS, "report")
	dst = os.path.join(UNI_FINANCE, "report")

	if not os.path.isdir(src):
		raise FileNotFoundError(f"Source report directory not found: {src}")

	os.makedirs(dst, exist_ok=True)

	# Copy report subdirectories
	copied = 0
	skipped = 0
	for entry in sorted(os.listdir(src)):
		src_path = os.path.join(src, entry)
		dst_path = os.path.join(dst, entry)

		if not os.path.isdir(src_path):
			continue

		if os.path.exists(dst_path):
			skipped += 1
			continue

		shutil.copytree(src_path, dst_path)
		_clean_directory(dst_path)
		copied += 1

	# Copy root-level report utility files
	root_files = [
		"financial_statements.py",
		"financial_statements.html",
		"non_billed_report.py",
		"utils.py",
	]
	root_copied = 0
	for fname in root_files:
		src_file = os.path.join(src, fname)
		dst_file = os.path.join(dst, fname)
		if os.path.isfile(src_file) and not os.path.isfile(dst_file):
			shutil.copy2(src_file, dst_file)
			root_copied += 1

	# Ensure __init__.py exists in report directory
	init_file = os.path.join(dst, "__init__.py")
	if not os.path.isfile(init_file):
		with open(init_file, "w") as f:
			f.write("")

	print(f"Reports: copied {copied} dirs, skipped {skipped}. Root files: {root_copied}")
	return copied


def copy_core_python_files():
	"""Copy core utility files from erpnext/accounts to university_finance.

	Files: general_ledger.py, utils.py, party.py, deferred_revenue.py
	Skips files that already exist.
	"""
	core_files = [
		"general_ledger.py",
		"utils.py",
		"party.py",
		"deferred_revenue.py",
	]

	copied = 0
	for fname in core_files:
		src_file = os.path.join(ERPNEXT_ACCOUNTS, fname)
		dst_file = os.path.join(UNI_FINANCE, fname)

		if os.path.isfile(dst_file):
			print(f"  Skipping {fname} (already exists)")
			continue

		if not os.path.isfile(src_file):
			print(f"  WARNING: Source not found: {src_file}")
			continue

		shutil.copy2(src_file, dst_file)
		copied += 1

	print(f"Core files: copied {copied}")
	return copied


def update_module_in_jsons():
	"""Walk all JSON files under university_finance/doctype/ and university_finance/report/,
	replacing "module": "Accounts" with "module": "University Finance".
	"""
	updated = 0
	for base_dir in [
		os.path.join(UNI_FINANCE, "doctype"),
		os.path.join(UNI_FINANCE, "report"),
	]:
		for json_file in glob.glob(os.path.join(base_dir, "**", "*.json"), recursive=True):
			try:
				with open(json_file) as f:
					doc = json.load(f)
			except (json.JSONDecodeError, UnicodeDecodeError):
				continue

			if not isinstance(doc, dict):
				continue

			if doc.get("module") == "Accounts":
				doc["module"] = "University Finance"
				with open(json_file, "w") as f:
					json.dump(doc, f, indent=1, sort_keys=True)
					f.write("\n")
				updated += 1

	print(f"JSON module fields updated: {updated}")
	return updated


def rewrite_imports_in_file(filepath):
	"""Rewrite all erpnext import paths in a single Python file.

	Rewrites:
	- from erpnext.accounts.* -> from university_erp.university_finance.*
	- import erpnext.accounts.* -> import university_erp.university_finance.*
	- import erpnext -> from university_erp.university_finance import _erpnext_compat as erpnext
	- from erpnext import X -> from university_erp.university_finance._erpnext_compat import X
	- from erpnext.exceptions -> from university_erp.university_finance._exceptions
	- from erpnext.controllers.* -> from university_erp.university_finance.controllers.*
	- from erpnext.utilities.transaction_base -> from university_erp.university_finance.controllers.transaction_base
	- from erpnext.utilities.regional -> from university_erp.university_finance._erpnext_compat
	- from erpnext.setup.utils import get_exchange_rate -> from university_erp.university_finance._erpnext_compat import get_exchange_rate
	- from erpnext.stock.* -> stubbed via _erpnext_compat
	"""
	try:
		with open(filepath, "r") as f:
			content = f.read()
	except (UnicodeDecodeError, IOError):
		return False

	original = content

	# 1. Replace erpnext.accounts -> university_erp.university_finance
	content = content.replace(
		"from erpnext.accounts.",
		"from university_erp.university_finance.",
	)
	content = content.replace(
		"import erpnext.accounts.",
		"import university_erp.university_finance.",
	)

	# 2. Replace erpnext.exceptions -> university_finance._exceptions
	content = content.replace(
		"from erpnext.exceptions",
		"from university_erp.university_finance._exceptions",
	)

	# 3. Replace erpnext.controllers -> university_finance.controllers
	content = content.replace(
		"from erpnext.controllers.",
		"from university_erp.university_finance.controllers.",
	)

	# 4. Replace erpnext.utilities.transaction_base
	content = content.replace(
		"from erpnext.utilities.transaction_base",
		"from university_erp.university_finance.controllers.transaction_base",
	)

	# 5. Replace erpnext.utilities.regional
	content = content.replace(
		"from erpnext.utilities.regional",
		"from university_erp.university_finance._erpnext_compat",
	)

	# 6. Replace erpnext.setup.utils import get_exchange_rate
	content = content.replace(
		"from erpnext.setup.utils import get_exchange_rate",
		"from university_erp.university_finance._erpnext_compat import get_exchange_rate",
	)

	# 7. Replace bare 'import erpnext' with compat shim (must be AFTER .accounts replacements)
	content = re.sub(
		r"^import erpnext$",
		"from university_erp.university_finance import _erpnext_compat as erpnext",
		content,
		flags=re.MULTILINE,
	)

	# 8. Replace 'from erpnext import X' with compat shim imports
	content = re.sub(
		r"^from erpnext import (.+)$",
		r"from university_erp.university_finance._erpnext_compat import \1",
		content,
		flags=re.MULTILINE,
	)

	# 9. Replace erpnext.stock imports with compat stubs
	# from erpnext.stock import get_warehouse_account_map -> from _erpnext_compat
	content = re.sub(
		r"from erpnext\.stock import get_warehouse_account_map.*",
		"from university_erp.university_finance._erpnext_compat import get_warehouse_account_map",
		content,
	)
	content = re.sub(
		r"from erpnext\.stock\.utils import get_stock_value_on.*",
		"from university_erp.university_finance._erpnext_compat import get_stock_value_on",
		content,
	)
	# Other stock imports that may exist in non-test controller files
	content = re.sub(
		r"from erpnext\.stock\.utils import check_pending_reposting.*",
		"# Stubbed: from erpnext.stock.utils import check_pending_reposting",
		content,
	)
	content = re.sub(
		r"from erpnext\.stock\.doctype\.",
		"# Stubbed: from erpnext.stock.doctype.",
		content,
	)
	content = re.sub(
		r"from erpnext\.stock\.stock_ledger",
		"# Stubbed: from erpnext.stock.stock_ledger",
		content,
	)
	content = re.sub(
		r"from erpnext\.stock\.get_item_details",
		"# Stubbed: from erpnext.stock.get_item_details",
		content,
	)
	content = re.sub(
		r"from erpnext\.stock import ",
		"# Stubbed: from erpnext.stock import ",
		content,
	)

	# 10. Handle remaining erpnext.* imports (buying, selling, etc.)
	# These are non-core dependencies that should be stubbed
	content = re.sub(
		r"from erpnext\.buying\.",
		"# Stubbed: from erpnext.buying.",
		content,
	)
	content = re.sub(
		r"from erpnext\.selling\.",
		"# Stubbed: from erpnext.selling.",
		content,
	)
	content = re.sub(
		r"from erpnext\.manufacturing\.",
		"# Stubbed: from erpnext.manufacturing.",
		content,
	)
	content = re.sub(
		r"from erpnext\.projects\.",
		"# Stubbed: from erpnext.projects.",
		content,
	)
	content = re.sub(
		r"from erpnext\.crm\.",
		"# Stubbed: from erpnext.crm.",
		content,
	)
	content = re.sub(
		r"from erpnext\.assets\.",
		"# Stubbed: from erpnext.assets.",
		content,
	)
	content = re.sub(
		r"from erpnext\.subcontracting\.",
		"# Stubbed: from erpnext.subcontracting.",
		content,
	)

	# 10b. Handle erpnext.setup.* and erpnext.utilities.* imports
	content = re.sub(
		r"from erpnext\.setup\.",
		"# Stubbed: from erpnext.setup.",
		content,
	)
	content = re.sub(
		r"from erpnext\.utilities\.",
		"# Stubbed: from erpnext.utilities.",
		content,
	)
	content = re.sub(
		r"from erpnext\.utilities import ",
		"# Stubbed: from erpnext.utilities import ",
		content,
	)

	# 11. Remaining bare erpnext references in strings (e.g., module paths in JSON-like strings)
	# These are typically in get_attr() calls - replace erpnext.accounts string references
	content = content.replace(
		'"erpnext.accounts.',
		'"university_erp.university_finance.',
	)
	content = content.replace(
		"'erpnext.accounts.",
		"'university_erp.university_finance.",
	)

	if content != original:
		with open(filepath, "w") as f:
			f.write(content)
		return True

	return False


def rewrite_all_imports():
	"""Walk ALL .py files under university_finance/ and rewrite imports."""
	rewritten = 0
	total = 0

	for dirpath, _dirnames, filenames in os.walk(UNI_FINANCE):
		for fname in filenames:
			if not fname.endswith(".py"):
				continue

			filepath = os.path.join(dirpath, fname)
			total += 1
			if rewrite_imports_in_file(filepath):
				rewritten += 1

	print(f"Import rewriting: {rewritten}/{total} files modified")
	return rewritten


def stub_stock_imports():
	"""In university_finance/utils.py, replace the stock import lines with stubs.

	The original utils.py has:
	  from erpnext.stock import get_warehouse_account_map
	  from erpnext.stock.utils import get_stock_value_on

	These should already be rewritten by rewrite_all_imports(), but this function
	ensures the stubs are properly in place.
	"""
	utils_file = os.path.join(UNI_FINANCE, "utils.py")
	if not os.path.isfile(utils_file):
		print("  WARNING: utils.py not found, skipping stock stub")
		return

	with open(utils_file) as f:
		content = f.read()

	# Verify the stock imports have been rewritten to compat imports
	if "from erpnext.stock" in content:
		content = re.sub(
			r"from erpnext\.stock import get_warehouse_account_map.*",
			"from university_erp.university_finance._erpnext_compat import get_warehouse_account_map",
			content,
		)
		content = re.sub(
			r"from erpnext\.stock\.utils import get_stock_value_on.*",
			"from university_erp.university_finance._erpnext_compat import get_stock_value_on",
			content,
		)

		with open(utils_file, "w") as f:
			f.write(content)
		print("Stock imports stubbed in utils.py")
	else:
		print("Stock imports already rewritten in utils.py")


def _clean_directory(dirpath):
	"""Remove test_*.py files and __pycache__ directories from a copied directory."""
	for root, dirs, files in os.walk(dirpath, topdown=False):
		# Remove test files
		for fname in files:
			if fname.startswith("test_") and fname.endswith(".py"):
				os.remove(os.path.join(root, fname))

		# Remove __pycache__ directories
		for dname in dirs:
			if dname == "__pycache__":
				shutil.rmtree(os.path.join(root, dname))


def run_full_fork():
	"""Orchestrate the complete fork process.

	Steps:
	1. Copy all doctype directories (excluding tests, __pycache__)
	2. Copy all report directories + root-level utility files
	3. Copy 4 core Python files (general_ledger, utils, party, deferred_revenue)
	4. Update all JSON module fields from "Accounts" to "University Finance"
	5. Rewrite all Python imports from erpnext.accounts to university_erp.university_finance
	6. Stub stock imports in utils.py
	"""
	print("=" * 60)
	print("ERPNext Accounts -> University Finance Fork")
	print("=" * 60)

	print("\n[1/6] Copying doctype directories...")
	copy_doctype_dirs()

	print("\n[2/6] Copying report directories...")
	copy_report_dirs()

	print("\n[3/6] Copying core Python files...")
	copy_core_python_files()

	print("\n[4/6] Updating JSON module fields...")
	update_module_in_jsons()

	print("\n[5/6] Rewriting Python imports...")
	rewrite_all_imports()

	print("\n[6/6] Stubbing stock imports...")
	stub_stock_imports()

	print("\n" + "=" * 60)
	print("Fork complete!")
	print("=" * 60)


if __name__ == "__main__":
	run_full_fork()
