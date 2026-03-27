import unittest

from research_loop import ResearchIdea, ResearchLoop


class ResearchLoopTest(unittest.TestCase):
    def test_add_and_select_frontier(self):
        loop = ResearchLoop()
        root = loop.add_root_idea(
            ResearchIdea(
                name="idea1",
                title="Idea 1",
                hypothesis="h1",
                experiments=["exp_a"],
                risk_factors=["cost"],
            )
        )
        child = loop.branch_node(root.node_id, "v2", "stronger baseline")

        loop.score_node(root.node_id, {"novelty": 0.7, "feasibility": 0.8, "signal_quality": 0.8, "safety": 0.9})
        loop.score_node(child.node_id, {"novelty": 0.95, "feasibility": 0.8, "signal_quality": 0.8, "safety": 0.9})

        frontier = loop.select_frontier(top_k=1)
        self.assertEqual(len(frontier), 1)
        self.assertEqual(frontier[0].node_id, child.node_id)


if __name__ == "__main__":
    unittest.main()
