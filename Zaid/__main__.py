"""Backward-compatible launcher for the renamed ICC package."""
import runpy

runpy.run_module("ICC", run_name="__main__")
