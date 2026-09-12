# Pedagogical Screenplay & Storyboard Architecture

Every high-quality Manim animation starts with a structured storyboard. Animations
created without an explicit screenplay suffer from pacing mismatch, visual
clutter, and cognitive overload. The storyboard is also the handoff between GNOS
teaching context and the renderer: name the subject, concept, lead teacher,
course notation, learner target, and relevant prerequisite assumption in its
notes or an adjacent design record. Never infer a learner identity.

The artifact should answer one question: what can the learner do or explain
after seeing this change? A visual is evidence for that outcome, not evidence
that the learner mastered it. Leave a small prediction, explanation, or changed
case check for the teacher to use after the render.

---

## 1. The 4-Element Scene Specification

Define each scene using four synchronized pillars:

| Pillar | Definition | Purpose |
| :--- | :--- | :--- |
| **Concept Target** | Single core insight (e.g., "The derivative is the limit of secant slopes") | Prevents split attention |
| **Spoken Script** | Exact words spoken by the narrator | Drives the timeline |
| **Visual Choreography** | Precise list of Mobjects, transforms, and highlights | Mirrors spoken concepts |
| **Sync Cues** | Exact timestamp or word boundary triggering an animation | Eliminates dead air & rushed cuts |

---

## 2. Cognitive Load Constraints for STEM Animations

Adhere to cognitive psychology principles (Sweller et al.):
1. **Modality Principle**: Spoken explanation + animated visual is superior to on-screen written text + animated visual. Avoid displaying paragraphs of text; show only mathematical symbols, diagrams, and labels.
2. **Temporal Contiguity**: Start the visual action when the narration identifies
   the relevant object or change. A short lead-in can establish context, but do
   not animate an unexplained result several seconds early.
3. **Signaling (Cueing)**: When mentioning a term or variable, highlight the corresponding visual element (e.g. `Indicate(obj)` or `Circumscribe(obj)`).
4. **Segmenting**: Break complex derivations into scenes under 45 seconds each.

---

## 3. Storyboard JSON Format

Store screenplays in `storyboard.json` so the voice tool can generate clips and a
manifest. The scene consumes that manifest through `CuePlayer.play(cue_id, ...)`;
it does not guess timing from punctuation. A cue's authored `duration` is for a
silent preview; measured audio duration is authoritative when audio exists.

```json
{
  "title": "Derivative as Tangent Slope",
  "aspect_ratio": "16:9",
  "scenes": [
    {
      "id": "scene_1",
      "title": "Secant to Tangent Intuition",
      "concept_target": "Relate the secant slope to the derivative at one point",
      "narration_cues": [
        {
          "cue_id": "c1",
          "text": "To find the instantaneous rate of change at a point, we start with an approximation.",
          "sync_target": "draw_curve_and_secant"
        },
        {
          "cue_id": "c2",
          "text": "By picking a second nearby point, we draw a secant line connecting them.",
          "sync_target": "add_second_point_and_line"
        },
        {
          "cue_id": "c3",
          "text": "As delta x shrinks to zero, the secant line morphs directly into the tangent line.",
          "sync_target": "animate_delta_x_limit"
        }
      ]
    }
  ]
}
```

---

## 4. Narration Pacing Guidelines

- **Speaking Rate**: Aim for 130–150 words per minute. Math explainers require slower pacing than conversational podcasts to allow working memory processing.
- **Micro-Pauses**: Add 0.5s to 1.0s of silence (`self.wait(0.5)`) after complex visual transformations to let the viewer inspect the resulting state before continuing narration.
- **No Filler**: Avoid setup phrases that consume a cue without advancing the
  learner's question. Begin with the phenomenon, paradox, or central question.

## 5. Review before rendering

Check each cue against four columns: spoken claim, visible object, state change,
and learner inference. Verify the mathematical or physical invariant before
rendering. Afterward inspect the opening, each transition, and the final state
at playback size; compare the artifact with the success check rather than with a
cinematic style target. If a still frame communicates the claim, remove motion.
