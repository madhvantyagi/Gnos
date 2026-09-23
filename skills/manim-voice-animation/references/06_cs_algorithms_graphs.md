# Computer Science: Algorithms, Data Structures & Graphs

Computer science visualizations communicate abstract state transitions: array
mutations, tree balances, and graph traversals. Begin with the learner's target
invariant or postcondition, then show the smallest input that makes the state
change visible. Keep data, indices, pointers, and visited state distinct; a
color is a signal, not a substitute for the algorithm's rule.

---

## 1. Array Element Swapping & State Mutations

```python
from manim import *

class ArraySwapScene(Scene):
    def construct(self):
        values = [42, 17, 89, 5, 23]
        boxes = VGroup()
        labels = VGroup()

        # Build visual array with index tags
        for i, val in enumerate(values):
            box = Square(side_length=1.2, color=WHITE, stroke_width=2)
            label = Integer(val, color=YELLOW).move_to(box.get_center())
            idx_label = Integer(i, color=GREY_B).scale(0.6).next_to(box, DOWN, buff=0.2)
            
            elem = VGroup(box, label)
            boxes.add(elem)
            labels.add(idx_label)

        boxes.arrange(RIGHT, buff=0.1).shift(UP * 0.5)
        for i, idx_mob in enumerate(labels):
            idx_mob.next_to(boxes[i], DOWN, buff=0.2)

        self.play(Create(boxes), Write(labels), run_time=1.5)
        self.wait(1)

        # Highlight elements at index 1 and index 3 (values 17 and 5)
        idx_a, idx_b = 1, 3
        box_a, box_b = boxes[idx_a], boxes[idx_b]

        self.play(
            box_a[0].animate.set_color(RED),
            box_b[0].animate.set_color(GREEN),
            run_time=0.8
        )

        # Swap elements using curved path animations
        self.play(
            box_a.animate.move_to(box_b.get_center()),
            box_b.animate.move_to(box_a.get_center()),
            path_arc=PI / 2,
            run_time=1.5
        )

        # Restore border colors
        self.play(
            box_a[0].animate.set_color(WHITE),
            box_b[0].animate.set_color(WHITE),
            run_time=0.5
        )
```

For a traversal, state the adjacency and visit-order convention. Review that
every highlighted node is reachable under the shown rule, that a swap changes
values without accidentally moving cell positions, and that the final frame
supports the claimed complexity or invariant. Add a changed input when the
lesson's outcome is transfer rather than recognition.

---

## 4. Teaching checklist: state diff, pinned quantity, stable layout, cues

- Keep the state diff visible: highlight exactly the cells or vertices that
  changed and leave that highlight plus a one-line caption in the final frame.
  Fading the pointers is fine; resetting every color to white erases the claim.
- Pin the compared quantity: keep the pair under comparison (swapped values,
  pivot, search key, or visited count) in a fixed corner panel through the
  transition. The learner inspects the change without chasing a moving label.
- Keep the layout stable: arrange array cells once and move only the value
  mobjects between fixed box centers (then swap the list references so later
  steps stay aligned). For graphs, declare one explicit `layout` dict and reuse
  it for every cue; a traversal changes vertex colors, never positions.
- Map each template block to one narration cue (`c1` input, `c2` mark, `c3`
  change, `c4` frozen diff). The narrated form replaces each `self.play`
  block with one `player.play(cue_id, ...)` keeping `run_time` inside the cue.

---

## 2. Graph Theory & Network Traversal (`Graph`)

ManimCE includes built-in `Graph` and `DiGraph` classes:

```python
class GraphTraversalScene(Scene):
    def construct(self):
        vertices = [1, 2, 3, 4, 5]
        edges = [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]
        layout = {
            1: [-3, 0, 0],
            2: [-1, 1.5, 0],
            3: [-1, -1.5, 0],
            4: [1.5, 0, 0],
            5: [3.5, 0, 0]
        }

        g = Graph(
            vertices,
            edges,
            layout=layout,
            vertex_config={"radius": 0.35, "color": BLUE_C},
            edge_config={"stroke_width": 3, "color": GREY_A}
        )

        self.play(Create(g), run_time=2)
        self.wait(0.5)

        # Breadth-First-Search traversal animation
        visited_order = [1, 2, 3, 4, 5]
        for node in visited_order:
            self.play(
                g.vertices[node].animate.set_color(YELLOW).scale(1.2),
                run_time=0.5
            )
            self.play(
                g.vertices[node].animate.scale(1 / 1.2),
                run_time=0.2
            )
```

---

## 3. Pointer Arrows for Linked Lists & Stacks

```python
class PointerScene(Scene):
    def construct(self):
        node = Rectangle(width=2, height=1, color=BLUE).shift(LEFT * 2)
        val = Text("Node", font_size=24).move_to(node)
        
        # Pointer arrow pointing to active memory block
        ptr_arrow = Arrow(UP * 2, node.get_top(), color=RED, buff=0.1)
        ptr_label = Text("head", color=RED, font_size=20).next_to(ptr_arrow, UP)

        self.add(node, val, ptr_arrow, ptr_label)
        self.wait(1)

        # Move pointer to next node
        next_pos = RIGHT * 2
        self.play(
            ptr_arrow.animate.shift(next_pos),
            ptr_label.animate.shift(next_pos),
            run_time=1.2
        )
```
