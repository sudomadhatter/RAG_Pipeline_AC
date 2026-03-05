from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from pathlib import Path

class BasePipeline(ABC):
    """
    Abstract Base Class for Ingestion Pipelines.
    Defines the standard 5-phase execution flow.
    """
    
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run_phase_1_discovery_validation(self) -> Tuple[List[Path], List[str]]:
        """
        Scan `new/` directory.
        Validate schemas and pair relationships.
        Returns: 
            valid_files: List of Paths ready for upload
            errors: List of error messages (if any)
        """
        pass

    @abstractmethod
    def run_phase_2_bridge_keys(self, new_metadata_files: List[Path]) -> List[str]:
        """
        Optional: Cross-reference DB1 against DB2 library.
        Returns:
            warnings: List of warning messages. Non-blocking.
        """
        pass

    @abstractmethod
    def run_phase_3_gcs_upload(self, valid_files: List[Path]) -> List[Path]:
        """
        Uploads local files in `new/` to the GCS bucket.
        Returns: List of paths that successfully uploaded.
        """
        pass

    @abstractmethod
    def run_phase_4_manifest_gen(self, new_uploaded: List[Path]) -> Path:
        """
        Generates the `.jsonl` manifest combining `active/` and newly uploaded items.
        Uploads the manifest to GCS.
        Returns: 
            Path to the local generated manifest file.
        """
        pass

    @abstractmethod
    def run_phase_5_vertex_import(self, manifest_gcs_uri: str) -> bool:
        """
        Triggers the Vertex AI Search ingest job.
        Returns True if successful.
        """
        pass

    @abstractmethod
    def run_phase_6_lifecycle_commit(self, successful_files: List[Path]) -> None:
        """
        Moves files from `new/` to `active/`, superseding old ones.
        Updates local `manifest.json` state.
        """
        pass

    def execute(self, is_dry_run: bool = False):
        """
        Orchestrates the pipeline phases.
        """
        print(f"=== Starting {self.name} Ingestion Pipeline ===")
        
        # Phase 1
        valid_files, errors = self.run_phase_1_discovery_validation()
        if errors:
            print(f" Phase 1 Failed. {len(errors)} validation errors found:")
            for e in errors:
                print(f"  - {e}")
            print("Aborting.")
            return

        print(f" Phase 1 Complete. {len(valid_files)} files validated.")

        # If nothing to do, stop early unless forced rebuild (handled by subclass logic)
        if not valid_files:
            print("No new files found to ingest. Pipeline complete.")
            return

        # Phase 2 (warnings only)
        warnings = self.run_phase_2_bridge_keys(valid_files)
        if warnings:
            print(" Phase 2 Check: Missing Bridge Key Destinations:")
            for w in warnings:
                print(f"  - {w}")

        if is_dry_run:
            print(" Dry run flag set. Skipping GCP uploads and lifecycle commits.")
            print(f"Files that would be processed: {[f.name for f in valid_files]}")
            return

        # Phase 3
        try:
            uploaded = self.run_phase_3_gcs_upload(valid_files)
        except Exception as e:
            print(f" Phase 3 Failed. Upload error: {e}")
            return

        # Phase 4
        try:
            manifest_uri = self.run_phase_4_manifest_gen(uploaded)
        except Exception as e:
            print(f" Phase 4 Failed. Manifest generation error: {e}")
            return

        # Phase 5
        try:
            success = self.run_phase_5_vertex_import(manifest_uri)
            if not success:
               print(f" Phase 5 Failed. Vertex returned non-success state.")
               return 
        except Exception as e:
            print(f" Phase 5 Failed. Vertex import error: {e}")
            return

        # Phase 6
        try:
            self.run_phase_6_lifecycle_commit(uploaded)
            print(" Phase 6 Complete. Local filesystem state transitioned.")
        except Exception as e:
            print(f" Phase 6 Failed during lifecycle commit: {e}")
            return

        print(f" Pipeline {self.name} successfully updated data stores.")
