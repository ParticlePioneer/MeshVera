// Preview launcher: starts `python -m meshvera.api` and the Streamlit shell.
// Needs Python >= 3.10 with `pip install -e ".[dev]"` already done.
import { spawn } from "node:child_process";

const py = process.env.PYTHON || "python3";
const uiPort = process.env.PORT || "8501";
const apiPort = process.env.API_PORT || "8000";
const env = {
  ...process.env,
  PYTHONPATH: "src" + (process.env.PYTHONPATH ? ":" + process.env.PYTHONPATH : ""),
  API_PORT: apiPort,
  API_ORIGIN: process.env.API_ORIGIN || `http://127.0.0.1:${apiPort}`,
};

const procs = [
  spawn(py, ["-m", "meshvera.api"], { env, stdio: "inherit" }),
  spawn(
    py,
    ["-m", "streamlit", "run", "ui/app.py", "--server.port", uiPort, "--server.address", "0.0.0.0", "--server.headless", "true"],
    { env, stdio: "inherit" },
  ),
];

for (const p of procs) {
  p.on("error", (e) => {
    console.error(`Could not start Python (${py}): ${e.message}. Install Python 3.10+ and run: pip install -e ".[dev]"`);
    shutdown(1);
  });
  p.on("exit", (code) => {
    if (code) shutdown(code);
  });
}

function shutdown(code) {
  for (const p of procs) p.kill();
  process.exit(code);
}
process.on("SIGINT", () => shutdown(0));
process.on("SIGTERM", () => shutdown(0));
