from easing_functions import LinearInOut, SineEaseInOut, QuadEaseOut


def make_ease(ease_type: str, start, end, duration):
    if ease_type == "linear":
        return LinearInOut(start, end, duration)
    elif ease_type == "sineinout":
        return SineEaseInOut(start, end, duration)
    elif ease_type == "quadout":
        return QuadEaseOut(start, end, duration)
    else:
        return LinearInOut(start, end, duration)  # fallback
