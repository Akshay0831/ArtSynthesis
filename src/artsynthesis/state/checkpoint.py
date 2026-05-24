import json
from pathlib import Path
from typing import Optional, Any
from artsynthesis.state.state_machine import StreamState, GenerationState


class CheckpointManager:
    def __init__(self, checkpoint_dir: str):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def SaveCheckpoint(self, stream_state: StreamState) -> Path:
        checkpoint_file = self.checkpoint_dir / f"stream_{stream_state.stream_id:02d}_state.json"
        
        data = {
            "stream_id": stream_state.stream_id,
            "seed": stream_state.seed,
            "state": stream_state.state.value,
            "current_stage": stream_state.current_stage,
            "completed_regions": stream_state.completed_regions,
            "hero_generated": stream_state.hero_generated,
            "sheet_complete": stream_state.sheet_complete,
            "rig_complete": stream_state.rig_complete,
            "error_message": stream_state.error_message,
        }
        
        with open(checkpoint_file, "w") as f:
            json.dump(data, f, indent=2)
        
        return checkpoint_file
    
    def LoadCheckpoint(self, checkpoint_file: str) -> Optional[StreamState]:
        path = Path(checkpoint_file)
        
        if not path.exists():
            return None
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
            
            return StreamState(
                stream_id=data.get("stream_id", 0),
                seed=data.get("seed", 0),
                state=GenerationState(data.get("state", "idle")),
                current_stage=data.get("current_stage", 0),
                completed_regions=data.get("completed_regions", []),
                hero_generated=data.get("hero_generated", False),
                sheet_complete=data.get("sheet_complete", False),
                rig_complete=data.get("rig_complete", False),
                error_message=data.get("error_message"),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            return None
    
    def DeleteCheckpoint(self, stream_id: int) -> None:
        checkpoint_file = self.checkpoint_dir / f"stream_{stream_id:02d}_state.json"
        if checkpoint_file.exists():
            checkpoint_file.unlink()
