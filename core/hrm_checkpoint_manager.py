#!/usr/bin/env python3
"""
HRM Checkpoint Manager
Manages HRM checkpoints for trading - download, load, and manage multiple checkpoints
"""

import os
import torch
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import json
from datetime import datetime

try:
    from huggingface_hub import hf_hub_download, snapshot_download
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logging.warning("huggingface_hub not available. Install with: pip install huggingface_hub")

logger = logging.getLogger(__name__)


class HRMCheckpointManager:
    """
    Manages HRM checkpoints for trading
    Handles downloading, loading, and switching between checkpoints
    """
    
    # Available checkpoints from HuggingFace
    CHECKPOINTS = {
        'arc_agi_2': {
            'repo_id': 'sapientinc/HRM-checkpoint-ARC-2',
            'description': 'ARC-AGI-2 checkpoint for general reasoning',
            'specialization': 'general_reasoning'
        },
        'sudoku_extreme': {
            'repo_id': 'sapientinc/HRM-checkpoint-sudoku-extreme',
            'description': 'Sudoku Extreme checkpoint for pattern recognition',
            'specialization': 'pattern_recognition'
        },
        'maze_30x30': {
            'repo_id': 'sapientinc/HRM-checkpoint-maze-30x30-hard',
            'description': 'Maze 30x30 checkpoint for path finding/optimization',
            'specialization': 'path_finding'
        }
    }
    
    def __init__(self, checkpoint_dir: str = "hrm_checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Metadata file
        self.metadata_file = self.checkpoint_dir / "checkpoint_metadata.json"
        self.metadata = self._load_metadata()
        
        logger.info(f"HRM Checkpoint Manager initialized: {self.checkpoint_dir}")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load checkpoint metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")
        
        return {
            'checkpoints': {},
            'active_checkpoint': None,
            'last_updated': None
        }
    
    def _save_metadata(self):
        """Save checkpoint metadata"""
        self.metadata['last_updated'] = datetime.now().isoformat()
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def download_checkpoint(self, checkpoint_name: str, 
                          force_download: bool = False) -> Optional[str]:
        """
        Download HRM checkpoint from HuggingFace
        
        Args:
            checkpoint_name: Name of checkpoint (arc_agi_2, sudoku_extreme, maze_30x30)
            force_download: Force re-download even if exists
        
        Returns:
            Path to downloaded checkpoint or None
        """
        if not HF_AVAILABLE:
            logger.error("huggingface_hub not available. Install with: pip install huggingface_hub")
            return None
        
        if checkpoint_name not in self.CHECKPOINTS:
            logger.error(f"Unknown checkpoint: {checkpoint_name}")
            return None
        
        checkpoint_info = self.CHECKPOINTS[checkpoint_name]
        repo_id = checkpoint_info['repo_id']
        
        # Check if already downloaded
        checkpoint_path = self.checkpoint_dir / checkpoint_name
        if checkpoint_path.exists() and not force_download:
            logger.info(f"Checkpoint {checkpoint_name} already exists at {checkpoint_path}")
            return str(checkpoint_path)
        
        try:
            logger.info(f"Downloading checkpoint {checkpoint_name} from {repo_id}...")
            
            # Download entire repository snapshot
            downloaded_path = snapshot_download(
                repo_id=repo_id,
                local_dir=str(checkpoint_path),
                local_dir_use_symlinks=False
            )
            
            # Find the actual checkpoint file
            checkpoint_file = self._find_checkpoint_file(checkpoint_path)
            
            if checkpoint_file:
                # Update metadata
                self.metadata['checkpoints'][checkpoint_name] = {
                    'path': str(checkpoint_file),
                    'repo_id': repo_id,
                    'description': checkpoint_info['description'],
                    'specialization': checkpoint_info['specialization'],
                    'downloaded_at': datetime.now().isoformat()
                }
                self._save_metadata()
                
                logger.info(f"✅ Downloaded checkpoint {checkpoint_name} to {checkpoint_file}")
                return str(checkpoint_file)
            else:
                logger.warning(f"Checkpoint downloaded but file not found in {checkpoint_path}")
                return str(checkpoint_path)
                
        except Exception as e:
            logger.error(f"❌ Failed to download checkpoint {checkpoint_name}: {e}")
            return None
    
    def _find_checkpoint_file(self, checkpoint_dir: Path) -> Optional[Path]:
        """Find the actual checkpoint file in downloaded directory"""
        # Check in checkpoint subdirectory first
        checkpoint_subdir = checkpoint_dir / "checkpoint"
        if checkpoint_subdir.exists():
            checkpoint_dir = checkpoint_subdir
        
        # Common checkpoint file names
        possible_names = [
            'step_*.pt',
            'checkpoint.pt',
            'model.pt',
            'pytorch_model.bin',
            '*.pt',
            '*.pth'
        ]
        
        for pattern in possible_names:
            files = list(checkpoint_dir.rglob(pattern))
            if files:
                # Prefer files with 'step' in name or largest file
                step_files = [f for f in files if 'step' in f.name]
                if step_files:
                    # Get the latest step file
                    step_files.sort(key=lambda x: int(x.stem.split('_')[-1]) if x.stem.split('_')[-1].isdigit() else 0, reverse=True)
                    return step_files[0]
                else:
                    # Return largest file
                    files.sort(key=lambda x: x.stat().st_size, reverse=True)
                    return files[0]
        
        # If no .pt files found, return the checkpoint directory itself
        if checkpoint_subdir.exists():
            return checkpoint_subdir
        
        return None
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """List all available and downloaded checkpoints"""
        checkpoints = []
        
        for name, info in self.CHECKPOINTS.items():
            checkpoint_data = {
                'name': name,
                'description': info['description'],
                'specialization': info['specialization'],
                'downloaded': name in self.metadata.get('checkpoints', {}),
                'path': self.metadata.get('checkpoints', {}).get(name, {}).get('path'),
                'downloaded_at': self.metadata.get('checkpoints', {}).get(name, {}).get('downloaded_at')
            }
            checkpoints.append(checkpoint_data)
        
        return checkpoints
    
    def get_checkpoint_path(self, checkpoint_name: str) -> Optional[str]:
        """Get path to checkpoint if downloaded"""
        if checkpoint_name in self.metadata.get('checkpoints', {}):
            return self.metadata['checkpoints'][checkpoint_name].get('path')
        return None
    
    def set_active_checkpoint(self, checkpoint_name: str) -> bool:
        """Set active checkpoint"""
        if checkpoint_name not in self.metadata.get('checkpoints', {}):
            logger.error(f"Checkpoint {checkpoint_name} not downloaded")
            return False
        
        self.metadata['active_checkpoint'] = checkpoint_name
        self._save_metadata()
        logger.info(f"✅ Set active checkpoint to {checkpoint_name}")
        return True
    
    def get_active_checkpoint(self) -> Optional[str]:
        """Get active checkpoint name"""
        return self.metadata.get('active_checkpoint')
    
    def load_checkpoint_state(self, checkpoint_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint state dict
        
        Args:
            checkpoint_name: Name of checkpoint, or None for active checkpoint
        
        Returns:
            State dict or None
        """
        if checkpoint_name is None:
            checkpoint_name = self.get_active_checkpoint()
        
        if checkpoint_name is None:
            logger.error("No checkpoint specified and no active checkpoint")
            return None
        
        checkpoint_path = self.get_checkpoint_path(checkpoint_name)
        if not checkpoint_path or not os.path.exists(checkpoint_path):
            logger.error(f"Checkpoint path not found: {checkpoint_path}")
            return None
        
        try:
            logger.info(f"Loading checkpoint from {checkpoint_path}...")
            checkpoint = torch.load(checkpoint_path, map_location='cpu')
            
            # Handle different checkpoint formats
            if isinstance(checkpoint, dict):
                if 'model' in checkpoint:
                    return checkpoint['model']
                elif 'state_dict' in checkpoint:
                    return checkpoint['state_dict']
                else:
                    return checkpoint
            else:
                return checkpoint
                
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None
    
    def download_all_checkpoints(self, force_download: bool = False) -> Dict[str, bool]:
        """
        Download all available checkpoints
        
        Args:
            force_download: Force re-download
        
        Returns:
            Dictionary of checkpoint_name -> success
        """
        results = {}
        
        for checkpoint_name in self.CHECKPOINTS.keys():
            logger.info(f"Downloading {checkpoint_name}...")
            path = self.download_checkpoint(checkpoint_name, force_download=force_download)
            results[checkpoint_name] = path is not None
        
        return results

