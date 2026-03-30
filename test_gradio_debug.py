import gradio as gr

try:
    print("Testing gr.Markdown positional...")
    m1 = gr.Markdown("# Test")
    print("m1 created")
    
    print("Testing gr.Markdown with label (should fail if that's the issue)...")
    try:
        m2 = gr.Markdown(value="# Test", label="My Label")
        print("m2 created with label")
    except TypeError as e:
        print(f"m2 failed as expected: {e}")

    print("Testing GradioHeader-like call...")
    label = "Header"
    level = 1
    m3 = gr.Markdown(f"{'#' * level} {label}")
    print("m3 created")

except Exception as e:
    print(f"Caught Exception: {type(e).__name__}: {e}")
