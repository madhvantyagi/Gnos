from manim import *

class PhysicsSimScene(Scene):
    """
    Template for Physics Simulations & Dynamical Systems.

    Storyboard (silent preview; map each numbered block to one narration cue):
    - Concept target: a spring force F = -k*x - c*v changes velocity, and
      velocity changes position; damping dissipates energy.
    - Prerequisite: Hooke's law and the idea that acceleration follows force.
    - Success check: the learner predicts the sign of F at each extreme and
      checks it against the arrow plus the pinned x / v / F readouts.
    - Cues: c1 setup + assumptions | c2 force law + readouts tied to state |
      c3 run simulation (force -> motion) | c4 freeze + changed case.
    - Visible objects per cue: c1 axes + equilibrium + assumptions footer;
      c2 mass + spring + force arrow + x/v/F panel; c3 same panel live;
      c4 frozen state + decay note.
    - Change per cue: c1 model on screen; c2 cause (F) linked to state;
      c3 motion caused by F; c4 updater detached, amplitude decayed.

    Narrated form (same choreography, cue-timed audio): add scripts/ to the
    import path, build ``CuePlayer(self, manifest_path, "PhysicsSimScene")``,
    replace each ``self.play`` / ``self.wait`` block with one
    ``player.play("c1", ...)`` ... ``player.play("c4", ...)`` call keeping
    ``run_time`` inside the cue duration, then call ``player.finish(...)``.
    The updater run in c3 uses ``player.play("c3")`` with no animation args:
    the wait inside the cue lets the attached updater evolve the state.
    """
    def construct(self):
        # Cue c1 -- narration: "A damped spring on a track; here is the model."
        # Visible: title, axes, equilibrium line, assumptions footer.
        # Change: the model and its limits are on screen before motion starts.
        title = Title("Harmonic Oscillator Simulation", color=WHITE)
        self.play(Write(title), run_time=1.0)

        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-2, 2, 1],
            x_length=8,
            y_length=3.5,
            axis_config={"color": GREY_B, "stroke_width": 2},
            tips=False
        ).shift(DOWN * 0.5)
        equilibrium_line = DashedLine(
            axes.c2p(0, -1.2), axes.c2p(0, 1.2), color=YELLOW
        )
        assumptions = Text(
            "1-D spring, linear damping, semi-implicit Euler",
            font_size=20,
            color=GREY_B
        ).to_edge(DOWN, buff=0.4)
        self.play(Create(axes), Create(equilibrium_line), run_time=1.2)
        self.play(Write(assumptions), run_time=1.0)

        # Cue c2 -- narration: "Force pulls toward rest; the panel reads state."
        # Visible: mass, spring, force arrow, pinned x / v / F readouts.
        # Change: the cause (F) appears, computed from the same state as motion.
        mass = 1.0        # kg
        k = 4.0           # Spring constant (N/m)
        damping = 0.3     # Linear damping (N s / m)

        # Single simulation state shared by geometry AND readouts.
        sim_state = {"x": 3.0, "v": 0.0}

        def spring_force():
            return -k * sim_state["x"] - damping * sim_state["v"]

        mass_dot = Dot(axes.c2p(sim_state["x"], 0), color=TEAL, radius=0.2)
        spring_line = always_redraw(lambda: Line(
            axes.c2p(-3.5, 0), mass_dot.get_center(), stroke_width=4, color=GREY_A
        ))

        force_scale = 0.15
        max_arrow = 2.2

        def force_arrow_mobject():
            raw = spring_force() * force_scale
            clipped = max(-max_arrow, min(max_arrow, raw))
            if abs(clipped) < 0.05:
                clipped = 0.05 if raw >= 0 else -0.05
            start = mass_dot.get_center()
            return Arrow(
                start, start + RIGHT * clipped,
                buff=0.05, stroke_width=5, color=YELLOW
            )

        force_arrow = always_redraw(force_arrow_mobject)
        force_label = Text("F", font_size=24, color=YELLOW)
        force_label.add_updater(
            lambda mob: mob.next_to(force_arrow.get_end(), UP, buff=0.1)
        )

        # Pinned readout panel: one DecimalNumber per quantity, updated in
        # place from sim_state. Never rebuild MathTex every frame.
        x_number = DecimalNumber(
            sim_state["x"], num_decimal_places=2,
            mob_class=Text, color=TEAL, font_size=26
        )
        v_number = DecimalNumber(
            sim_state["v"], num_decimal_places=2,
            mob_class=Text, color=BLUE_C, font_size=26
        )
        f_number = DecimalNumber(
            spring_force(), num_decimal_places=2,
            mob_class=Text, color=YELLOW, font_size=26
        )
        readout_panel = VGroup(
            VGroup(MathTex(r"x =", color=TEAL), x_number).arrange(RIGHT, buff=0.12),
            VGroup(MathTex(r"v =", color=BLUE_C), v_number).arrange(RIGHT, buff=0.12),
            VGroup(MathTex(r"F =", color=YELLOW), f_number).arrange(RIGHT, buff=0.12),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_corner(UL).shift(DOWN * 0.8)

        x_number.add_updater(lambda mob: mob.set_value(sim_state["x"]))
        v_number.add_updater(lambda mob: mob.set_value(sim_state["v"]))
        f_number.add_updater(lambda mob: mob.set_value(spring_force()))

        self.play(
            Create(spring_line), Create(mass_dot),
            Create(force_arrow), Write(force_label),
            Write(readout_panel),
            run_time=1.5
        )
        self.wait(0.5)

        # Cue c3 -- narration: "Force changes velocity; velocity moves the mass."
        # Visible: same objects, now live; arrow flips sign at each extreme.
        # Change: F -> v -> x evolve together; watch x/v/F agree each frame.
        def step_oscillator(mob, dt):
            # Clamp the frame step so the explicit integration stays stable.
            dt = min(dt, 0.04)
            accel = spring_force() / mass
            sim_state["v"] += accel * dt
            sim_state["x"] += sim_state["v"] * dt
            mob.move_to(axes.c2p(sim_state["x"], 0))

        mass_dot.add_updater(step_oscillator)
        self.wait(5.0)  # Narrated form: player.play("c3") waits the cue out.

        # Cue c4 -- narration: "Friction shrank the swing; what if damping were zero?"
        # Visible: frozen state, decay note; updaters detached.
        # Change: motion stops cleanly; learner predicts the undamped case.
        mass_dot.clear_updaters()
        x_number.clear_updaters()
        v_number.clear_updaters()
        f_number.clear_updaters()
        force_label.clear_updaters()

        decay_note = Text(
            "Amplitude decayed: damping removed energy.",
            font_size=22,
            color=GREY_B
        ).to_edge(DOWN, buff=0.9)
        self.play(Write(decay_note), run_time=1.0)
        self.wait(1.5)
