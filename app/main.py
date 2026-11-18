"""Research prototype. No diagnosis without an independently validated checkpoint."""
import base64
import os
import re
import smtplib
import time
import uuid
from email.message import EmailMessage
from pathlib import Path

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

MAX_UPLOAD_BYTES=10*1024*1024
METHODS=("baseline","dehaze","equalize","combined")
EMAIL_RE=re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

def dark_channel_dehaze(bgr):
    im=bgr.astype(np.float32)/255.0
    kernel=np.ones((15,15),np.uint8)
    dark=cv2.erode(np.min(im,axis=2),kernel)
    n=max(1,int(np.ceil(0.001*dark.size)))
    idx=np.argpartition(dark.ravel(),-n)[-n:]
    A=np.maximum(im.reshape(-1,3)[idx].max(axis=0),1.0/255.0)
    d=cv2.erode(np.min(im/A,axis=2),kernel)
    t=np.maximum(1-0.95*d,0.1)
    return np.uint8(np.clip(((im-A)/t[...,None]+A)*255,0,255))

def equalize_luminance(bgr):
    yuv=cv2.cvtColor(bgr,cv2.COLOR_BGR2YUV)
    yuv[:,:,0]=cv2.equalizeHist(yuv[:,:,0])
    return cv2.cvtColor(yuv,cv2.COLOR_YUV2BGR)

def preprocess(image,method):
    if method not in METHODS:raise ValueError("Unknown preprocessing method")
    out=dark_channel_dehaze(image) if method in ("dehaze","combined") else image.copy()
    return equalize_luminance(out) if method in ("equalize","combined") else out

def actual_predictor():
    name=os.environ.get("MODEL_PATH","")
    if not name or not Path(name).is_file():return None
    from ultralytics import YOLO
    model=YOLO(name)
    def predict(image):
        result=model.predict(image,conf=0.25,imgsz=640,device="cpu",verbose=False)[0]
        return [{"class":str(result.names[int(box.cls.item())]),
                 "confidence":float(box.conf.item()),
                 "xyxy":[float(x) for x in box.xyxy[0].tolist()]}
                for box in result.boxes]
    return predict

def send_mail(recipient,result):
    host=os.environ.get("SMTP_HOST","")
    sender=os.environ.get("SMTP_FROM","")
    if not host or not sender:raise RuntimeError("SMTP not configured")
    msg=EmailMessage()
    msg["From"]=sender
    msg["To"]=recipient
    msg["Subject"]="Plant image analysis (research prototype)"
    msg.set_content("Not a confirmed diagnosis.\nAnalysis ID: "+result["analysis_id"]+
                    "\nPredictions: "+str(result["predictions"]))
    port=int(os.environ.get("SMTP_PORT","465"))
    if os.environ.get("SMTP_TLS_MODE","ssl")=="starttls":
        client=smtplib.SMTP(host,port,timeout=12)
        client.starttls()
    else:client=smtplib.SMTP_SSL(host,port,timeout=12)
    with client:
        if os.environ.get("SMTP_USER"):
            client.login(os.environ["SMTP_USER"],os.environ.get("SMTP_PASSWORD",""))
        client.send_message(msg)
    return "smtp_accepted_not_inbox_verified"

PAGE="""<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Plant image research prototype</title><style>
body{font:16px system-ui;max-width:650px;margin:3rem auto;padding:1rem;color:#184a3a}
main{border:1px solid #ccc;border-radius:12px;padding:20px}label{display:block;margin:15px 0}
input,select,button{font:inherit;padding:8px}button{background:#08775e;color:#fff;border:0;border-radius:5px}
pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><main><h1>Plant image processing</h1>
<p>Research demonstration, not a confirmed disease diagnosis. Model predictions are disabled without a checkpoint.</p>
<form id="f"><label>Image <input name="image" type="file" accept="image/*" capture="environment" required></label>
<label>Preprocessing <select name="method"><option>baseline</option><option>dehaze</option>
<option>equalize</option><option selected>combined</option></select></label>
<label>Optional notification email <input name="recipient" type="email"></label><button>Analyse</button></form>
<pre id="o"></pre><img id="p" style="max-width:100%"></main>
<script>document.querySelector("#f").onsubmit=async e=>{e.preventDefault();const o=document.querySelector("#o");
try{const r=await fetch("/api/analyze",{method:"POST",body:new FormData(e.target)});
const j=await r.json();o.textContent=JSON.stringify({...j,annotated_image:j.annotated_image?"[base64 image omitted]":null},null,2);
document.querySelector("#p").src=j.annotated_image||""}catch(x){o.textContent=String(x)}}</script></html>"""

def create_app(predictor=None,mailer=None):
    app=FastAPI(title="Plant image research prototype",version="0.1")
    predictor=predictor if predictor is not None else actual_predictor()
    mailer=mailer if mailer is not None else send_mail
    @app.get("/",response_class=HTMLResponse)
    def index():return PAGE
    @app.get("/health")
    def health():
        return {"status":"ok","disease_model_loaded":predictor is not None,
                "research_only":True,"field_validated":False,
                "email_transport_configured":bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_FROM"))}
    @app.post("/api/analyze")
    async def analyze(image:UploadFile=File(...),method:str=Form("combined"),recipient:str=Form("")):
        if method not in METHODS:raise HTTPException(422,"Invalid preprocessing method")
        if recipient and not EMAIL_RE.fullmatch(recipient):raise HTTPException(422,"Invalid recipient")
        if predictor is None:raise HTTPException(503,"Validated disease-specific model not configured")
        start=time.perf_counter()
        raw=await image.read(MAX_UPLOAD_BYTES+1)
        if len(raw)>MAX_UPLOAD_BYTES:raise HTTPException(413,"Image exceeds 10MB")
        tick=time.perf_counter()
        bgr=cv2.imdecode(np.frombuffer(raw,dtype=np.uint8),cv2.IMREAD_COLOR)
        if bgr is None:raise HTTPException(422,"Invalid image")
        decode=(time.perf_counter()-tick)*1000
        tick=time.perf_counter()
        out=preprocess(bgr,method)
        prep=(time.perf_counter()-tick)*1000
        tick=time.perf_counter()
        predictions=predictor(out)
        inference=(time.perf_counter()-tick)*1000
        annotated=out.copy()
        for p in predictions:
            x1,y1,x2,y2=map(int,p["xyxy"])
            cv2.rectangle(annotated,(x1,y1),(x2,y2),(0,180,80),2)
            cv2.putText(annotated,f'{p["class"]} {p["confidence"]:.2f}',(max(0,x1),max(15,y1-5)),
                        cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,180,80),1,cv2.LINE_AA)
        ok,jpg=cv2.imencode(".jpg",annotated)
        report={"analysis_id":str(uuid.uuid4()),"method":method,"predictions":predictions,
                "diagnostically_validated":False,"research_only":True,
                "timing_ms":{"server_decode":round(decode,2),"server_preprocessing":round(prep,2),
                             "model_inference":round(inference,2)},
                "timing_exclusions":["phone_capture","network_upload","recipient_inbox_delivery"]}
        report["annotated_image"]="data:image/jpeg;base64,"+base64.b64encode(jpg).decode() if ok else None
        if recipient:
            tick=time.perf_counter()
            try:report["email"]=mailer(recipient,report)
            except Exception:report["email"]="submission_failed"
            report["timing_ms"]["smtp_submitting"]=round((time.perf_counter()-tick)*1000,2)
        else:report["email"]="not_requested"
        report["timing_ms"]["server_handler_total"]=round((time.perf_counter()-start)*1000,2)
        return report
    return app
app=create_app()
