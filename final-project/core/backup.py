"""
Backup management for PKMS application.

Provides functionality to create, list, restore, and manage backups of all data.
"""

import os
import json
import zipfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from core.errors import StorageError, InvalidInputError
from core.utils import format_success, format_error, format_info, pluralize


class BackupManager:
    """Manages backups of all PKMS data."""
    
    def __init__(self, data_dir):
        """
        Initialize BackupManager.
        
        Args:
            data_dir: Path to data directory
        """
        self.data_dir = Path(data_dir)
        self.backup_dir = self.data_dir / 'backups'
        self.export_dir = self.data_dir.parent / 'exports'
        
        # Ensure directories exist
        self.backup_dir.mkdir(exist_ok=True)
        self.export_dir.mkdir(exist_ok=True)
    
    def create_backup(self, auto=False):
        """
        Create a backup ZIP of all data.
        
        Args:
            auto: Whether this is an automatic backup
            
        Returns:
            Path to created backup file
            
        Raises:
            StorageError: If backup creation fails
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prefix = "auto_backup" if auto else "backup"
        backup_filename = f"{prefix}_{timestamp}.zip"
        backup_path = self.backup_dir / backup_filename
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add README
                readme_content = self._generate_backup_readme()
                zipf.writestr('README.txt', readme_content)
                
                # Add all JSON files
                for json_file in self.data_dir.glob('*.json'):
                    arcname = f'data/{json_file.name}'
                    zipf.write(json_file, arcname)
                
                # Add documents
                docs_dir = self.data_dir / 'docs'
                if docs_dir.exists():
                    for doc_type in ['pdfs', 'docx', 'txt']:
                        type_dir = docs_dir / doc_type
                        if type_dir.exists():
                            for doc_file in type_dir.rglob('*'):
                                if doc_file.is_file():
                                    arcname = f'data/docs/{doc_type}/{doc_file.name}'
                                    zipf.write(doc_file, arcname)
                
                # Add settings if exists
                settings_file = self.data_dir / 'settings.json'
                if settings_file.exists():
                    zipf.write(settings_file, 'data/settings.json')
            
            return backup_path
        
        except Exception as e:
            raise StorageError(
                f"Failed to create backup: {str(e)}",
                filepath=str(backup_path),
                operation="backup"
            )
    
    def list_backups(self):
        """
        List all backup files with metadata.
        
        Returns:
            List of tuples (filename, size_mb, created_date, is_auto)
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob('*.zip'), reverse=True):
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            created = datetime.fromtimestamp(backup_file.stat().st_mtime)
            is_auto = backup_file.name.startswith('auto_backup')
            
            backups.append((
                backup_file.name,
                size_mb,
                created,
                is_auto
            ))
        
        return backups
    
    def restore_backup(self, backup_file):
        """
        Restore from a backup ZIP file.
        
        Args:
            backup_file: Name of backup file or full path
            
        Raises:
            InvalidInputError: If backup file not found
            StorageError: If restore fails
        """
        # Find backup file
        if isinstance(backup_file, str):
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                backup_path = Path(backup_file)
        else:
            backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise InvalidInputError(
                f"Backup file not found: {backup_file}",
                field="backup_file"
            )
        
        try:
            # Create temporary restore directory
            temp_dir = self.data_dir / 'temp_restore'
            temp_dir.mkdir(exist_ok=True)
            
            # Extract backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Validate backup structure
            data_dir = temp_dir / 'data'
            if not data_dir.exists():
                raise InvalidInputError("Invalid backup format: missing data directory")
            
            # Move files to data directory
            for item in data_dir.iterdir():
                dest = self.data_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))
            
            # Cleanup temp directory
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            # Cleanup on error
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise StorageError(
                f"Failed to restore backup: {str(e)}",
                filepath=str(backup_path),
                operation="restore"
            )
    
    def auto_backup(self):
        """
        Create automatic backup if last backup is older than 24 hours.
        Only keeps the most recent auto-backup, deletes older ones.
        
        Returns:
            Tuple (created, backup_path or None)
        """
        # Check when last auto-backup was created
        auto_backups = [
            (f, self.backup_dir / f)
            for f in os.listdir(self.backup_dir)
            if f.startswith('auto_backup') and f.endswith('.zip')
        ]
        
        if auto_backups:
            # Sort by modification time
            auto_backups.sort(key=lambda x: x[1].stat().st_mtime, reverse=True)
            latest_backup = auto_backups[0][1]
            last_backup_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
            
            # Check if backup is needed
            if datetime.now() - last_backup_time < timedelta(hours=24):
                return False, None
            
            # Delete old auto-backups
            for filename, filepath in auto_backups:
                try:
                    filepath.unlink()
                except Exception:
                    pass  # Ignore deletion errors
        
        # Create new auto-backup
        try:
            backup_path = self.create_backup(auto=True)
            return True, backup_path
        except Exception:
            return False, None
    
    def cleanup_old_backups(self, keep_count=7, manual_keep_count=None):
        """
        Delete old backups, keeping the most recent ones.
        
        Args:
            keep_count: Number of auto-backups to keep
            manual_keep_count: Number of manual backups to keep (None = keep all)
        """
        # Get all backups
        auto_backups = []
        manual_backups = []
        
        for backup_file in self.backup_dir.glob('*.zip'):
            mtime = backup_file.stat().st_mtime
            if backup_file.name.startswith('auto_backup'):
                auto_backups.append((backup_file, mtime))
            else:
                manual_backups.append((backup_file, mtime))
        
        # Sort by modification time (newest first)
        auto_backups.sort(key=lambda x: x[1], reverse=True)
        manual_backups.sort(key=lambda x: x[1], reverse=True)
        
        # Delete old auto-backups
        for backup_file, _ in auto_backups[keep_count:]:
            try:
                backup_file.unlink()
            except Exception:
                pass  # Ignore deletion errors
        
        # Delete old manual backups if specified
        if manual_keep_count is not None:
            for backup_file, _ in manual_backups[manual_keep_count:]:
                try:
                    backup_file.unlink()
                except Exception:
                    pass
    
    def export_data(self):
        """
        Create full export ZIP with all data and metadata.
        
        Returns:
            Path to export file
            
        Raises:
            StorageError: If export fails
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_filename = f"pkms_export_{timestamp}.zip"
        export_path = self.export_dir / export_filename
        
        try:
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add export README
                readme_content = self._generate_export_readme()
                zipf.writestr('README.txt', readme_content)
                
                # Add metadata
                metadata = self._generate_export_metadata()
                zipf.writestr('export_info.json', json.dumps(metadata, indent=2))
                
                # Add all JSON files
                for json_file in self.data_dir.glob('*.json'):
                    arcname = f'data/{json_file.name}'
                    zipf.write(json_file, arcname)
                
                # Add documents
                docs_dir = self.data_dir / 'docs'
                if docs_dir.exists():
                    for doc_type in ['pdfs', 'docx', 'txt']:
                        type_dir = docs_dir / doc_type
                        if type_dir.exists():
                            for doc_file in type_dir.rglob('*'):
                                if doc_file.is_file():
                                    arcname = f'data/docs/{doc_type}/{doc_file.name}'
                                    zipf.write(doc_file, arcname)
                
                # Add settings
                settings_file = self.data_dir / 'settings.json'
                if settings_file.exists():
                    zipf.write(settings_file, 'data/settings.json')
            
            return export_path
        
        except Exception as e:
            raise StorageError(
                f"Failed to create export: {str(e)}",
                filepath=str(export_path),
                operation="export"
            )
    
    def import_data(self, import_file, mode='merge'):
        """
        Import data from export ZIP file.
        
        Args:
            import_file: Path to import ZIP file
            mode: 'merge' or 'replace'
            
        Returns:
            Dictionary with import statistics
            
        Raises:
            InvalidInputError: If import file invalid
            StorageError: If import fails
        """
        import_path = Path(import_file)
        if not import_path.exists():
            raise InvalidInputError(
                f"Import file not found: {import_file}",
                field="import_file"
            )
        
        try:
            # Create temporary import directory
            temp_dir = self.data_dir / 'temp_import'
            temp_dir.mkdir(exist_ok=True)
            
            # Extract import file
            with zipfile.ZipFile(import_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Validate import structure
            data_dir = temp_dir / 'data'
            if not data_dir.exists():
                raise InvalidInputError("Invalid import format: missing data directory")
            
            stats = {
                'tasks': 0,
                'documents': 0,
                'settings': False
            }
            
            if mode == 'replace':
                # Backup current data first
                self.create_backup(auto=False)
                
                # Replace all data
                for item in data_dir.iterdir():
                    dest = self.data_dir / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    shutil.move(str(item), str(dest))
                
                # Count imported items
                tasks_file = self.data_dir / 'tasks.json'
                if tasks_file.exists():
                    with open(tasks_file) as f:
                        tasks_data = json.load(f)
                        for folder_tasks in tasks_data.get('folders', {}).values():
                            stats['tasks'] += len(folder_tasks)
                
                docs_file = self.data_dir / 'docs_metadata.json'
                if docs_file.exists():
                    with open(docs_file) as f:
                        docs_data = json.load(f)
                        stats['documents'] = len(docs_data)
                
                settings_file = self.data_dir / 'settings.json'
                stats['settings'] = settings_file.exists()
            
            else:  # merge mode
                # Merge tasks
                tasks_file = data_dir / 'tasks.json'
                if tasks_file.exists():
                    stats['tasks'] = self._merge_tasks(tasks_file)
                
                # Merge documents
                docs_file = data_dir / 'docs_metadata.json'
                if docs_file.exists():
                    stats['documents'] = self._merge_documents(docs_file, data_dir)
                
                # Settings are not merged (kept as-is)
            
            # Cleanup temp directory
            shutil.rmtree(temp_dir)
            
            return stats
        
        except Exception as e:
            # Cleanup on error
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise StorageError(
                f"Failed to import data: {str(e)}",
                filepath=str(import_path),
                operation="import"
            )
    
    def _merge_tasks(self, import_tasks_file):
        """Merge imported tasks with existing tasks."""
        current_tasks_file = self.data_dir / 'tasks.json'
        
        # Load imported tasks
        with open(import_tasks_file) as f:
            import_data = json.load(f)
        
        # Load current tasks or create new structure
        if current_tasks_file.exists():
            with open(current_tasks_file) as f:
                current_data = json.load(f)
        else:
            current_data = {"folders": {}, "current_folder": "default"}
        
        # Merge folders
        imported_count = 0
        for folder_name, folder_tasks in import_data.get('folders', {}).items():
            if folder_name not in current_data['folders']:
                current_data['folders'][folder_name] = []
            
            # Add tasks that don't already exist (check by ID)
            existing_ids = {task['id'] for task in current_data['folders'][folder_name]}
            for task in folder_tasks:
                if task['id'] not in existing_ids:
                    current_data['folders'][folder_name].append(task)
                    imported_count += 1
        
        # Save merged data
        with open(current_tasks_file, 'w') as f:
            json.dump(current_data, f, indent=2)
        
        return imported_count
    
    def _merge_documents(self, import_docs_file, import_data_dir):
        """Merge imported documents with existing documents."""
        current_docs_file = self.data_dir / 'docs_metadata.json'
        
        # Load imported docs metadata
        with open(import_docs_file) as f:
            import_docs = json.load(f)
        
        # Load current docs or create new list
        if current_docs_file.exists():
            with open(current_docs_file) as f:
                current_docs = json.load(f)
        else:
            current_docs = []
        
        # Merge documents
        imported_count = 0
        existing_ids = {doc['id'] for doc in current_docs}
        
        for doc in import_docs:
            if doc['id'] not in existing_ids:
                # Copy document file
                src_path = import_data_dir / 'docs' / doc['extension'][1:] + 's' / Path(doc['filepath']).name
                if src_path.exists():
                    dest_dir = self.data_dir / 'docs' / (doc['extension'][1:] + 's')
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    dest_path = dest_dir / src_path.name
                    shutil.copy2(src_path, dest_path)
                    
                    # Update filepath in metadata
                    doc['filepath'] = str(dest_path)
                    current_docs.append(doc)
                    imported_count += 1
        
        # Save merged metadata
        with open(current_docs_file, 'w') as f:
            json.dump(current_docs, f, indent=2)
        
        return imported_count
    
    def _generate_backup_readme(self):
        """Generate README content for backup."""
        return f"""PKMS Backup Archive
