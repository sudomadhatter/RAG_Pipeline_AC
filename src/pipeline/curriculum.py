import json
import traceback
from pathlib import Path
from typing import List, Tuple

import config
from utils.schema import CurriculumLessonSchema, VertexCurriculumEntry, ContentSource
from gcp.storage import upload_to_gcs
from gcp.vertex import import_documents_to_vertex
from utils.lifecycle import activate_file
from .base import BasePipeline

class CurriculumPipeline(BasePipeline):
    
    def __init__(self):
        super().__init__("Curriculum (DB1)")
        self.bucket = config.CURRICULUM_BUCKET
        self.project_id = config.GCP_PROJECT_ID
        self.data_store = config.CURRICULUM_DATA_STORE_ID
        self.location = config.CURRICULUM_LOCATION

    def run_phase_1_discovery_validation(self) -> Tuple[List[Path], List[str]]:
        new_dir = config.CURRICULUM_NEW
        valid_files = []
        errors = []

        if not new_dir.exists():
            return [], ["Directory not found: " + str(new_dir)]

        for json_file in new_dir.glob("*.json"):
            md_file = new_dir / (json_file.stem + ".md")
            
            if not md_file.exists():
                errors.append(f"Orphaned metadata: {json_file.name} lacks matching .md file")
                continue

            try:
                content = json.loads(json_file.read_text('utf-8'))
                CurriculumLessonSchema(**content)
                # Valid pair
                valid_files.append(json_file)
                valid_files.append(md_file)
            except Exception as e:
                errors.append(f"Schema validation failed for {json_file.name}: {e}")

        return valid_files, errors

    def run_phase_2_bridge_keys(self, new_metadata_files: List[Path]) -> List[str]:
        # TODO: Implement cross-referencing with DB2 library/active contents
        # For now, we yield no warnings
        return []

    def run_phase_3_gcs_upload(self, valid_files: List[Path]) -> List[Path]:
        uploaded = []
        for f in valid_files:
            gcs_path = f"lessons/{f.name}"
            upload_to_gcs(f, self.bucket, gcs_path, self.project_id)
            uploaded.append(f)
        return uploaded

    def run_phase_4_manifest_gen(self, new_uploaded: List[Path]) -> str:
        # Collect all JSONs from active
        all_jsons = list(config.CURRICULUM_ACTIVE.glob("*.json"))
        # Add new JSONs
        new_jsons = [f for f in new_uploaded if f.suffix == '.json']
        all_jsons.extend(new_jsons)
        
        # Deduplicate by filename (new overrides active in this run)
        latest_jsons = {f.name: f for f in all_jsons}
        
        lines = []
        for f_path in latest_jsons.values():
            try:
                data = json.loads(f_path.read_text('utf-8'))
                schema = CurriculumLessonSchema(**data)
                
                # The markdown file URI in GCS
                md_gcs_uri = f"gs://{self.bucket}/lessons/{f_path.stem}.md"
                
                vertex_entry = VertexCurriculumEntry(
                    id=schema.id,
                    structData=schema.structData,
                    content=ContentSource(mimeType="text/markdown", uri=md_gcs_uri)
                )
                lines.append(vertex_entry.model_dump_json(exclude_none=True))
            except Exception as e:
                print(f" FATAL ERROR: Schema validation failed for {f_path.name}: {e}")
                raise ValueError(f"Aborting pipeline. Invalid metadata found in {f_path.name}: {e}") from e

        manifest_content = "\n".join(lines)
        manifest_path = config.CURRICULUM_ROOT / config.CURRICULUM_JSONL_FILE
        manifest_path.write_text(manifest_content, encoding='utf-8')
        
        # Upload manifest to GCS Root
        print(f"Uploading {manifest_path.name} to GCS root...")
        gcs_uri = upload_to_gcs(manifest_path, self.bucket, config.CURRICULUM_JSONL_FILE, self.project_id)
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
            activate_file(f, config.CURRICULUM_ACTIVE, config.CURRICULUM_SUPERSEDED)
