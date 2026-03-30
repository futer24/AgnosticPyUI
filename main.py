"""Main entry point for AgnosticPyUI.

Usage:
    python main.py --ui [gradio|streamlit]
"""

import argparse
import sys

from application.service import TodoService


def main() -> None:
    parser = argparse.ArgumentParser(description="AgnosticPyUI Launcher")
    parser.add_argument(
        "--ui",
        choices=["gradio", "streamlit"],
        default="gradio",
        help="UI framework to use (default: gradio)",
    )
    args = parser.parse_args()

    service = TodoService()

    from ui_core.app_builder import AppBuilder

    builder: AppBuilder

    if args.ui == "gradio":
        from ui_core.gradio_ui import GradioAppBuilder, GradioUIFactory

        factory: GradioUIFactory = GradioUIFactory()
        builder = GradioAppBuilder(service, factory)
        print("Launching Gradio UI...")
        builder.launch()

    elif args.ui == "streamlit":
        from ui_core.streamlit_ui import StreamlitAppBuilder, StreamlitUIFactory

        # For Streamlit, we check if we are already running inside streamlit
        # If not, we instruct the user.
        try:
            import streamlit.web.cli as stcli

            if not hasattr(sys, "_called_from_main"):
                # Re-run logic to handle `python main.py --ui streamlit`
                sys._called_from_main = True  # type: ignore
                sys.argv = ["streamlit", "run", sys.argv[0], "--", "--ui", "streamlit"]
                sys.exit(stcli.main())
        except ImportError:
            print("Error: Streamlit not installed or CLI entry point not found.")
            sys.exit(1)

        factory_st: StreamlitUIFactory = StreamlitUIFactory()
        builder = StreamlitAppBuilder(service, factory_st)
        builder.launch()


if __name__ == "__main__":
    main()
