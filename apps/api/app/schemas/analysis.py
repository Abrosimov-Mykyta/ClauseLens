from pydantic import BaseModel


class AnalysisSnapshot(BaseModel):
    id: str
    status: str
    summary: str
    red_flags: str
    obligations: str
    follow_up_questions: str
    created_at: str
