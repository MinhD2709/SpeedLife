import unittest
from app.agents.extraction import ExtractionAgent
from app.agents.orchestrator import Orchestrator
from app.agents.verification import VerificationAgent
from app.models import Evidence, Point


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.pages = [Evidence("source-a", "lecture.pdf", 1, "Force equals mass times acceleration."),
                      Evidence("source-b", "lecture.pdf", 1, "Energy is conserved in an isolated system.")]

    def test_rejects_fabricated_claim_and_wrong_source(self):
        real = self.pages[0]
        wrong = Evidence("source-a", real.filename, 2, real.text)
        points = [Point("Invented formula", real), Point(real.text, wrong), Point(real.text, real)]
        approved, issues = VerificationAgent().run(points, self.pages)
        self.assertEqual(approved, [points[2]])
        self.assertEqual(len(issues), 2)

    def test_identical_filenames_keep_document_identity(self):
        wrong = Evidence("source-b", "lecture.pdf", 1, self.pages[0].text)
        approved, issues = VerificationAgent().run([Point(wrong.text, wrong)], self.pages)
        self.assertFalse(approved)
        self.assertTrue(issues)

    def test_chunking_preserves_text_and_page(self):
        chunks = ExtractionAgent().run(self.pages[:1], chunk_chars=7)
        self.assertEqual("".join(c.text for c in chunks), self.pages[0].text)
        self.assertTrue(all(c.page == 1 and c.source_id == "source-a" for c in chunks))

    def test_recovery_replaces_unsupported_planner_output(self):
        class BadPlanner:
            def run(_, chunks):
                return [Point("Unsupported claim", chunks[0])]
        sheet = Orchestrator(planner=BadPlanner()).run(self.pages, "Physics", [])
        self.assertEqual(len(sheet.points), 2)
        self.assertTrue(any("replanned once" in step for step in sheet.trace))
        approved, issues = VerificationAgent().run(sheet.points, self.pages)
        self.assertEqual(approved, sheet.points)
        self.assertFalse(issues)

    def test_empty_input_fails(self):
        with self.assertRaises(ValueError):
            Orchestrator().run([], "Empty", [])


if __name__ == "__main__":
    unittest.main()
