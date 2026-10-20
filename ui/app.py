"""Streamlit shell. Thin presentation only: it calls the API, no business logic."""

import streamlit as st

from meshvera.client import fetch_health
from meshvera.config import ConfigError, load_settings

st.set_page_config(page_title="MeshVera", page_icon=None)
st.title("MeshVera")
st.caption("Decentralized-learning simulator and AI experiment copilot — foundation shell (F00)")

try:
    settings = load_settings()
except ConfigError as exc:
    st.error(str(exc))
    st.stop()

st.write(f"API origin: `{settings.api_origin}` · AI mode: **{settings.llm_mode}**")

result = fetch_health(settings.api_origin)
if result["ok"]:
    st.success("API reachable")
    st.json(result["data"])
else:
    st.warning(
        "API not reachable. Start it with `python -m meshvera.api` "
        f"({result['error']})"
    )

st.info("Experiments, simulation and AI planning arrive in later features.")
