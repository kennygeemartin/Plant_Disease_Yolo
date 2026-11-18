import cv2
import numpy as np
from fastapi.testclient import TestClient
from app.main import create_app,preprocess

def fake_predict(image):
    return [{"class":"TEST_ONLY_NOT_A_DIAGNOSIS","confidence":0.5,"xyxy":[10,10,40,40]}]

def fake_mail(email,payload):
    assert email=="test@example.org"
    return "mock_smtp_accepted_not_delivered"

def image_bytes():
    a=np.full((64,64,3),160,np.uint8)
    cv2.rectangle(a,(10,10),(40,40),(0,100,250),-1)
    return cv2.imencode(".png",a)[1].tobytes()

def test_four_input_methods():
    a=cv2.imdecode(np.frombuffer(image_bytes(),np.uint8),1)
    for method in ("baseline","dehaze","equalize","combined"):
        b=preprocess(a,method)
        assert b.shape==a.shape and b.dtype==np.uint8

def test_mocked_upload_preprocess_inference_mail():
    client=TestClient(create_app(predictor=fake_predict,mailer=fake_mail))
    assert client.get("/health").json()["disease_model_loaded"]
    response=client.post("/api/analyze",data={"method":"combined","recipient":"test@example.org"},
        files={"image":("test.png",image_bytes(),"image/png")})
    assert response.status_code==200
    result=response.json()
    assert result["email"]=="mock_smtp_accepted_not_delivered"
    assert result["annotated_image"].startswith("data:image/jpeg;base64,")
    assert result["diagnostically_validated"] is False
    assert "server_preprocessing" in result["timing_ms"]

def test_invalid_image():
    client=TestClient(create_app(predictor=fake_predict))
    assert client.post("/api/analyze",files={"image":("bad.txt",b"notimage","text/plain")}).status_code==422

def test_absent_checkpoint_means_no_predictions(monkeypatch):
    monkeypatch.delenv("MODEL_PATH",raising=False)
    client=TestClient(create_app())
    assert not client.get("/health").json()["disease_model_loaded"]
    assert client.post("/api/analyze",
        files={"image":("test.png",image_bytes(),"image/png")}).status_code==503
