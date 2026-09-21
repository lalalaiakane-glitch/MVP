"""評估 API：管理測試問題、一次跑完一批問題並輸出報告。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import EvalQuestion, EvalQuestionIn
from app.pipeline import run

router = APIRouter(prefix="/api/eval", tags=["eval"])


@router.get("/questions")
def list_questions(db: Session = Depends(get_db)):
    return db.query(EvalQuestion).all()


@router.post("/questions")
def add_question(payload: EvalQuestionIn, db: Session = Depends(get_db)):
    q = EvalQuestion(**payload.model_dump())
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


@router.post("/run")
def run_eval(db: Session = Depends(get_db)):
    """跑過所有測試問題，統計：正確擋下高風險問題的比例、意圖判斷準確率。"""
    questions = db.query(EvalQuestion).all()
    report = []
    correct_block_decisions = 0

    for q in questions:
        result = run(db, question=q.question, product_id=q.product_id)
        was_blocked = result.fallback_triggered or (result.validation_passed is False)
        block_decision_correct = was_blocked == q.expect_blocked
        if block_decision_correct:
            correct_block_decisions += 1

        report.append(
            {
                "question": q.question,
                "expected_intent": q.expected_intent,
                "detected_intent": result.detected_intent,
                "expect_blocked": q.expect_blocked,
                "was_blocked": was_blocked,
                "block_decision_correct": block_decision_correct,
                "final_response": result.final_response,
                "notes": q.notes,
            }
        )

    total = len(questions)
    accuracy = (correct_block_decisions / total) if total else None

    return {
        "total_questions": total,
        "correct_block_decisions": correct_block_decisions,
        "block_decision_accuracy": accuracy,
        "details": report,
    }
