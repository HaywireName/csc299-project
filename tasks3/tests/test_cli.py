import subprocess
import sys
import shutil
import pathlib


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)


def prepare_temp_cli(tmp_path):
    """Copy tasks2/task.py into a temp directory to run CLI safely."""
    repo_root = pathlib.Path(__file__).resolve().parents[2]
    src = repo_root / 'tasks2' / 'task.py'
    dst = tmp_path / 'task.py'
    shutil.copy2(src, dst)
    return dst


def test_cli_add_and_list(tmp_path):
    script = prepare_temp_cli(tmp_path)

    # Add three tasks
    for title in ['One', 'Two', 'Three']:
        r = run([sys.executable, str(script), 'add', title], cwd=tmp_path)
        assert r.returncode == 0, r.stderr

    # List should show three incomplete
    r = run([sys.executable, str(script), 'list'], cwd=tmp_path)
    assert 'Total: 3 (0 completed, 3 incomplete)' in r.stdout


def test_cli_complete_multiple_ids(tmp_path):
    script = prepare_temp_cli(tmp_path)

    # Add five tasks
    for i in range(1, 6):
        run([sys.executable, str(script), 'add', f'T{i}'], cwd=tmp_path)

    # Complete 2,3,4 in one command
    r = run([sys.executable, str(script), 'complete', '2', '3', '4'], cwd=tmp_path)
    assert r.returncode == 0
    assert '✓ Completed tasks #2, #3, and #4' in r.stdout

    # Verify with --all that T2-T4 are completed and T1,T5 incomplete
    r = run([sys.executable, str(script), 'list', '--all'], cwd=tmp_path)
    out = r.stdout
    assert '✓ Completed' in out
    assert 'Total: 5 (3 completed, 2 incomplete)' in out


def test_cli_delete_multiple_ids(tmp_path):
    script = prepare_temp_cli(tmp_path)

    # Add five tasks
    for name in ['A', 'B', 'C', 'D', 'E']:
        run([sys.executable, str(script), 'add', name], cwd=tmp_path)

    # Delete 1,3,5 in one call
    r = run([sys.executable, str(script), 'delete', '1', '3', '5'], cwd=tmp_path)
    assert r.returncode == 0
    assert '✗ Deleted tasks #1, #3, and #5' in r.stdout

    # Remaining should be 2 tasks
    r = run([sys.executable, str(script), 'list'], cwd=tmp_path)
    assert 'Total: 2 (0 completed, 2 incomplete)' in r.stdout


def test_cli_delete_completed_only(tmp_path):
    script = prepare_temp_cli(tmp_path)

    # Add three tasks
    for name in ['A', 'B', 'C']:
        run([sys.executable, str(script), 'add', name], cwd=tmp_path)

    # Complete middle one
    run([sys.executable, str(script), 'complete', '2'], cwd=tmp_path)

    # Attempt to delete 1,2 with completed-only; should skip 1 and delete 2
    r = run([sys.executable, str(script), 'delete', '1', '2', '--completed-only'], cwd=tmp_path)
    out = r.stdout
    assert 'Skip: Task #1 is not completed' in out
    assert '✗ Deleted task #2' in out

    r = run([sys.executable, str(script), 'list', '--all'], cwd=tmp_path)
    assert 'Total: 2 (0 completed, 2 incomplete)' in r.stdout
