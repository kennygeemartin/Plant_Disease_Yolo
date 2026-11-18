# Smartphone-to-server research prototype

This implementation is **not a deployed, clinically or agronomically validated disease diagnosis service**. It provides a responsive phone-browser upload page, the four specified preprocessing paths, optional Ultralytics checkpoint inference, annotated result output and optional SMTP submission. If no `MODEL_PATH` checkpoint exists, `/api/analyze` returns HTTP 503 instead of a fictitious prediction.

Install `python -m pip install -r requirements-prototype-test.txt`; for real model loading additionally install the Ultralytics version required by the verified checkpoint. Run `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` and open `http://127.0.0.1:8000` on the same machine. Execute `python -m pytest -q tests/test_gateway.py` to exercise mocked upload/preprocessing/prediction/SMTP code paths. Tests use deliberately artificial predicted boxes and a fake email transport, so **they provide no evidence of model accuracy, live networking, or email receipt**.

The optional environment variables are `MODEL_PATH`, `SMTP_HOST`, `SMTP_FROM`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and `SMTP_TLS_MODE` (`ssl` or `starttls`). Never commit secrets. `smtp_accepted_not_inbox_verified` does not mean delivered. The timing fields exclude image acquisition, network upload and inbox delivery; they are not end-to-end field latency.

Do not publicly host this prototype without authentication, TLS, rate limiting, privacy controls, model validation, independent crop-disease test images and notification-delivery logging. Committing source to GitHub is **not** a cloud deployment.
