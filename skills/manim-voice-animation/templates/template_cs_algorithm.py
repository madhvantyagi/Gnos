from manim import *

class AlgorithmArrayScene(Scene):
    """
    Template for an array state transition.

    Storyboard (silent preview; map each numbered block to one narration cue):
    - Concept target: exchanging two positions changes values while the cells
      stay fixed; the final frame must show what changed.
    - Prerequisite: array indexing and the meaning of pointers i and j.
    - Success check: the learner names the two exchanged values and points to
      the cells that changed without the layout having moved.
    - Cues: c1 build array + pinned pair | c2 point at i/j | c3 swap values |
      c4 freeze diff + changed case.
    - Visible objects per cue: c1 boxes + numbers + index tags + pinned pair;
      c2 pointers i/j; c3 moving numbers; c4 highlight + caption.
    - Change per cue: c1 initial state; c2 compared positions marked;
      c3 values trade places; c4 diff stays pinned for inspection.

    Narrated form (same choreography, cue-timed audio): add scripts/ to the
    import path, build ``CuePlayer(self, manifest_path, "AlgorithmArrayScene")``,
    replace each ``self.play`` / ``self.wait`` block with one
    ``player.play("c1", ...)`` ... ``player.play("c4", ...)`` call keeping
    ``run_time`` inside the cue duration, then call ``player.finish(...)``.
    Keep cells fixed in every cue; only the numbers travel.
    """
    def construct(self):
        # Cue c1 -- narration: "Six cells; we compare positions 1 and 3."
        # Visible: boxes, numbers, index tags, pinned compared pair.
        # Change: initial state plus the quantity under comparison, pinned.
        title = Title("Array Partition: Two-Pointer Swap", color=WHITE)
        self.play(Write(title), run_time=1.0)

        values = [14, 55, 32, 10, 88, 27]
        boxes = VGroup()
        numbers = VGroup()
        for val in values:
            box = Square(side_length=1.1, color=WHITE, stroke_width=2)
            num = Integer(val, color=YELLOW).move_to(box.get_center())
            boxes.add(box)
            numbers.add(num)

        boxes.arrange(RIGHT, buff=0.15).shift(UP * 0.5)
        for box, num in zip(boxes, numbers):
            num.move_to(box.get_center())

        # Persistent index tags: part of the stable layout, never moved.
        index_tags = VGroup()
        for i, box in enumerate(boxes):
            tag = Integer(i, color=GREY_B).scale(0.5).next_to(box, UP, buff=0.15)
            index_tags.add(tag)

        # Pinned compared quantity: stays in the corner through the swap.
        compared_pair = Text("55 <-> 10", font_size=24, color=YELLOW)
        compared_panel = VGroup(
            Text("swap i=1, j=3:", font_size=22, color=GREY_B),
            compared_pair
        ).arrange(RIGHT, buff=0.2).to_corner(UL).shift(DOWN * 0.8)

        self.play(Create(boxes), Write(numbers), Write(index_tags), run_time=1.5)
        self.play(Write(compared_panel), run_time=1.0)

        # Cue c2 -- narration: "Pointer i marks 55, pointer j marks 10."
        # Visible: arrows i/j plus highlighted cells.
        # Change: the two compared positions are marked; layout does not move.
        idx_left, idx_right = 1, 3

        ptr_left = Arrow(
            boxes[idx_left].get_bottom() + DOWN * 1.2,
            boxes[idx_left].get_bottom(),
            color=RED, buff=0.15
        )
        label_left = MathTex(r"i", color=RED).next_to(ptr_left, DOWN)

        ptr_right = Arrow(
            boxes[idx_right].get_bottom() + DOWN * 1.2,
            boxes[idx_right].get_bottom(),
            color=GREEN, buff=0.15
        )
        label_right = MathTex(r"j", color=GREEN).next_to(ptr_right, DOWN)

        self.play(
            GrowArrow(ptr_left), Write(label_left),
            GrowArrow(ptr_right), Write(label_right),
            boxes[idx_left].animate.set_color(RED),
            boxes[idx_right].animate.set_color(GREEN),
            run_time=1.2
        )
        self.wait(0.5)

        # Cue c3 -- narration: "The values trade places; the cells stay put."
        # Visible: numbers travelling between fixed box centers.
        # Change: positions 1 and 3 hold each other's values.
        pos_left = boxes[idx_left].get_center()
        pos_right = boxes[idx_right].get_center()

        self.play(
            numbers[idx_left].animate.move_to(pos_right),
            numbers[idx_right].animate.move_to(pos_left),
            run_time=1.8
        )
        # Keep the VGroup order aligned with screen positions for later steps.
        numbers[idx_left], numbers[idx_right] = numbers[idx_right], numbers[idx_left]

        # Cue c4 -- narration: "Cells 1 and 3 changed; the rest did not."
        # Visible: highlight + caption persist; pointers leave.
        # Change: the state diff is frozen and inspectable; pose a new pair.
        swapped_pair = Text("10 <-> 55", font_size=24, color=YELLOW).move_to(compared_pair)
        caption = Text(
            "Positions 1 and 3 exchanged; cells stayed fixed.",
            font_size=22,
            color=GREY_B
        ).to_edge(DOWN, buff=0.4)

        self.play(
            ReplacementTransform(compared_pair, swapped_pair),
            boxes[idx_left].animate.set_color(YELLOW),
            boxes[idx_right].animate.set_color(YELLOW),
            FadeOut(ptr_left), FadeOut(label_left),
            FadeOut(ptr_right), FadeOut(label_right),
            run_time=0.8
        )
        self.play(Write(caption), run_time=1.0)
        self.wait(1.5)


