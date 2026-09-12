from manim import *

class AlgorithmArrayScene(Scene):
    """
    Template for an array state transition.
    Keep cells fixed so a swap changes values rather than the array layout.
    """
    def construct(self):
        title = Title("Array Partition: Two-Pointer Swap", color=WHITE)
        self.play(Write(title), run_time=1.0)

        # 1. Build initial array
        values = [14, 55, 32, 10, 88, 27]
        boxes = VGroup()
        numbers = VGroup()
        for val in values:
            box = Square(side_length=1.1, color=WHITE, stroke_width=2)
            num = Integer(val, color=YELLOW).move_to(box.get_center())
            boxes.add(box)
            numbers.add(num)

        boxes.arrange(RIGHT, buff=0.15).shift(UP * 0.2)
        for box, num in zip(boxes, numbers):
            num.move_to(box.get_center())
        self.play(Create(boxes), Write(numbers), run_time=1.5)
        self.wait(0.5)

        # 2. Pointers Left (i=1, value 55) and Right (j=3, value 10)
        idx_left, idx_right = 1, 3
        
        ptr_left = Arrow(DOWN * 1.5, boxes[idx_left].get_bottom(), color=RED, buff=0.15)
        label_left = MathTex("i", color=RED).next_to(ptr_left, DOWN)
        
        ptr_right = Arrow(DOWN * 1.5, boxes[idx_right].get_bottom(), color=GREEN, buff=0.15)
        label_right = MathTex("j", color=GREEN).next_to(ptr_right, DOWN)

        self.play(
            GrowArrow(ptr_left), Write(label_left),
            GrowArrow(ptr_right), Write(label_right),
            boxes[idx_left].animate.set_color(RED),
            boxes[idx_right].animate.set_color(GREEN),
            run_time=1.2
        )
        self.wait(1.0)

        # 3. Swap elements 55 and 10
        pos_left = boxes[idx_left].get_center()
        pos_right = boxes[idx_right].get_center()

        self.play(
            numbers[idx_left].animate.move_to(pos_right),
            numbers[idx_right].animate.move_to(pos_left),
            path_arc=PI / 2,
            run_time=1.8
        )

        # Reset colors
        self.play(
            boxes[idx_left].animate.set_color(WHITE),
            boxes[idx_right].animate.set_color(WHITE),
            FadeOut(ptr_left), FadeOut(label_left),
            FadeOut(ptr_right), FadeOut(label_right),
            run_time=0.8
        )
        self.wait(1.5)
