"""Video Analysis Service - AI-powered video analysis using Claude"""
import json
import base64
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
import anthropic

from app.models.video import Video
from app.core.config import settings

logger = structlog.get_logger()


class VideoAnalysisService:
    """Service for analyzing Pokemon TCG gameplay videos using Claude"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = None
        if settings.anthropic_api_key:
            self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def analyze_video(
        self,
        video: Video,
        analysis_type: str = "full"
    ) -> dict:
        """
        Analyze a video using AI.

        analysis_type:
        - "full": Complete match analysis
        - "summary": Brief summary of the match
        - "key_moments": Identify key decision points
        """
        if not self.client:
            raise ValueError("Anthropic API key not configured")

        # Extract frames from video for analysis
        frames = await self._extract_key_frames(video)

        if not frames:
            raise ValueError("Could not extract frames from video")

        # Build analysis prompt based on type
        prompt = self._build_analysis_prompt(analysis_type)

        # Analyze frames with Claude
        analysis_result = await self._analyze_with_claude(frames, prompt, analysis_type)

        # Store analysis result
        video.analysis_result = json.dumps(analysis_result)
        video.analyzed_at = datetime.now()
        await self.db.flush()

        return analysis_result

    async def _extract_key_frames(self, video: Video, num_frames: int = 10) -> list:
        """Extract key frames from video for analysis"""
        from app.services.storage import StorageService
        from moviepy.editor import VideoFileClip
        import tempfile
        import os

        storage = StorageService()

        try:
            # Download video
            bucket, object_name = video.file_path.split("/", 1)
            video_data = await storage.download_file(bucket, object_name)

            # Write to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video.format}") as tmp:
                tmp.write(video_data)
                tmp_path = tmp.name

            try:
                clip = VideoFileClip(tmp_path)
                duration = clip.duration

                # Extract frames at regular intervals
                frames = []
                interval = duration / (num_frames + 1)

                for i in range(1, num_frames + 1):
                    time = interval * i
                    frame = clip.get_frame(time)

                    # Convert to base64
                    from PIL import Image
                    from io import BytesIO

                    img = Image.fromarray(frame)
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=85)
                    frame_b64 = base64.standard_b64encode(buffer.getvalue()).decode()

                    frames.append({
                        "timestamp": time,
                        "data": frame_b64
                    })

                clip.close()
                return frames

            finally:
                os.unlink(tmp_path)

        except Exception as e:
            logger.error(f"Failed to extract frames: {str(e)}")
            return []

    def _build_analysis_prompt(self, analysis_type: str) -> str:
        """Build the analysis prompt based on type"""
        base_prompt = """You are an expert Pokemon TCG analyst. Analyze these gameplay screenshots from a Pokemon TCG match.

For each frame, identify:
- The game state (prizes remaining, active Pokemon, bench)
- Any visible card plays or actions
- The current board position

"""

        if analysis_type == "full":
            return base_prompt + """Provide a comprehensive analysis including:
1. Match overview and flow
2. Key plays and decisions
3. Deck archetypes involved
4. Strategic insights
5. What went well and what could be improved
6. Overall assessment of the player's performance

Format your response as JSON with the following structure:
{
    "match_overview": "...",
    "decks_identified": {"player": "...", "opponent": "..."},
    "key_plays": [{"timestamp": 0, "description": "...", "assessment": "..."}],
    "strategic_insights": ["..."],
    "strengths": ["..."],
    "areas_for_improvement": ["..."],
    "overall_rating": 1-10,
    "summary": "..."
}"""

        elif analysis_type == "summary":
            return base_prompt + """Provide a brief summary of the match including:
1. Who won and why
2. Main deck archetypes
3. Key turning point

Format your response as JSON:
{
    "result": "win/loss",
    "player_deck": "...",
    "opponent_deck": "...",
    "turning_point": "...",
    "summary": "..."
}"""

        else:  # key_moments
            return base_prompt + """Identify the key decision points and critical moments:
1. Important decision points
2. Misplays or optimal plays
3. Game-winning/losing moments

Format your response as JSON:
{
    "key_moments": [
        {
            "timestamp": 0,
            "description": "...",
            "decision_made": "...",
            "optimal_play": "...",
            "impact": "high/medium/low"
        }
    ]
}"""

    async def _analyze_with_claude(
        self,
        frames: list,
        prompt: str,
        analysis_type: str
    ) -> dict:
        """Send frames to Claude for analysis"""
        # Build message with images
        content = [{"type": "text", "text": prompt}]

        for i, frame in enumerate(frames):
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": frame["data"]
                }
            })
            content.append({
                "type": "text",
                "text": f"Frame {i + 1} at {frame['timestamp']:.1f}s"
            })

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": content}
                ]
            )

            # Extract JSON from response
            response_text = response.content[0].text

            # Try to parse as JSON
            try:
                # Find JSON in response
                import re
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

            # Return as text if not JSON
            return {
                "analysis_type": analysis_type,
                "raw_analysis": response_text
            }

        except Exception as e:
            logger.error(f"Claude analysis failed: {str(e)}")
            raise
