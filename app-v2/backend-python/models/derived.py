from pydantic import BaseModel
from models.user_config import Track


class DerivedPlaylist(BaseModel):
  spotify_url: str
  spotify_id: str
  name: str
  enabled: bool
  tracks: list[Track]
  tracks_count: int