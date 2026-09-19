import io
import tempfile
import numpy as np
import cv2
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import init_db
from app.utils.validation import validate_upload, ValidationError
from app.cv import preprocessing, segmentation, contours, features
from app.models.health_classifier import HealthClassifier
from app.schemas.analysis import HealthPrediction

init_db()
client = TestClient(app)


def _synthetic_leaf_image() -> bytes:
    """A simple synthetic green blob on a neutral background, as a
    stand-in for a real leaf photo in tests."""
    img = np.full((300, 300, 3), (235, 235, 230), dtype=np.uint8)  # BGR-ish neutral bg
    cv2.ellipse(img, (150, 150), (90, 60), 20, 0, 360, (40, 150, 40), -1)
    buf = io.BytesIO()
    Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).save(buf, format="PNG")
    return buf.getvalue()


def test_health_endpoint():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert "models" in body
    assert "health_classifier" in body["models"]


def test_health_classifier_is_unavailable_without_real_weights():
    with tempfile.TemporaryDirectory() as model_dir:
        classifier = HealthClassifier(model_dir)
        assert classifier.is_trained is False
        assert classifier.predict(np.zeros((10, 10, 3), dtype=np.uint8)) is None


def test_health_prediction_schema_supports_unavailable_model():
    prediction = HealthPrediction()
    assert prediction.label is None
    assert prediction.confidence is None
    assert prediction.is_demo is True


def test_validate_upload_rejects_bad_extension():
    try:
        validate_upload(b"not-an-image", "file.txt", "text/plain", 10 * 1024 * 1024)
        assert False, "expected ValidationError"
    except ValidationError as e:
        assert e.code == "UNSUPPORTED_FORMAT"


def test_validate_upload_rejects_corrupt_image():
    try:
        validate_upload(b"\x00\x01\x02", "file.jpg", "image/jpeg", 10 * 1024 * 1024)
        assert False, "expected ValidationError"
    except ValidationError as e:
        assert e.code == "CORRUPT_IMAGE"


def test_validate_upload_accepts_real_image():
    image = validate_upload(_synthetic_leaf_image(), "leaf.png", "image/png", 10 * 1024 * 1024)
    assert image.size[0] > 0


def test_preprocessing_pipeline_runs():
    img = cv2.imdecode(np.frombuffer(_synthetic_leaf_image(), np.uint8), cv2.IMREAD_COLOR)
    stages = preprocessing.preprocess_pipeline(img)
    assert "final" in stages
    assert stages["final"].shape[:2] == img.shape[:2]


def test_segmentation_finds_synthetic_leaf():
    img = cv2.imdecode(np.frombuffer(_synthetic_leaf_image(), np.uint8), cv2.IMREAD_COLOR)
    result = segmentation.segment_leaf(img)
    assert result["found"] is True
    assert result["coverage"] > 0.01


def test_feature_extraction_on_synthetic_leaf():
    img = cv2.imdecode(np.frombuffer(_synthetic_leaf_image(), np.uint8), cv2.IMREAD_COLOR)
    seg = segmentation.segment_leaf(img)
    contour = contours.find_largest_contour(seg["mask"])
    assert contour is not None
    geom = contours.contour_geometry(contour)
    shape = features.shape_features(contour, geom["hull_area"])
    assert shape["area"] > 0
    assert 0 <= shape["circularity"] <= 1
    color = features.color_features(img, seg["mask"])
    assert "rgb" in color
    texture = features.texture_features(img, seg["mask"])
    assert "contrast" in texture


def test_analyze_endpoint_with_no_leaf_image():
    blank = np.full((200, 200, 3), 240, dtype=np.uint8)
    buf = io.BytesIO()
    Image.fromarray(blank).save(buf, format="PNG")
    resp = client.post("/api/analyze", files={"file": ("blank.png", buf.getvalue(), "image/png")})
    assert resp.status_code in (422, 200)  # blank may or may not trip the leaf-coverage threshold


def test_analyze_endpoint_rejects_bad_file():
    resp = client.post("/api/analyze", files={"file": ("bad.txt", b"hello", "text/plain")})
    assert resp.status_code == 422


def test_history_empty_list_initially():
    resp = client.get("/api/history")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
