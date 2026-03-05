import json
import traceback
from pathlib import Path
from typing import List, Tuple

import config
from utils.schema import LibraryStructData, VertexLibraryEntry, ContentSource
from gcp.storage import upload_to_gcs
from gcp.vertex import import_documents_to_vertex
from utils.lifecycle import activate_file
from .base import BasePipeline

class LibraryPipeline(BasePipeline):
    
    def __init__(self):
        super().__init__("Library (DB2)")
        self.bucket = config.LIBRARY_BUCKET
        self.project_id = config.GCP_PROJECT_ID
        self.data_store = config.LIBRARY_DATA_STORE_ID
        self.location = config.LIBRARY_LOCATION

    def _get_category(self, subfolder_name: str) -> str:
        mapping = {
            "regulations": "regulation",
            "handbooks": "handbook",
            "advisory_circulars": "advisory_circular"
        }
        return mapping.get(subfolder_name, "unknown")

    def _generate_id(self, category: str, filename: str) -> str:
        # e.g. regulation_14_cfr_part_91_2025
        clean_name = filename.replace('.pdf', '').replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').lower()
        return f"{category}_{clean_name}"

    def run_phase_1_discovery_validation(self) -> Tuple[List[Path], List[str]]:
        new_dir = config.LIBRARY_NEW
        valid_files = []
        errors = []

        if not new_dir.exists():
            return [], [f"Directory not found: {new_dir}"]

        # Library docs are PDF files inside subfolders
        allowed_folders = ["regulations", "handbooks", "advisory_circulars"]
        
        for root, dirs, files in os.walk(new_dir):
            root_path = Path(root)
            if root_path == new_dir:
                continue # Skip files in root, must be in subfolder
                
            subfolder = root_path.name
            if subfolder not in allowed_folders:
                for f in files:
                    errors.append(f"Invalid subfolder '{subfolder}' for file {f}")
                continue
                
            for file_name in files:
                if not file_name.endswith('.pdf'):
                    errors.append(f"Only .pdf files allowed in library. Found: {file_name}")
                    continue
                
                valid_files.append(root_path / file_name)

        return valid_files, errors

    def run_phase_2_bridge_keys(self, new_metadata_files: List[Path]) -> List[str]:
        # Library doesn't have bridge keys to verify (it IS the destination)
        return []

    def run_phase_3_gcs_upload(self, valid_files: List[Path]) -> List[Path]:
        uploaded = []
        for f in valid_files:
            subfolder = f.parent.name
            gcs_path = f"{subfolder}/{f.name}"
            upload_to_gcs(f, self.bucket, gcs_path, self.project_id)
            uploaded.append(f)
        return uploaded

    def run_phase_4_manifest_gen(self, new_uploaded: List[Path]) -> str:
        # Collect all PDFs from active
        all_pdfs = list(config.LIBRARY_ACTIVE.glob("**/*.pdf"))
        # Add new PDFs
        all_pdfs.extend(new_uploaded)
        
        # Deduplicate
        latest_pdfs = {f.name: f for f in all_pdfs}
        
        lines = []
        for f_path in latest_pdfs.values():
            subfolder = f_path.parent.name
            filename = f_path.name
            title = f_path.stem
            category = self._get_category(subfolder)
            doc_id = self._generate_id(category, filename)
            
            struct_data = LibraryStructData(
                category=category,
                title=title,
                subfolder=subfolder,
                filename=filename
            )
            
            pdf_gcs_uri = f"gs://{self.bucket}/{subfolder}/{f_path.name}"
            
            vertex_entry = VertexLibraryEntry(
                id=doc_id,
                structData=struct_data,
                content=ContentSource(mimeType="application/pdf", uri=pdf_gcs_uri)
            )
            
            lines.append(vertex_entry.model_dump_json(exclude_none=True))

        manifest_content = "\n".join(lines)
        manifest_path = config.LIBRARY_ROOT / config.LIBRARY_JSONL_FILE
        manifest_path.write_text(manifest_content, encoding='utf-8')
        
        print(f"Uploading {manifest_path.name} to GCS root...")
        gcs_uri = upload_to_gcs(manifest_path, self.bucket, config.LIBRARY_JSONL_FILE, self.project_id)
        return gcs_uri

    def run_phase_5_vertex_import(self, manifest_gcs_uri: str) -> bool:
        try:
            import_documents_to_vertex(
                self.project_id,
                self.location,
                self.data_store,
                manifest_gcs_uri
            )
            return True
        except Exception as e:
            traceback.print_exc()
            return False

    def run_phase_6_lifecycle_commit(self, successful_files: List[Path]) -> None:
        for f in successful_files:
            activate_file(f, config.LIBRARY_ACTIVE, config.LIBRARY_SUPERSEDED)

import os # Need to import os down here for the os.walk in Phase 1 if not imported above
