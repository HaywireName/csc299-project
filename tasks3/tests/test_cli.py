import shutil
import subprocess
import sys
from pathlib import Path


def prepare_temp_cli(tmp_path: Path) -> Path:
	"""Copy the CLI script (task.py) into a temporary folder and return its path."""
	repo_root = Path(__file__).resolve().parents[1]
	src = repo_root / "task.py"
	dst = tmp_path / "task.py"
	shutil.copy2(src, dst)
	return dst


def run(cmd, cwd: Path):
	return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def test_cli_add_and_list(tmp_path: Path):
	script = prepare_temp_cli(tmp_path)
	# Add two tasks
	run([sys.executable, str(script), 'add', 'Alpha'], cwd=tmp_path)
	run([sys.executable, str(script), 'add', 'Bravo'], cwd=tmp_path)

	# List tasks and verify they appear
	r = run([sys.executable, str(script), 'list'], cwd=tmp_path)
	out = r.stdout
	assert 'Alpha' in out and 'Bravo' in out


def test_cli_complete_multiple(tmp_path: Path):
	script = prepare_temp_cli(tmp_path)
	for name in ['A', 'B', 'C']:
		run([sys.executable, str(script), 'add', name], cwd=tmp_path)

	# Complete first two by display ids
	run([sys.executable, str(script), 'complete', '1', '2'], cwd=tmp_path)

	r = run([sys.executable, str(script), 'list', '--all'], cwd=tmp_path)
	out = r.stdout
	# Expect at least two completed markers
	assert out.count('✓ Completed') >= 2


def test_cli_delete_ids(tmp_path: Path):
	script = prepare_temp_cli(tmp_path)
	for name in ['A', 'B', 'C']:
		run([sys.executable, str(script), 'add', name], cwd=tmp_path)

	# Delete the middle by display id
	run([sys.executable, str(script), 'delete', '2'], cwd=tmp_path)

	r = run([sys.executable, str(script), 'list'], cwd=tmp_path)
	out = r.stdout
	assert 'A' in out and 'C' in out and 'B' not in out


def test_cli_delete_all(tmp_path: Path):
	script = prepare_temp_cli(tmp_path)
	for name in ['A', 'B']:
		run([sys.executable, str(script), 'add', name], cwd=tmp_path)

	run([sys.executable, str(script), 'delete', '--all'], cwd=tmp_path)

	r = run([sys.executable, str(script), 'list', '--all'], cwd=tmp_path)
	out = r.stdout
	assert 'No tasks found' in out


def test_cli_clean_removes_only_completed(tmp_path: Path):
	script = prepare_temp_cli(tmp_path)
	# Add three tasks
	for name in ['A', 'B', 'C']:
		run([sys.executable, str(script), 'add', name], cwd=tmp_path)

	# Complete middle one
	run([sys.executable, str(script), 'complete', '2'], cwd=tmp_path)

	# Clean should remove completed tasks only
	run([sys.executable, str(script), 'clean'], cwd=tmp_path)

	r = run([sys.executable, str(script), 'list', '--all'], cwd=tmp_path)
	out = r.stdout
	assert 'A' in out and 'C' in out and 'B' not in out

