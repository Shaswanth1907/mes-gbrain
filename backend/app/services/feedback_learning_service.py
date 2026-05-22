class FeedbackLearningService:
    def __init__(self, db):
        from app.repositories.feedback_learning_repository import FeedbackLearningRepository
        self.repo = FeedbackLearningRepository(db)

    def record_outcome(
        self,
        machine_code,
        action_type,
        predicted_downtime,
        actual_downtime,
        predicted_technician,
        actual_technician,
        predicted_part,
        actual_part,
        success,
        notes=""
    ):
        record = self.repo.create({
            "machine_code": machine_code,
            "action_type": action_type,
            "predicted_downtime": predicted_downtime,
            "actual_downtime": actual_downtime,
            "predicted_technician": predicted_technician,
            "actual_technician": actual_technician,
            "predicted_part": predicted_part,
            "actual_part": actual_part,
            "success": success,
            "notes": notes
        })

        downtime_variance = actual_downtime - predicted_downtime

        return {
            "message": "Feedback recorded successfully",
            "feedback_id": record.id,
            "machine_code": machine_code,
            "downtime_variance_minutes": downtime_variance,
            "technician_match": predicted_technician == actual_technician,
            "part_match": predicted_part == actual_part,
            "success": success
        }

    def insights(self, machine_code=None):
        records = (
            self.repo.get_by_machine(machine_code)
            if machine_code
            else self.repo.get_all()
        )

        if not records:
            return {
                "message": "No feedback records found"
            }

        total = len(records)
        successful = len([r for r in records if r.success])
        avg_variance = sum(
            (r.actual_downtime or 0) - (r.predicted_downtime or 0)
            for r in records
        ) / total

        technician_mismatches = [
            r for r in records
            if r.predicted_technician != r.actual_technician
        ]

        part_mismatches = [
            r for r in records
            if r.predicted_part != r.actual_part
        ]

        recommendations = []

        if avg_variance > 15:
            recommendations.append(
                "Downtime estimates are consistently low. Increase future downtime prediction buffer."
            )

        if technician_mismatches:
            recommendations.append(
                "Technician assignment mismatch detected. Improve technician availability validation."
            )

        if part_mismatches:
            recommendations.append(
                "Spare part mismatch detected. Improve root cause to part mapping."
            )

        if successful / total < 0.8:
            recommendations.append(
                "Success rate below target. Review corrective action planning logic."
            )

        if not recommendations:
            recommendations.append(
                "Prediction and execution outcomes are performing well."
            )

        return {
            "machine_code": machine_code or "ALL",
            "total_feedback_records": total,
            "success_rate_percent": round((successful / total) * 100, 2),
            "average_downtime_variance_minutes": round(avg_variance, 2),
            "technician_mismatch_count": len(technician_mismatches),
            "part_mismatch_count": len(part_mismatches),
            "learning_recommendations": recommendations
        }
