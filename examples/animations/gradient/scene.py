"""A narrated or silent example, using the same cue-driven scene in both modes."""
from pathlib import Path
import os
import sys
from manim import *

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/manim-voice-animation-skill/scripts'))
from cue_player import CuePlayer
from render_pipeline import resolve_ffmpeg_exe

# Pydub must use a working binary if this host's system FFmpeg is broken.
from pydub import AudioSegment
AudioSegment.converter=resolve_ffmpeg_exe()


class GradientStep(Scene):
    def construct(self):
        self.camera.background_color='#101c27'
        manifest=Path(os.environ.get('GNOS_MANIFEST',ROOT/'output/gradient/audio/timing_manifest.json'))
        player=CuePlayer(self,manifest,'GradientStep')
        title=Text('Why subtract the slope?',font_size=32).to_edge(UP,buff=.35)
        axes=Axes(x_range=[-1,3,1],y_range=[0,9,1],x_length=7,y_length=4.5,
                  tips=False,axis_config={'color':GREY_B}).shift(LEFT*1.8+DOWN*.25)
        curve=axes.plot(lambda x:x*x,x_range=[-1,3],color=TEAL_C)
        label=Text('f(x) = x²',font_size=24,color=TEAL_C).next_to(axes,UP,buff=.1)
        tracker=ValueTracker(2)
        dot=Dot(axes.c2p(2,4),color=YELLOW)
        dot.add_updater(lambda m:m.move_to(axes.c2p(tracker.get_value(),tracker.get_value()**2)))
        loss=DecimalNumber(4,num_decimal_places=2,font_size=32,color=YELLOW)
        loss.add_updater(lambda m:m.set_value(tracker.get_value()**2))
        loss_label=Text('loss',font_size=24).move_to(RIGHT*4+UP*1.3)
        loss.next_to(loss_label,DOWN)
        self.add(title)
        player.play('start',Create(axes),Create(curve),FadeIn(dot),FadeIn(label),FadeIn(loss_label),FadeIn(loss))
        tangent=Line(axes.c2p(1.3,1.2),axes.c2p(2.7,6.8),color=ORANGE)
        slope=Text('slope = 4',font_size=24,color=ORANGE).move_to(RIGHT*4+DOWN*.3)
        player.play('slope',Create(tangent),FadeIn(slope))
        update=Text('2 − 0.2 × 4 = 1.2',font_size=25).to_edge(DOWN,buff=.35)
        player.play('step',tracker.animate.set_value(1.2),FadeIn(update),FadeOut(tangent),run_time=2)
        prompt=Text('What if η = 1.2?',font_size=24,color=TEAL_C).move_to(RIGHT*4+DOWN*1.3)
        player.play('limit',FadeIn(prompt),run_time=1)
        dot.clear_updaters();loss.clear_updaters()
        player.finish(os.environ.get('GNOS_TIMELINE_PREFIX',str(ROOT/'output/gradient/lesson')))
