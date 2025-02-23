from manim import *
from manimpango import register_font

class RollingNumberAnimationVertical(Scene):
    def construct(self):

        register_font("/home/sunshine/repos/svoboda/fonts/Russo_One/RussoOne-Regular.ttf")
        font_name = "Russo One"
        start_number = 1085
        target_number = 1095

        # Convert numbers to zero-padded strings
        start_str = str(start_number)
        target_str = str(target_number)
        max_digits = max(len(start_str), len(target_str))
        start_str_padded = start_str.zfill(max_digits)
        target_str_padded = target_str.zfill(max_digits)

        # Create individual digit mobjects
        digits = [Text(d, font=font_name, font_size=96) for d in start_str_padded]

        # Hide leading zeros
        leading_zeros = len(start_str_padded) - len(start_str_padded.lstrip('0'))
        leading_zero_indices = list(range(leading_zeros))
        for i in leading_zero_indices:
            if start_str_padded[i] == "0":
                digits[i].set_opacity(0)

        # Arrange the digits horizontally with shared bottom edge
        number_group = VGroup(*digits).arrange(RIGHT, aligned_edge=DOWN, buff=0.05)

        # Create the label with the SAME font size as digits
        label = Text("Дней СВО", font=font_name, font_size=96)

        # Combine number_group + label side by side, but still with a bottom alignment
        # so that bounding boxes are aligned on the bottom
        combined_group = VGroup(number_group, label).arrange(RIGHT, buff=0.3, aligned_edge=DOWN)

        # --- Manual shift of the label to compensate for the glyph "Д" going below baseline ---
        # Try values like 0.1, 0.2, etc., until the bottom lines up visually with the digits.
        label_shift = 0.2
        label.shift(DOWN * label_shift)

        # Optionally center or move them to your desired location
        combined_group.move_to(ORIGIN)

        self.add(combined_group)

        current_str = start_str_padded

        def animate_digit_change(i, old_digit, new_char):
            pos = old_digit.get_center()
            offset = old_digit.height  # vertical distance to roll
            new_digit = Text(new_char, font=font_name, font_size=96).move_to(pos - offset * UP)
            new_digit.set_opacity(0)
            self.add(new_digit)
            anim_old = old_digit.animate.shift(UP * offset).set_opacity(0.5)
            anim_new = new_digit.animate.shift(UP * offset).set_opacity(1)
            return new_digit, [anim_old, anim_new]

        # Roll from start_number+1 to target_number
        for num in range(start_number + 1, target_number + 1):
            next_str = str(num).zfill(max_digits)
            animations = []
            new_digit_refs = {}
            for i in range(max_digits):
                if current_str[i] != next_str[i]:
                    # Skip leading zeros if they remain "0"
                    if i in leading_zero_indices and next_str[i] == "0":
                        continue

                    new_digit, anims = animate_digit_change(i, digits[i], next_str[i])
                    animations.extend(anims)
                    new_digit_refs[i] = new_digit

            if animations:
                self.play(*animations, run_time=0.1)
                # Replace updated digits
                for i, nd in new_digit_refs.items():
                    self.remove(digits[i])
                    digits[i] = nd
            else:
                self.wait(0.3)

            current_str = next_str

        self.wait(2)

if __name__ == "__main__":
    scene = RollingNumberAnimationVertical()
    scene.render()