==================

Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Format Version: 1.0

Contents:
---------
- data/*.json: All task and metadata files
- data/docs/: All document files (PDFs, DOCX, TXT)
- data/settings.json: Application settings

Restore Instructions:
--------------------
1. Open PKMS application
2. Run command: restore <backup_filename>
3. Confirm restoration when prompted

The backup will restore all your tasks, documents, and settings.

WARNING: Restoring will replace current data. Make sure to backup
current data before restoring if you want to keep it.
"""
    
    def _generate_export_readme(self):
        """Generate README content for export."""
        return f"""PKMS Data Export
===============

Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Format Version: 1.0

Contents:
---------
- README.txt: This file
- export_info.json: Export metadata
- data/*.json: All task and metadata files
- data/docs/: All document files
- data/settings.json: Application settings

Import Instructions:
-------------------
1. Open PKMS application
2. Run command: import <export_filename>
3. Choose merge or replace mode:
   - merge: Combine with existing data
   - replace: Replace all current data

Export Format:
-------------
This export contains a complete snapshot of your PKMS data at the
time of export. It can be imported into any PKMS installation.

For questions or issues, refer to the PKMS documentation.
"""
    
    def _generate_export_metadata(self):
        """Generate metadata for export."""
        # Count items
        tasks_count = 0
        docs_count = 0
        
        tasks_file = self.data_dir / 'tasks.json'
        if tasks_file.exists():
            with open(tasks_file) as f:
                tasks_data = json.load(f)
                for folder_tasks in tasks_data.get('folders', {}).values():
                    tasks_count += len(folder_tasks)
        
        docs_file = self.data_dir / 'docs_metadata.json'
        if docs_file.exists():
            with open(docs_file) as f:
                docs_data = json.load(f)
                docs_count = len(docs_data)
        
        return {
            'format_version': '1.0',
            'export_date': datetime.now().isoformat(),
            'pkms_version': '1.0.0',
            'tasks_count': tasks_count,
            'documents_count': docs_count,
            'contents': {
                'tasks': tasks_count > 0,
                'documents': docs_count > 0,
                'settings': (self.data_dir / 'settings.json').exists()
            }
        }
    
    def get_storage_stats(self):
        """
        Calculate storage statistics.
        
        Returns:
            Dictionary with storage information
        """
        stats = {
            'total_mb': 0,
            'json_mb': 0,
            'docs_mb': 0,
            'cache_mb': 0,
            'backups_mb': 0
        }
        
        # JSON files
        for json_file in self.data_dir.glob('*.json'):
            stats['json_mb'] += json_file.stat().st_size / (1024 * 1024)
        
        # Documents
        docs_dir = self.data_dir / 'docs'
        if docs_dir.exists():
            for doc_file in docs_dir.rglob('*'):
                if doc_file.is_file():
                    stats['docs_mb'] += doc_file.stat().st_size / (1024 * 1024)
        
        # Cache
        cache_dir = self.data_dir / 'doc_cache'
        if cache_dir.exists():
            for cache_file in cache_dir.rglob('*'):
                if cache_file.is_file():
                    stats['cache_mb'] += cache_file.stat().st_size / (1024 * 1024)
        
        # Backups
        if self.backup_dir.exists():
            for backup_file in self.backup_dir.glob('*.zip'):
                stats['backups_mb'] += backup_file.stat().st_size / (1024 * 1024)
        
        stats['total_mb'] = stats['json_mb'] + stats['docs_mb'] + stats['cache_mb']
        
        return stats
