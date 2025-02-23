from manim import *
from manimpango import register_font
from utils.timeops import main as days_at_war

class RollingNumberAnimationVertical(Scene):
    config.pixel_width = 1080
    config.pixel_height = 1960

    def construct(self):
        register_font("/home/sunshine/repos/svoboda/fonts/Russo_One/RussoOne-Regular.ttf")
        font_name = "Russo One"
        

        # 1) CREATE THE BACKGROUND IMAGE
        #    Replace "background.png" with the path to your own image file.
        bg_image = ImageMobject("static/road1.png")

        # 2) OPTIONAL: Scale the image to fill the frame
        #    By default, the camera is about 8 "Manim units" high, but let's just
        #    match the image to the camera's frame width/height in coordinate space.
        bg_image.set_height(self.camera.frame_height)
        bg_image.set_width(self.camera.frame_width)

        # 3) Move background to the center, add to scene
        bg_image.move_to(ORIGIN)
        self.add(bg_image)
        # If you want to ensure it's behind everything else, you can do:
        
        start_scale = 1.0
        end_scale = 1.15

        total_scene_time = 14.0
        bg_image.current_scale = start_scale
        
        # Define an updater that smoothly goes from 1.0 → 1.1 over total_scene_time seconds
        def bg_zoom_updater(mob, dt):
            # Current scene time in seconds
            t = self.time

            # Fraction of total time (clamped to 1.0 max)
            fraction = min(t / total_scene_time, 1.0)

            # Desired scale from 1.0 up to 1.1
            desired_scale = start_scale + fraction * (end_scale - start_scale)

            # Scale relative to the current scale
            scale_ratio = desired_scale / mob.current_scale
            mob.scale(scale_ratio)

            # Update the custom attribute so we can keep applying incremental scales
            mob.current_scale = desired_scale

        # Attach the updater so it's called every frame
        bg_image.add_updater(bg_zoom_updater)
        
        # === 1) STATIC TEXT (fades in from 0→1 second) ===
        # Create text, place at the top, make invisible initially
        static_text = Text("24-02-2025", font=font_name, font_size=96)
        static_text.set_opacity(0)
        static_text.to_edge(UP, buff=0.5)  # or move_to(...) if you want more precise placement

        # Add to the scene
        self.add(static_text)

        # Fade in over 1 second (from t=0 to t=1)
        self.play(static_text.animate.set_opacity(1), run_time=1)
        # Let it sit alone from second 1→2
        self.wait(1)


        # 1) Get data
        data = days_at_war()  # e.g. {"svo": {"days":1234,"label":"..."}, "donbass": ...}
        target_svo = data["svo"]["days"]
        label_svo = data["svo"]["label"]
        label2_svo = data["svo"]["label_2"]
        target_donbass = data["donbass"]["days"]
        label_donbass = data["donbass"]["label"]
        label2_donbass = data["donbass"]["label_2"]

        # 2) Derive start = target - 7
        delta_days = 7
        start_svo = target_svo - delta_days
        start_donbass = target_donbass - delta_days

        # 3) Create both counters (returns dicts with mobjects + metadata)
        counter_donbass = self.create_rolling_counter(
            start_num=start_donbass,
            target_num=target_donbass,
            label_text=label_donbass,
            font_name=font_name,
            label2_text=label2_donbass
        )
        counter_svo = self.create_rolling_counter(
            start_num=start_svo,
            target_num=target_svo,
            label_text=label_svo,
            font_name=font_name,
            label2_text=label2_svo
        )

        # 4) Arrange them vertically with a larger buff to increase the gap
        both_counters = VGroup(
            counter_donbass["group"],
            counter_svo["group"],
        ).arrange(DOWN, buff=2.5, aligned_edge=DOWN)

        # Optional scaling so they fit nicely on screen
        both_counters.scale(0.8)
        # Compute 75% of the scene's height
        frame_height = self.camera.frame_height
        y_75 = (-frame_height / 2) + 0.4 * frame_height

        # Move group so its center is at y=75%
        both_counters.move_to([0, y_75, 0])

        # Initially set them invisible
        both_counters.set_opacity(0)

        self.add(both_counters)
        
        self.wait(1)

        self.play(both_counters.animate.set_opacity(1), run_time=1)

        # 5) Animate both in parallel so digits roll simultaneously
        self.animate_both_counters(
            counter_donbass,
            counter_svo,
            start_donbass, target_donbass,
            start_svo,     target_svo,
            font_name,
            run_time=0.1
        )

        self.wait(12)


    def create_rolling_counter(
        self,
        start_num: int,
        target_num: int,
        label_text: str,
        label2_text: str,
        font_name: str,
        font_size_digits=96,
        font_size_label=96
    ):
        """
        Creates [digits][label] side-by-side, returns a dict with:
          - "group": the VGroup (digits+label)
          - "digits": list of digit mobjects
          - "current_str": zero-padded start string
          - "leading_zero_indices": which indices are leading zeros
        """
        start_str = str(start_num)
        target_str = str(target_num)
        max_digits = max(len(start_str), len(target_str))
        start_str_padded = start_str.zfill(max_digits)

        # Create each digit
        digits = [
            Text(d, font=font_name, font_size=font_size_digits)
            for d in start_str_padded
        ]

        # Hide leading zeros
        leading_zeros = len(start_str_padded) - len(start_str_padded.lstrip('0'))
        leading_zero_indices = list(range(leading_zeros))
        for i in leading_zero_indices:
            if start_str_padded[i] == "0":
                digits[i].set_opacity(0)

        # Place digits horizontally
        number_group = VGroup(*digits).arrange(RIGHT, aligned_edge=DOWN, buff=0.05)

        # Create label and arrange to the right
        label = Text(label_text, font=font_name, font_size=font_size_label)
        combined_group = VGroup(number_group, label).arrange(
            RIGHT, buff=0.3, aligned_edge=DOWN
        )

        # Small manual shift for letters like "Д"
        label_shift = 0.2
        label.shift(DOWN * label_shift)
        
        label2 = Text(label2_text, font=font_name, font_size=font_size_label)

        combined_group_all = VGroup(combined_group, label2).arrange(
            DOWN, buff=0.6, aligned_edge=DOWN
        )

        return {
            "group": combined_group_all,
            "digits": digits,
            "current_str": start_str_padded,
            "leading_zero_indices": leading_zero_indices,
        }


    def animate_both_counters(
        self,
        counter_donbass,
        counter_svo,
        start_donbass, target_donbass,
        start_svo,     target_svo,
        font_name,
        run_time=0.1
    ):
        """
        Roll both counters simultaneously in a single loop.
        Each iteration we gather animations for Donbass + SVO digits,
        then self.play() them all together.
        """
        digits_donbass = counter_donbass["digits"]
        current_str_donbass = counter_donbass["current_str"]
        zeros_donbass = counter_donbass["leading_zero_indices"]

        digits_svo = counter_svo["digits"]
        current_str_svo = counter_svo["current_str"]
        zeros_svo = counter_svo["leading_zero_indices"]

        # total steps
        diff_donbass = target_donbass - start_donbass
        diff_svo = target_svo - start_svo
        steps = max(diff_donbass, diff_svo)

        max_digits_donbass = len(current_str_donbass)
        max_digits_svo = len(current_str_svo)

        curr_str_donbass_local = current_str_donbass
        curr_str_svo_local = current_str_svo

        # Step from 1..steps so both can animate in parallel
        for step in range(1, steps + 1):
            animations = []

            # 1) Donbass
            if step <= diff_donbass:
                next_val = start_donbass + step
                next_str = str(next_val).zfill(max_digits_donbass)

                for i in range(max_digits_donbass):
                    if curr_str_donbass_local[i] != next_str[i]:
                        # skip if leading zero remains '0'
                        if i in zeros_donbass and next_str[i] == '0':
                            continue

                        new_digit, anims = self.animate_digit_change(
                            digits_donbass[i],
                            next_str[i],
                            font_name
                        )
                        animations.extend(anims)
                        # Remove old digit after the play
                        self.remove(digits_donbass[i])
                        digits_donbass[i] = new_digit

                curr_str_donbass_local = next_str

            # 2) SVO
            if step <= diff_svo:
                next_val_svo = start_svo + step
                next_str_svo = str(next_val_svo).zfill(max_digits_svo)

                for j in range(max_digits_svo):
                    if curr_str_svo_local[j] != next_str_svo[j]:
                        # skip if leading zero remains '0'
                        if j in zeros_svo and next_str_svo[j] == '0':
                            continue

                        new_digit, anims = self.animate_digit_change(
                            digits_svo[j],
                            next_str_svo[j],
                            font_name
                        )
                        animations.extend(anims)
                        self.remove(digits_svo[j])
                        digits_svo[j] = new_digit

                curr_str_svo_local = next_str_svo

            # 3) Play them together so both counters roll simultaneously
            if animations:
                self.play(*animations, run_time=run_time)
            else:
                self.wait(run_time * 0.5)


    def animate_digit_change(self, old_digit: Text, new_char: str, font_name: str):
        """
        Rolls one digit upward, old digit fades out, new digit fades in.
        Returns (new_digit, [anim_old, anim_new]) for simultaneous play.
        """
        pos = old_digit.get_center()
        offset = old_digit.height
        new_digit = Text(new_char, font=font_name, font_size=old_digit.font_size)
        new_digit.move_to(pos - offset * UP)
        new_digit.set_opacity(0)
        self.add(new_digit)

        # old digit fades to 0, new digit to 1
        anim_old = old_digit.animate.shift(UP * offset).set_opacity(0)
        anim_new = new_digit.animate.shift(UP * offset).set_opacity(1)
        return new_digit, [anim_old, anim_new]


if __name__ == "__main__":
    scene = RollingNumberAnimationVertical()
    scene.render()
