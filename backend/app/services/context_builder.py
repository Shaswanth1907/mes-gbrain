class ContextBuilder:
    def build_machine_context(self, context_data):
        if not context_data:
            return "No machine data found."

        machine = context_data["machine"]
        issues = context_data["issues"]

        machine_section = f"""
Machine Details:
Machine Ref: {machine.machine_ref}
Machine Code: {machine.machine_code}
Name: {machine.name}
Location: {machine.location}
Status: {machine.status}
"""

        issue_section = "\nIssues:\n"

        if issues:
            for issue in issues:
                issue_section += (
                    f"- {issue.issue_ref} | "
                    f"{issue.title} | "
                    f"{issue.status} | "
                    f"Severity: {issue.severity}\n"
                )
        else:
            issue_section += "No issues found.\n"

        return machine_section + issue_section