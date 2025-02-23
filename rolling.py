from manim import *
from manimpango import register_font
from utils.timeops import main as days_at_war


class RollingNumberAnimationVertical(Scene):
    def construct(self):

        register_font("/home/sunshine/repos/svoboda/fonts/Russo_One/RussoOne-Regular.ttf")
        font_name = "Russo One"
        
        data = days_at_war()
        
        target_svo = data["svo"]["days"]
        target_donbass = data["donbass"]["days"]
        start_svo = target_svo - 7
        start_donbass = target_donbass - 7

        # --- Create the FIRST counter (Days SVO) ---
        group_svo = self.create_rolling_counter(
            start_num=start_svo,
            target_num=target_svo,
            label_text=data["svo"]["label"],
            font_name=font_name
        )

        # --- Create the SECOND counter (Days War in Donbass) ---
        group_donbass = self.create_rolling_counter(
            start_num=start_donbass,
            target_num=target_donbass,
            label_text=data["donbass"]["label"],
            font_name=font_name
        )

        # Arrange them VERTICALLY with a small gap
        both_counters = VGroup(
            group_donbass["group"],   # VGroup from the second counter
            group_svo["group"],      # VGroup from the first counter
        ).arrange(DOWN, buff=1.0, aligned_edge=LEFT)
        both_counters.scale(0.5)       # shrink them a bit

        # Move them to center
        both_counters.move_to(ORIGIN)
        self.add(both_counters)

        # Animate the FIRST counter

        self.animate_rolling(
            group_donbass["digits"],
            group_donbass["current_str"],
            group_donbass["leading_zero_indices"],
            start_donbass,
            target_donbass,
            font_name,
            run_time=0.1
        )

        self.wait(0.1)

        # Animate the SECOND counter
        self.animate_rolling(
            group_svo["digits"],
            group_svo["current_str"],
            group_svo["leading_zero_indices"],
            start_svo,
            target_svo,
            font_name,
            run_time=0.1
        )

        self.wait(2)

    # ------------------------------------------------------------------
    def create_rolling_counter(
        self,
        start_num: int,
        target_num: int,
        label_text: str,
        font_name: str,
        font_size_digits=96,
        font_size_label=96
    ):
        """
        Creates a horizontal group: [digits][label]
        Returns a dict with keys:
          - "group" (VGroup of digits+label),
          - "digits" (list of digit mobjects),
          - "current_str" (zero-padded start string),
          - "leading_zero_indices" (list of leading zeros).
        """
        # Convert to strings and zero-pad
        start_str = str(start_num)
        target_str = str(target_num)
        max_digits = max(len(start_str), len(target_str))
        start_str_padded = start_str.zfill(max_digits)

        # Create digit mobjects
        digits = [
            Text(d, font=font_name, font_size=font_size_digits)
            for d in start_str_padded
        ]

        # Hide leading zeros initially
        leading_zeros = len(start_str_padded) - len(start_str_padded.lstrip("0"))
        leading_zero_indices = list(range(leading_zeros))
        for i in leading_zero_indices:
            if start_str_padded[i] == "0":
                digits[i].set_opacity(0)

        # Arrange digits horizontally
        number_group = VGroup(*digits).arrange(
            RIGHT, aligned_edge=DOWN, buff=0.05
        )

        # Create label
        label = Text(label_text, font=font_name, font_size=font_size_label)

        # Put them side by side
        combined_group = VGroup(number_group, label).arrange(
            RIGHT, buff=0.3, aligned_edge=DOWN
        )

        # Manual shift for the letter "Д"
        label_shift = 0.2
        label.shift(DOWN * label_shift)

        # Return group plus metadata so we can animate later
        return {
            "group": combined_group,
            "digits": digits,
            "current_str": start_str_padded,
            "leading_zero_indices": leading_zero_indices,
        }

    # ------------------------------------------------------------------
    def animate_rolling(
        self,
        digits: list,
        current_str: str,
        leading_zero_indices: list,
        start: int,
        end: int,
        font_name: str,
        run_time=0.1
    ):
        """
        Animate vertical rolling of digits from (start+1) up to end.
        """
        max_digits = len(current_str)

        def animate_digit_change(old_digit, new_char):
            pos = old_digit.get_center()
            offset = old_digit.height
            new_digit = Text(
                new_char, font=font_name, font_size=old_digit.font_size
            ).move_to(pos - offset * UP)
            new_digit.set_opacity(0)
            self.add(new_digit)

            anim_old = old_digit.animate.shift(UP * offset).set_opacity(0.5)
            anim_new = new_digit.animate.shift(UP * offset).set_opacity(1)
            return new_digit, [anim_old, anim_new]

        current_str_local = current_str

        for num in range(start + 1, end + 1):
            next_str = str(num).zfill(max_digits)
            animations = []
            new_digit_refs = {}

            for i in range(max_digits):
                if current_str_local[i] != next_str[i]:
                    # Skip anim if leading zero remains "0"
                    if i in leading_zero_indices and next_str[i] == "0":
                        continue

                    new_digit, anims = animate_digit_change(digits[i], next_str[i])
                    animations.extend(anims)
                    new_digit_refs[i] = new_digit

            if animations:
                self.play(*animations, run_time=run_time)
                # Update references
                for i, nd in new_digit_refs.items():
                    self.remove(digits[i])
                    digits[i] = nd
            else:
                self.wait(run_time * 0.5)

            current_str_local = next_str

if __name__ == "__main__":
    scene = RollingNumberAnimationVertical()
    scene.render()
