from __future__ import annotations

import json
import uuid

import cv2
import numpy as np
from PIL import Image
from sqlalchemy.orm import Session

from app.models.model_manager import ModelManager
from app.cv import preprocessing, contours, features as feat, visualization
from app.db import models
from app.utils import files as file_utils
from app.utils.validation import safe_filename


class NoLeafDetectedError(Exception):
    pass


def pil_to_bgr(image: Image.Image) -> np.ndarray:
    arr = np.array(image.convert("RGB"))
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


def run_full_analysis(
    db: Session,
    image: Image.Image,
    filename: str,
    model_manager: ModelManager,
) -> models.Analysis:

    analysis_id = uuid.uuid4().hex

    original_bgr = pil_to_bgr(image)

    upload_name = safe_filename(filename)

    file_utils.save_upload(
        original_bgr,
        upload_name,
    )

    # ---------------------------------------------------------
    # CLASSICAL PREPROCESSING
    # ---------------------------------------------------------

    stages = preprocessing.preprocess_pipeline(
        original_bgr
    )

    working_image = stages["final"]

    file_utils.save_processed(
        stages["resized"],
        analysis_id,
        "original",
    )

    file_utils.save_processed(
        stages["denoised"],
        analysis_id,
        "denoised",
    )

    file_utils.save_processed(
        stages["enhanced"],
        analysis_id,
        "preprocessed",
    )

    # ---------------------------------------------------------
    # DETECTION
    # IMPORTANT: use ORIGINAL image for YOLO
    # ---------------------------------------------------------

    detection = model_manager.detector.detect(
        original_bgr
    )

    seg = detection["seg"]

    file_utils.save_processed(
        visualization.mask_to_bgr(
            seg["mask"]
        ),
        analysis_id,
        "mask",
    )

    file_utils.save_processed(
        (
            contours.draw_detection_overlay(
                working_image,
                detection["instances"],
            )
            if detection["instances"]
            else working_image
        ),
        analysis_id,
        "detection",
    )

    is_demo_overall = (
        not model_manager.detector.is_trained
    )

    warnings: list[str] = []

    # ---------------------------------------------------------
    # NO LEAF DETECTED
    # ---------------------------------------------------------

    if not detection["instances"]:

        analysis = models.Analysis(
            id=analysis_id,
            image_path=upload_name,
            thumbnail_url=file_utils.upload_url(
                upload_name
            ),
            mode=(
                "demo"
                if is_demo_overall
                else "production"
            ),
            status="no_leaf_detected",
            leaf_count=0,
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return analysis

    # ---------------------------------------------------------
    # CREATE ANALYSIS
    # ---------------------------------------------------------

    analysis = models.Analysis(
        id=analysis_id,
        image_path=upload_name,
        thumbnail_url=file_utils.upload_url(
            upload_name
        ),
        mode=(
            "demo"
            if is_demo_overall
            else "production"
        ),
        status="completed",
        leaf_count=len(
            detection["instances"]
        ),
    )

    db.add(analysis)
    db.flush()

    # ---------------------------------------------------------
    # PROCESS EACH LEAF
    # ---------------------------------------------------------

    for idx, inst in enumerate(
        detection["instances"],
        start=1,
    ):

        inst_mask = inst["mask"]

        # -----------------------------------------------------
        # CONTOUR
        # -----------------------------------------------------

        contour = contours.find_largest_contour(
            inst_mask
        )

        if contour is None:
            continue

        geom = contours.contour_geometry(
            contour
        )

        # -----------------------------------------------------
        # FEATURES
        # -----------------------------------------------------

        shape = feat.shape_features(
            contour,
            geom["hull_area"],
        )

        color = feat.color_features(
            working_image,
            inst_mask,
        )

        texture = feat.texture_features(
            working_image,
            inst_mask,
        )

        # -----------------------------------------------------
        # ORIGINAL PROJECT CROP METHOD
        # -----------------------------------------------------

        crop = visualization.crop_to_bbox(
            working_image,
            inst["bbox"],
        )

        crop_mask = visualization.crop_to_bbox(
            inst_mask,
            inst["bbox"],
        )

        # -----------------------------------------------------
        # ORIGINAL IMAGE FOR GROWTH STAGE
        # -----------------------------------------------------

        growth_crop = visualization.crop_to_bbox(
            original_bgr,
            inst["bbox"],
        )

        # -----------------------------------------------------
        # SPECIES
        # -----------------------------------------------------

        type_pred = (
            model_manager
            .leaf_classifier
            .predict(crop)
        )

        # -----------------------------------------------------
        # HEALTH
        # -----------------------------------------------------

        health_pred = (
            model_manager
            .health_classifier
            .predict(crop)
        )

        # -----------------------------------------------------
        # GROWTH STAGE
        # ONLY Early / Mature
        # -----------------------------------------------------

        stage_pred = (
            model_manager
            .stage_classifier
            .predict(
                growth_crop,
                crop_mask,
            )
        )

        # -----------------------------------------------------
        # SAVE PER-LEAF VIEWS
        # -----------------------------------------------------

        file_utils.save_processed(
            crop,
            analysis_id,
            f"leaf{idx}_crop",
        )

        file_utils.save_processed(
            visualization.mask_to_bgr(
                crop_mask
            ),
            analysis_id,
            f"leaf{idx}_mask",
        )

        contour_view = (
            contours.draw_contour_overlay(
                crop,
                _shift_contour(
                    contour,
                    inst["bbox"],
                ),
                _shift_contour(
                    geom["hull"],
                    inst["bbox"],
                ),
            )
        )

        file_utils.save_processed(
            contour_view,
            analysis_id,
            f"leaf{idx}_contours",
        )

        # -----------------------------------------------------
        # DATABASE RESULT
        # -----------------------------------------------------

        leaf_result = models.LeafResult(
            analysis_id=analysis_id,
            leaf_index=idx,

            detection_confidence=(
                inst["confidence"]
            ),

            bbox_x=inst["bbox"]["x"],
            bbox_y=inst["bbox"]["y"],
            bbox_w=inst["bbox"]["width"],
            bbox_h=inst["bbox"]["height"],

            type_label=(
                type_pred["label"]
                if type_pred
                else None
            ),

            type_confidence=(
                type_pred["confidence"]
                if type_pred
                else None
            ),

            type_is_demo=(
                type_pred is None
            ),

            type_top3_json=(
                json.dumps(
                    type_pred["top3"]
                )
                if type_pred
                else None
            ),

            stage_label=(
                stage_pred["label"]
                if stage_pred
                else None
            ),

            stage_confidence=(
                stage_pred["confidence"]
                if stage_pred
                else 0.0
            ),

            stage_is_demo=(
                stage_pred is None
            ),

            health_label=(
                health_pred["label"]
                if health_pred
                else None
            ),

            health_confidence=(
                health_pred["confidence"]
                if health_pred
                else None
            ),

            health_is_demo=(
                health_pred is None
            ),

            health_top3_json=(
                json.dumps(
                    health_pred.get(
                        "top3",
                        [],
                    )
                )
                if health_pred
                else None
            ),
        )

        db.add(leaf_result)
        db.flush()

        # -----------------------------------------------------
        # FEATURES
        # -----------------------------------------------------

        db.add(
            models.Features(
                leaf_result_id=leaf_result.id,

                area=shape["area"],
                perimeter=shape["perimeter"],
                width=shape["width"],
                height=shape["height"],
                aspect_ratio=shape["aspect_ratio"],
                circularity=shape["circularity"],
                solidity=shape["solidity"],
                extent=shape["extent"],
                convex_hull_area=(
                    shape["convex_hull_area"]
                ),
                equivalent_diameter=(
                    shape["equivalent_diameter"]
                ),

                mean_r=color["rgb"]["r"],
                mean_g=color["rgb"]["g"],
                mean_b=color["rgb"]["b"],

                dominant_color=(
                    color["dominant_color"]
                ),

                texture_contrast=(
                    texture["contrast"]
                ),
                texture_homogeneity=(
                    texture["homogeneity"]
                ),
                texture_energy=(
                    texture["energy"]
                ),
                texture_correlation=(
                    texture["correlation"]
                ),
            )
        )

        # -----------------------------------------------------
        # WARNINGS
        # -----------------------------------------------------

        if (
            type_pred
            and type_pred["confidence"] < 0.55
        ):
            warnings.append(
                f"Leaf {idx}: "
                "low-confidence type prediction."
            )

        if (
            health_pred
            and health_pred["confidence"]
            < model_manager
            .health_classifier
            .confidence_threshold
        ):
            warnings.append(
                f"Leaf {idx}: "
                "low-confidence health prediction."
            )

    # ---------------------------------------------------------
    # COMMIT
    # ---------------------------------------------------------

    db.commit()
    db.refresh(analysis)

    return analysis


def _shift_contour(
    contour,
    bbox,
    padding: int = 8,
):
    shifted = contour.copy()

    shifted[:, 0, 0] -= max(
        0,
        bbox["x"] - padding,
    )

    shifted[:, 0, 1] -= max(
        0,
        bbox["y"] - padding,
    )

    return shifted