class GraphTraversalTemplateScene(Scene):
    """
    Template for a graph traversal with a stable layout.

    Storyboard (silent preview; map each numbered block to one narration cue):
    - Concept target: breadth-first visit order from node 1 with fixed vertex
      positions; only the visited color changes.
    - Prerequisite: adjacency and the visit-order convention (BFS).
    - Success check: the learner recites the visit order and confirms every
      highlighted node was reachable under the shown rule.
    - Cues: c1 graph + pinned progress | c2-c3 visits in order | c4 order kept.
    - Visible objects per cue: graph (fixed layout), pinned progress readout,
      current-node highlight.
    - Change per cue: more vertices turn visited; positions never move.

    Narrated form: ``CuePlayer(self, manifest_path,
    "GraphTraversalTemplateScene")`` with one ``player.play(...)`` per cue and
    ``player.finish(...)`` at the end. The layout dict below is the stability
    contract: do not recompute it between cues.
    """
    def construct(self):
        # Cue c1 -- narration: "Five nodes; we visit breadth-first from 1."
        # Visible: graph at fixed positions, pinned progress readout.
        # Change: the input and the visit rule are on screen.
        title = Title("Graph Traversal: Breadth-First Order", color=WHITE)
        self.play(Write(title), run_time=1.0)

        vertices = [1, 2, 3, 4, 5]
        edges = [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]
        # Stable layout: explicit coordinates, reused for every cue. Never
        # auto-layout between steps or the learner loses track of identity.
        layout = {
            1: [-3.5, 0, 0],
            2: [-1.5, 1.5, 0],
            3: [-1.5, -1.5, 0],
            4: [1.0, 0, 0],
            5: [3.5, 0, 0],
        }

        g = Graph(
            vertices,
            edges,
            layout=layout,
            vertex_config={"radius": 0.35, "color": BLUE_C},
            edge_config={"stroke_width": 3, "color": GREY_A}
        )
        progress = Text("visited: 0 / 5", font_size=24, color=GREY_B).to_corner(
            UL
        ).shift(DOWN * 0.8)

        self.play(Create(g), Write(progress), run_time=1.5)

        # Cues c2-c3 -- narration: "Visit 1, then 2 and 3, then 4, then 5."
        # Visible: current node circled, visited nodes stay yellow.
        # Change: visited set grows; vertex positions stay fixed.
        visited_order = [1, 2, 3, 4, 5]
        for step, node in enumerate(visited_order, start=1):
            next_progress = Text(
                f"visited: {step} / 5", font_size=24, color=YELLOW
            ).move_to(progress, aligned_edge=LEFT)
            self.play(
                Circumscribe(g.vertices[node], color=YELLOW, run_time=0.4),
                g.vertices[node].animate.set_color(YELLOW),
                ReplacementTransform(progress, next_progress),
                run_time=0.8
            )
            progress = next_progress

        # Cue c4 -- narration: "Order 1-2-3-4-5; layout never moved."
        # Visible: fully visited graph, pinned order caption.
        # Change: final state supports the claimed order; pose a new start node.
        order_caption = Text(
            "BFS order 1-2-3-4-5; only color changed.",
            font_size=22,
            color=GREY_B
        ).to_edge(DOWN, buff=0.4)
        self.play(Write(order_caption), run_time=1.0)
        self.wait(1.5)
